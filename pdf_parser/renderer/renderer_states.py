"""
Parameter sets representing renderer states
"""

import copy
from collections import namedtuple
from ..pdf_matrix import PdfMatrix

__all__ = ['TextState', 'GraphicsState']

class TextState(object):
    """Renderer text state.  Has all of the various text rendering
    parameters"""
    id_matrix = PdfMatrix(1, 0, 0, 1, 0, 0)
    def __init__(self):
        self.T_c     = 0.0  # Char space
        self.T_w     = 0.0  # Word space
        self.T_h     = 1.0  # Horizontal text scale
        self.T_l     = 0.0  # Text leading
        self.T_f     = None # Font
        self.T_fs    = None # Font scaling
        self.T_mode  = 0    # Text render mode
        self.T_rise  = 0.0  # Text rise
        self.T_m     = self.id_matrix # Text Matrix
        self.T_lm    = self.id_matrix # Line Matrix

    def reset_T_m(self):
        """Reset the text matrix to the identity"""
        self.T_m  = self.id_matrix

    def reset_T_lm(self):
        """Reset the line matrix to the general text matrix"""
        self.T_lm = copy.copy(self.T_m)

#For now, GraphicsState can be treated as a slightly tweaked namedtuple
GraphicsState = namedtuple('GraphicsState', ['CTM'])
GraphicsState.__new__.__defaults__ = (TextState.id_matrix,)
