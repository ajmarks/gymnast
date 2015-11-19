"""
Parameter sets representing renderer states
"""

import copy
from ..pdf_matrix import PdfMatrix

__all__ = ['TextState', 'GraphicsState']

class RendererState(object):
    """Base class for renderer states"""
    id_matrix = PdfMatrix(1, 0, 0, 1, 0, 0)

class TextState(object):
    """Renderer text state.  Has all of the various text rendering parameters
    described on pp. 396-404 in the Reference (without the leading T).
    
    Attributes (all units are in text space units):
        m:  The current text matrix
        lm: Text matrix at the start of the current line
        c: Charcter spacing - Amount of extra space between characters before
           scaling by T_h.  Default 0.
        w: Word spacing - Extra space (pre-T_h) added on encountering a space.
           Default 0.
        h: Horizontal scaling - Scaling factor applied to character width and
           horizontal spacing (i.e., T_c and T_w).  Default 1.  
           N.B.: The associated Tz operator sets this to its operand divided by
           100.
        l: Leading - Vertical distance between the baselines of adjacent text
           lines. Default 0.
        f: Text font - The name of the current font in the current resource
           dictionary.  No default value.
        fs: Text font size - Scaling factor applied to the font in all 
            directions.  No default value.
        mode: Text rendering mode - Determines text shading, outlining, when
              rendering text.  Default 0 (solid fill, no stroke).
        rise: Text rise - Vertical offset from the baseline at which to draw
              the text.  Positive values result in superscript, negative in
              subsctipt. Default 0.
        k: Text knockout - Boolean used in drawing overlappign characters.
           Set through graphics state operators.  Default True."""
    id_matrix = PdfMatrix(1, 0, 0, 1, 0, 0)
    def __init__(self):
        """Create a new TextState object with values initialed to their
        respective defaults"""
        self.c     = 0.0    # Char space
        self.w     = 0.0    # Word space
        self.h     = 1.0    # Horizontal text scale
        self.l     = 0.0    # Text leading
        self.f     = None   # Font
        self.fs    = None   # Font scaling
        self.mode  = 0      # Text render mode
        self.rise  = 0.0    # Text rise
        self.m     = self.id_matrix # Text Matrix
        self.lm    = self.id_matrix # Line Matrix

    def reset_m(self):
        """Reset the text matrix to the identity"""
        self.m  = self.id_matrix

    def reset_lm(self):
        """Reset the line matrix to the general text matrix"""
        self.lm = copy.copy(self.m)


class GraphicsState(RendererState):
    """Renderer graphics state.  Has all of the various graphical state
    parameters, including the current transformation matrix."""
    def __init__(self):
        self.CTM    = self.id_matrix # Current transformation matrix
