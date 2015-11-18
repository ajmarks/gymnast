"""
Simple renderer example that just extracts the text with no processing
"""

import io
from .base_renderer import PdfBaseRenderer

class PdfSimpleRenderer(PdfBaseRenderer):
    """Simple renderer example that just extracts the text with no processing"""
    def __init__(self, page):
        """Create a new naive rendered that just collects all of the text"""
        super(PdfSimpleRenderer, self).__init__(page)
        self._text = io.StringIO()
    def _render_text(self, text, new_state):
        """Add the text to the buffer"""
        self._text.write(self.active_font.decode_string(text))
    def _return(self):
        """Return collected text"""
        return self._text.getvalue()
