import .pdf_constants

class FontDescriptor(object):
    """FontDescriptior object describefd in Table 5.19 on p. 456.
    Note that this will need to be overloaded to properly handle Type3 fonts."""

    # Dict mapping official PDF FontDescriptor names to our pythonic ones
    names_map = {'FontName'    :'font_name',
                 'Flags'       :'flags',
                 'FontBBox'    :'font_b_box',
                 'ItalicAngle' :'italic_angle',
                 'Ascent'      :'ascent',
                 'Descent'     :'descent',
                 'CapHeight'   :'cap_height',
                 'StemV'       :'stem_v',
                 'FontFamily'  :'font_family',
                 'FontStretch' :'font_stretch',
                 'FontWeight'  :'font_weight',
                 'Leading'     :'leading',
                 'XHeight'     :'x_height',
                 'StemH'       :'stem_h',
                 'AvgWidth'    :'avg_width',
                 'MaxWidth'    :'max_width',
                 'MissingWidth':'missing_width',
                 'FontFile'    :'font_file',
                 'FontFile2'   :'font_file2',
                 'FontFile3'   :'font_file3',
                 'CharSet'     :'char_set'}

    def __init__(self, font_name, flags, font_b_box, italic_angle, ascent,
                       descent, cap_height,stem_v,
                       font_family=None, font_stretch=None, font_weight=None,
                       leading=0, x_height=None, stem_h=0, avg_width=0,
                       max_width=0, missing_width=0, font_file=None, 
                       font_file2=None, font_file3=None, char_set=None):
        self.font_name     = font_name
        self.flags         = flags
        self.font_b_box    = font_b_box
        self.italic_angle  = italic_angle
        self.ascent        = ascent
        self.descent       = descent
        self.cap_height    = cap_height
        self.stem_v        = stem_v
        self.font_family   = font_family
        self.font_stretch  = font_stretch
        self.font_weight   = font_weight
        self.leading       = leading
        self.x_height      = x_height
        self.stem_h        = stem_h
        self.avg_width     = avg_width
        self.max_width     = max_width
        self.missing_width = missing_width
        self.font_file     = font_file
        self.font_file2    = font_file2
        self.font_file3    = font_file3
        if isinstance(char_set, str):
            self.char_set  = ['/'+c for c in char_set.split('/')[1:]]
        elif isinstance(char_set, (list, tuple)) or char_set is None:
            self.char_set  = char_set
        else:
            raise ValueError('Invalid CharSet')


class FontEncoding(object):
    """Font encoding object as described in Appendix D"""

    # Base font encodings
    BASE_ENCODINGS  = pdf_constants.BASE_ENCODINGS
    #This should never change ever, but why hardcode in two places?
    VALID_ENCODINGS = set(next(iter(BASE_ENCODINGS.values())).keys())

    def __init__(self, base_encoding=None, differences=None):
        if base_encoding is None:
            base_encoding = 'StandardEncoding'
        elif base_encoding not in VALID_ENCODINGS:
            raise ValueError('Invalid BaseEncoding')
        self._base_encoding = base_encoding
        
        # Build the default encoding system
        glyphnames = {v[base_encoding]: k  
                        for k,v in BASE_ENCODINGS.items()}
        # Now modify it with the differences array, if specified
        if not differences:
            differences = []
        if not isinstance(differences, (list, tuple)):
            raise ValueError('Invalid differences array')
        if isinstance(differences[0], list):
            differences = sum(differences, [])
        for d in differences:
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

class PdfFont(object):
    GLYPH_LIST = pdf_constants.GLYPH_LIST
    def __init__(self, font):
        """See Table 5.8 on p. 413"""
        self._type       = font['Type']
        self._subtype    = font['Subtype']
        self._name       = font.get('Name')
        self._base_font  = font.get('BaseFont')
        self._first_char = font['FirstChar']
        self._last_char  = font['LastChar']
        self._widths     = font['Widths']
        self._descriptor = FontDescriptor(**{v: font['FontDescriptor'][k] 
                                           for k, v in FontDescriptor.names_map.items()
                                             if k in font['FontDescriptor']})
        self._encoding   = FontEncoding(font['Encoding'].get('BaseEncoding'),
                                        font['Encoding'].get('Differences'))

    def get_glyph_width(self, glyph):
        if not isinstance(glyph, int):
            if len(glyph) != 1:
                raise ValueError('Invalid glyph')
            # We're going to need to modify PyPDF2 to do better here,
            # also this should use the encodings 
            glyph = int.from_bytes(glyph.encode('utf_16_be'))
        if glyph > self._last_char:
            return self._descriptor.missing_width
        return self._widths[glyph - self._first_char]

    def glyph_to_unicode(self, glyph_code):
        """TODO: Support ToUnicode CMaps"""
        return self.GLYPH_LIST[self.get_glyph_name(glyph_code)]

    def get_glyph_name(self, code):
        return self._encoding.get_glyph_name(code)
    def get_char_code(self, name):
        return self._encoding.get_char_code(name)

    @property
    def space_width(self):
        """Width of the space character in the current font"""
        return self.get_glyph_width(self.get_char_code('space'))