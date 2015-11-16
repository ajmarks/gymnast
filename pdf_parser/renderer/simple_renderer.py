import io
from .base_renderer import PdfBaseRenderer

class PdfSimpleRenderer(PdfBaseRenderer):
    """Simple renderer example that just extracts the text with no processing"""
    def __init__(self, page):
        super(PdfSimpleRenderer, self).__init__(page)
        self._text = io.StringIO()
    def _render_text(self, text, new_state):
        for glyph in text:
            self._text.write(self.active_font.decode_char(glyph))
    def _return(self):
        return self._text.getvalue()