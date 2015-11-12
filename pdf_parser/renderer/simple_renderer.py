import io
from .base_renderer import PdfBaseRenderer

class PdfSimpleRenderer(PdfBaseRenderer):
    def __init__(self, page):
        super().__init__(page)
        self._text = io.StringIO()
    def _post_write(self, glyph=None, tx=0.0, ty=0.0):
        if glyph:
            self._text.write(self.active_font.decode_char(glyph))
    def _return(self):
        return self._text.getvalue()