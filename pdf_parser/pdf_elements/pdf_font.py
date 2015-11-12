from bidict import collapsingbidict
import codecs

from .pdf_element    import PdfElement
from ..pdf_constants import BASE_ENCODINGS, GLYPH_LIST
from ..pdf_parser    import PdfParser
from ..pdf_types     import PdfLiteralString, PdfDict
from ..exc           import *

#PTVS nonsense
from builtins import *

class FontDescriptor(PdfElement):
    """FontDescriptior object describefd in Table 5.19 on p. 456.
    Note that this will need to be overloaded to properly handle Type3 fonts."""
    def __init__(self, obj, obj_key=None):
        super().__init__(obj, obj_key)
        self._charset = False

    @property
    def CharSet(self):
        if self._charset is False: # We need None
            chars = self._object.value.get('CharSet')
            if isinstance(chars, (bytes, PdfLiteralString)):
                self._charset = PdfParser().parse(chars, False)
            elif chars is None:
                self._charset = chars
            else:
                raise PdfError('Invalid charset')
        return self._charset

class FontEncoding(PdfElement):
    """Font encoding object as described in Appendix D"""

    #This should never change ever, but why hardcode in two places?
    VALID_ENCODINGS = set(next(iter(BASE_ENCODINGS.values())).keys())

    def __init__(self, obj, obj_key=None):
        super().__init__(obj, obj_key)
        base_encoding = obj.value.get('BaseEncoding', 'StandardEncoding')
        if base_encoding not in self.VALID_ENCODINGS:
            raise ValueError('Invalid BaseEncoding')
        
        #Base glyph map for the specified encoding
        self._glyphmap = collapsingbidict({k: v[base_encoding]
                                           for k,v in BASE_ENCODINGS.items()})
        # Now modify it with the differences array, if specified
        diffs = obj.value.get('Differences', [])
        if not isinstance(diffs, (list, tuple)):
            raise ValueError('Invalid differences array')
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
        return self._glyphmap[name]
    @classmethod
    def from_name(cls, encoding_name):
        """Return an FontEncoding object when given a name"""
        return cls(PdfDict({'Encoding': encoding_name}))

class PdfFont(PdfElement):
    #Type hints
    if False:
        codec = codecs.Codec()

    def __init__(self, obj, obj_key=None):
        super().__init__(obj, obj_key)
        self._encoding = None
        self._codec    = None

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
        try:
            return GLYPH_LIST[self.get_glyph_name(int.from_bytes(val, 'big'))]
        except KeyError:
            return char
    def decode_string(self, string):
        """Convenience method to translate a string one character at a time."""
        return ''.join(self.decode_char(c) for c in string)

    def get_glyph_width(self, glyph):
        """Return the width of the specified glyph in the current font.

        Arguments:
            glyph - a one character string"""
        if not isinstance(glyph, int):
            glyph = self.Encoding.get_char_code(GLYPH_LIST[:glyph])
        if glyph > self.LastChar or glyph < self.FirstChar:
            return self.FontDescriptor.get('MissingWidth', 0)
        return self.Widths[glyph - self.FirstChar]

    def get_glyph_name(self, code):
        return self.Encoding.get_glyph_name(code)
    def get_char_code(self, name):
        return self.Encoding.get_char_code(name)

    @property
    def space_width(self):
        """Width of the space character in the current font"""
        return self.get_glyph_width(self.get_char_code('space'))