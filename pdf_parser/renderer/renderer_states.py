import copy
from ..pdf_matrix import PdfMatrix

__all__ = ['TextState', 'GraphicsState']

class RendererState(object):
    id_matrix = PdfMatrix(1, 0, 0, 1, 0, 0)

class TextState(RendererState):
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
        self.T_lm = copy.copy(self._ts.T_m)

class GraphicsState(RendererState):
    def __init__(self):
        self.CTM    = self.id_matrix # Current transformation matrix