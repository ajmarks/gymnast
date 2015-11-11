from bidict import collapsingbidict

from .pdf_element    import PdfElement
from ..pdf_constants import BASE_ENCODINGS, GLYPH_LIST
from ..pdf_parser    import PdfParser
from ..pdf_types     import PdfLiteralString
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
        if isinstance(diffs[0], list):
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

class PdfFont(PdfElement):
    def get_glyph_width(self, glyph):
        if not isinstance(glyph, int):
            if len(glyph) != 1:
                raise ValueError('Invalid glyph')
            # We're going to need to modify PyPDF2 to do better here,
            # also this should use the encodings 
            glyph = int.from_bytes(glyph.encode('utf_16_be'))
        if glyph > self.LastChar or glyph < self.FirstChar:
            return self.FontDescriptor.get('MissingWidth', 0)
        return self.Widths[glyph - self.FirstChar]

    def glyph_to_unicode(self, glyph_code):
        """TODO: Support ToUnicode CMaps"""
        return GLYPH_LIST[self.get_glyph_name(glyph_code)]

    def get_glyph_name(self, code):
        return self.Encoding.get_glyph_name(code)
    def get_char_code(self, name):
        return self.Encoding.get_char_code(name)

    @property
    def space_width(self):
        """Width of the space character in the current font"""
        return self.get_glyph_width(self.get_char_code('space'))