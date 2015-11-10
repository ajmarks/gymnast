from .pdf_constants import BASE_ENCODINGS
from .pdf_common    import PdfObject
from .pdf_parser    import PdfParser
from .pdf_types     import PdfLiteralString
#from pdf_parser     import PdfParser

#PTVS nonsense
from builtins import *

class FontDescriptor(PdfObject):
    """FontDescriptior object describefd in Table 5.19 on p. 456.
    Note that this will need to be overloaded to properly handle Type3 fonts."""
    def __init__(self, obj):
        super().__init__(obj)
        self._charset = None
        chars = obj.value.get('CharSet')
        if isinstance(chars, PdfLiteralString):
            self._charset = PdfParser().parse(chars, False)
    @property
    def CharSet(self):
        return self._charset

class FontEncoding(PdfObject):
    """Font encoding object as described in Appendix D"""

    #This should never change ever, but why hardcode in two places?
    VALID_ENCODINGS = set(next(iter(BASE_ENCODINGS.values())).keys())

    def __init__(self, obj):
        super().__init__(obj)
        base_encoding = obj.value.get('BaseEncoding')
        if base_encoding is None:
            base_encoding = 'StandardEncoding'
        elif base_encoding not in VALID_ENCODINGS:
            raise ValueError('Invalid BaseEncoding')
        self._base_encoding = base_encoding
        
        # Build the default encoding system
        glyphnames = {v[base_encoding]: k  
                        for k,v in BASE_ENCODINGS.items()}
        # Now modify it with the differences array, if specified
        diffs = obj.value.get('Differences', [])
        if not isinstance(diffs, (list, tuple)):
            raise ValueError('Invalid differences array')
        if isinstance(diffs[0], list):
            differences = sum(diffs, [])
        for d in diffs:
            if isinstance(d, int):
                code = d
            else:
                glyphnames[code] = d
                code += 1
        self._glyphnames = glyphnames
        self._charcodes  = {v:k for k,v in glyphnames.items()}

    def get_glyph_name(self, code):
        return self._glyphnames[code]
    def get_char_code(self, name):
        return self._charcodes[name]

class PdfFont(PdfObject):
    def __init__(self, font):
        """See Table 5.8 on p. 413"""
        super().__init__(font)

    def get_glyph_width(self, glyph):
        if not isinstance(glyph, int):
            if len(glyph) != 1:
                raise ValueError('Invalid glyph')
            # We're going to need to modify PyPDF2 to do better here,
            # also this should use the encodings 
            glyph = int.from_bytes(glyph.encode('utf_16_be'))
        if glyph > self._last_char:
            return self.FontDescriptor.missing_width
        return self._widths[glyph - self._first_char]

    def glyph_to_unicode(self, glyph_code):
        """TODO: Support ToUnicode CMaps"""
        return self.GLYPH_LIST[self.get_glyph_name(glyph_code)]

    def get_glyph_name(self, code):
        return self.Encoding.get_glyph_name(code)
    def get_char_code(self, name):
        return self.Encoding.get_char_code(name)

    @property
    def space_width(self):
        """Width of the space character in the current font"""
        return self.get_glyph_width(self.get_char_code('space'))