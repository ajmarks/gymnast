from .base_renderer import PdfBaseRenderer

class PdfTextRenderer(PdfBaseRenderer):
    """More sophisticated page renderer.  Stores the result of each text 
    showing operator in a TextBlock object, which are then assigned to lines
    on the page based on their vertical coordinates.  After the page has been 
    processed, it goes over each line determining spacing based on the gap
    between successive TextBlocks in the line and width of the space character
    in the first of the two.
    
    TODO: Add support for vertical text direction and RTL languages"""


    def _preop(self):
        # If the op is a text showing one, create a new text box for it
        pass

    @property
    def _space_width(self):
        """The width of a space in the current font"""
        # TODO: Double check that we need to go to the encoding here
        c = font.Encoding.get_char_code('space')-self.active_font['FirstChar']
        return self.active_font['Widths'][c]
    @property
    def active_font(self):
        if self._T_f:
            return self._fonts[self._T_f]
        else:
            return None

    @property
    def _cap_height(self):
        """The height of a capital letter in the current font"""
        return self.active_font['FontDescriptor']['CapHeight']

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