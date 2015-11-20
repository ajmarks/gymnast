"""
Font objects
"""

import six
import struct
from bidict    import collapsingbidict

from ..pdf_element    import PdfElement
from ...pdf_constants import BASE_ENCODINGS, GLYPH_LIST
from ...pdf_matrix    import PdfMatrix
from ...pdf_types     import PdfLiteralString, PdfDict, PdfNull, PdfName
from ...exc           import PdfError

class PdfBaseFont(PdfElement):
    """Base PDF Font.  Right now this is exclusively Type 1."""

    def __init__(self, obj, obj_key=None):
        super(PdfBaseFont, self).__init__(obj, obj_key)
        self._encoding  = None
        self._codec     = None
        self._avg_width = None

    def text_space_coords(self, x, y):
        """Convert a vector in glyph space to text space"""
        raise NotImplementedError

    @property
    def Encoding(self):
        """The font's parsed Encoding object.
        Returns a null encoding if the attribute is missing."""
        if self._encoding:
            return self._encoding
        try:
            obj = self._object['Encoding'].parsed_object
        except KeyError:
            self._encoding = FontEncoding(PdfDict({}))
        else:
            if isinstance(obj, FontEncoding):
                self._encoding = obj
            else:
                self._encoding = FontEncoding.from_name(obj)
        return self._encoding
    @property
    def codec(self):
        """codecs.Codec object based on the font's Endcoding"""
        if not self._codec:
            self._codec = self._get_codec()
        return self._codec

    def to_text(self, string):
        """Convert the string to a unicode representation based on the font's
        encoding."""
        self.codec.decode(string.encode('utf-16-be'))
    def decode_char(self, char):
        """Translate a string based on the font's encoding.  This is kind of
        twisted, so here's the basic explanation for Latin1 fonts:

        1. First, try to use the font's ToUnicode CMap (not yet implemented)
        2. If there's no ToUnicode, use the font's Encoding:
           a. Use the Encoding (including the Differences array, if defined)
              to map the character code to a name.
           b. Look up that name's UTF-16 value in the Adobe Glyph List

        TODO: CMap"""
        val = char.encode('utf-16-be')
        intval = struct.unpack(">Q", b'\x00'*(8-len(val))+val)[0]
        try:
            return GLYPH_LIST[self.get_glyph_name(intval)]
        except KeyError:
            return char

    def decode_string(self, string):
        """Convenience method to translate a string one character at a time."""
        return ''.join(self.decode_char(c) for c in string)

    def get_glyph_width(self, glyph, missing_width=0):
        """Return the width of the specified glyph in the current font.
        Note that these widths are in _glyph_ space, not _text_ space.

        Arguments:
            glyph - a one character string"""
        if not isinstance(glyph, int):
            glyph = self.Encoding.get_char_code(GLYPH_LIST[:glyph])
        if not (self.FirstChar <= glyph <= self.LastChar):
            return self.FontDescriptor.get('MissingWidth', missing_width)
        return self.Widths[glyph - self.FirstChar]

    def get_glyph_name(self, code):
        return self.Encoding.get_glyph_name(code)

    def get_char_code(self, name):
        return self.Encoding.get_char_code(name)

    @property
    def space_width(self):
        """Width of the space character in the current font"""
        return self.get_glyph_width(self.get_char_code('space'))
    @property
    def avg_width(self):
        """Approximate average character width.  Currently only defined for
        latin fonts."""
        if self._avg_width is None:
            capwidths = [i for i in (self.get_glyph_width(i, None)
                                     for i in range(ord('A'), ord('Z')+1)) if i]
            lowwidths = [i for i in (self.get_glyph_width(i, None)
                                     for i in range(ord('a'), ord('z')+1)) if i]
            try:
                self._avg_width = float(4*sum(lowwidths)+sum(capwidths)) \
                                 /(4*len(lowwidths)+len(capwidths))
            except ZeroDivisionError:
                self._avg_width = float(sum(self.Widths))/len(self.Widths)
        return self._avg_width

class FontDescriptor(PdfElement):
    """FontDescriptior object describefd in Table 5.19 on p. 456.
    Note that this will need to be overloaded to properly handle Type3 fonts."""
    def __init__(self, obj, obj_key=None):
        super(FontDescriptor, self).__init__(obj, obj_key)
        self._charset = False

    @property
    def CharSet(self):
        """Returns the CharSet property as a list of PdfNames instead of one
        long string"""
        if self._charset is False: # We need None
            chars = self._object.value.get('CharSet')
            if isinstance(chars, bytes):
                self._charset = [PdfName.from_token(char)
                                 for char in chars.split(b'/')[1:]]
            elif isinstance(chars, PdfLiteralString):
                self._charset = [PdfName.from_token(char)
                                 for char in chars.split('/')[1:]]
            elif chars is None or chars is PdfNull:
                self._charset = chars
            else:
                raise PdfError('Invalid charset')
        return self._charset

class FontEncoding(PdfElement):
    """Font encoding object as described in Appendix D"""
    #This should never change ever, but why hardcode in two places?
    VALID_ENCODINGS = set(six.next(iter(BASE_ENCODINGS.values())).keys())

    def __init__(self, obj, obj_key=None):
        super(FontEncoding, self).__init__(obj, obj_key)
        base_encoding = obj.value.get('BaseEncoding', 'StandardEncoding')
        if base_encoding not in self.VALID_ENCODINGS:
            raise ValueError('Invalid BaseEncoding')

        #Base glyph map for the specified encoding
        self._glyphmap = collapsingbidict({k: v[base_encoding]
                                           for k,v in six.iteritems(BASE_ENCODINGS)})
        # Now modify it with the differences array, if specified
        diffs = obj.value.get('Differences', [])
        # Flatten if we need to (though we shouldn't need to)
        if diffs and isinstance(diffs[0], list):
            diffs = sum(diffs, [])
        differences = {}
        # A diffs array is a series of numbers followed by one or more glyph
        # names and remaps the characters table such that the nth glyph name
        # has character code equal to that number + (n-1).  Wash, rinse,
        # and repeat.
        for d in diffs:
            if isinstance(d, int):
                n = d
            else: # d is a glyph name
                differences[d] = n
                n += 1
        self._glyphmap.update(differences)
        self._differences = differences
        self._fontmatrix  = PdfMatrix(.001, 0, 0, .001, 0, 0)
    @property
    def BaseEncoding(self):
        return self._object.get('BaseEncoding', 'StandardEncoding')
    @property
    def Differences(self):
        return self._differences
    @property
    def GlyphMap(self):
        """bidict on pairs (glyph, character code)"""
        return self._glyphmap
    def get_glyph_name(self, code):
        return self._glyphmap[:code]
    def get_char_code(self, name):
        try:
            return self._glyphmap[name]
        except KeyError:
            print('Ruh Roh!')
    @classmethod
    def from_name(cls, encoding_name):
        """Return an FontEncoding object when given a name"""
        return cls(PdfDict({'BaseEncoding': encoding_name}))
