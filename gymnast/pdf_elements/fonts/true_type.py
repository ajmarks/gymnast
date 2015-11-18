"""
TrueType Fonts
"""

from .base_font       import PdfBaseFont

class TrueTypeFont(PdfBaseFont):
    """For our purposes, these are just a more restricted form of the Type 1
    Fonts, so...we're done here."""

    def text_space_coords(self, x, y):
        """Type1 fonts just scale by 1/1000 to convert from glyph space"""
        return x/1000., y/1000.
