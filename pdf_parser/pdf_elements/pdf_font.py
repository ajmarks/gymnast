"""
Font objects
"""

import codecs
import os
import six
from bidict import collapsingbidict

from .pdf_element    import PdfElement
from ..pdf_constants import BASE_ENCODINGS, GLYPH_LIST, DATA_DIR
from ..pdf_matrix    import PdfMatrix
from ..pdf_parser    import PdfParser
from ..pdf_types     import PdfLiteralString, PdfDict, PdfName
from ..exc           import *

AFM_DIR   = DATA_DIR + '/afm/'
STD_FONTS = set([i[:-4] for i in os.listdir(AFM_DIR) if i[-4:] == '.afm'])

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
                self._charset = PdfParser().parse_list(chars)
            elif isinstance(chars, PdfLiteralString):
                self._charset = PdfParser().parse_list(chars._raw_bytes)
            elif chars is None:
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
        return self._glyphmap[name]
    @classmethod
    def from_name(cls, encoding_name):
        """Return an FontEncoding object when given a name"""
        return cls(PdfDict({'Encoding': encoding_name}))

class PdfFont(PdfElement):
    """Base PDF Font.  Right now this is exclusively Type 1."""
    #Type hints
    if False:
        codec = codecs.Codec()

    def __init__(self, obj, obj_key=None):
        super(PdfFont, self).__init__(obj, obj_key)
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
        Note that these widths are in _glyph_ space, not _text_ space.  For
        Type 1 fonts, the conversion is generally to divide by 1000.  For
        Type 3 fonts though, it's more complex.

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
    def FontMatrix(self):
        """Transformation matrix to go from glyph space to text space.
        Using this instead of just division by 1000 will make things easier
        when we add support for Type 3 fonts"""
        return self._fontmatrix
    @property
    def space_width(self):
        """Width of the space character in the current font"""
        return self.get_glyph_width(self.get_char_code('space'))

    @classmethod
    def load_standard_font(cls, font_name):
        """Super, super crude method to parse a afm font file into a Type1
        PdfFont object

        TODO: Make this not disgustingly, eye gougingly awful"""
        FILE_PAT = AFM_DIR + '/{}.afm'

        with open(FILE_PAT.format(font_name)) as f:
            lines = [l for l in f.read().splitlines() if l[:8]!='Comment ']

        parsed = {}
        i = 1
        typify = lambda a: None if not a else (a[0] if len(a) == 1 else a)
        while i < len(lines):
            elems = lines[i].strip().split()
            field = elems[0]
            attrs = elems[1:]
            if field[:5] == 'Start' and attrs:
                parsed[field[5:]] = lines[i+1:int(attrs[0])+i+1]
                i += int(attrs[0])+1
            else:
                parsed[field] = typify(attrs)
                i += 1
        charmets = [{i.split()[0]:typify(i.split()[1:])
                     for i in l.split(';') if i.strip()}
                    for l in parsed['CharMetrics']]
        first_char = min(int(i['C']) for i in charmets if i['C'] != '-1')
        last_char  = min(int(i['C']) for i in charmets)
        widths     = [i['WX']
                      for i in sorted(charmets, key=lambda x: int(x['C']))
                        if i['C'] != '-1']
        charset    = [PdfName(i['N'])  for i in charmets if i['C'] != '-1']
        intprop = lambda x: None if x not in parsed else int(parsed[x])

        flags =   1*int(parsed.get('IsFixedPitch') == 'true')\
              +   8*(parsed['CharacterSet'] == 'Special')    \
              +  64*(parsed['CharacterSet'] != 'Special')    \
              + 128*(parsed['ItalicAngle'] != '0')
        fdesc = {PdfName('Type')       : 'FontDescriptor',
                 PdfName('FontName')   : parsed['FontName'],
                 PdfName('FontFamily') : parsed['FamilyName'],
                 PdfName('FontWeight') : parsed['Weight'],
                 PdfName('Flags')      : flags,
                 PdfName('FontBBox')   : [int(i) for i in parsed['FontBBox']],
                 PdfName('ItalicAngle'): intprop('ItalicAngle'),
                 PdfName('Ascent')     : intprop('Ascender'),
                 PdfName('Descent')    : intprop('Descender'),
                 PdfName('CapHeight')  : intprop('CapHeight'),
                 PdfName('XHeight')    : intprop('XHeight'),
                 PdfName('StemV')      : intprop('StdHW'),
                 PdfName('StemH')      : intprop('StdVW'),
                 PdfName('Charset')    : charset,
                }
        font  = {PdfName('Type')     : 'Font',
                 PdfName('Subtype')  : 'Type1',
                 PdfName('BaseFont') : parsed['FontName'],
                 PdfName('FirstChar'): first_char,
                 PdfName('LastChar') : last_char,
                 PdfName('Widths')   : widths,
                 PdfName('FontDescriptor'): PdfDict(fdesc),
                }
        return cls(PdfDict(font))
