from pdf_font import PdfFont

class TextBlock(object):
    """Represents a block of text in the PDF output"""
    
    _next_id = 0

    #Type hints
    if False:
        font = PdfFont()
    
    @classmethod
    def get_next_id(cls):
        cls._next_id += 1
        return cls._next_id
    
    @property
    def text(self):
        if self._text:
            return self._text
        return 

    def __init__(self, font, glyphs, x_0, x_1, y_0, height):
        self._font   = font
        self._glyphs = glyphs
        self._box    = (min(x_0, x_1), max(x_0, x_1), y_0, y_0+height)
        self._id     = self.get_next_id()
        self._text   = None