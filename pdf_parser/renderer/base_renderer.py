from ..exc           import *
from ..pdf_elements  import PdfPage
from ..pdf_matrix    import PdfMatrix
from ..pdf_operation import PdfOperation

#Nonsense to make PTVS happy
from builtins import *

class PdfBaseRenderer(object):
    """PdfRenderer object.  PdfOperations act on this to produce a
    representation of the contents of the pdf document.  This class primarily
    serves to maintain the global state as the page is drawn.
    
    Usage:
        redered_page = PdfRenderer(page).render()
        
    TODO: Better encapsulate internals with setters and getters
    TODO: Vertical writing support
    TODO: Figure out graphics stuff"""
    
    #Type hints
    if False:
        _page = PdfPage()
    
    def __init__(self, page):
        self._id_matrix = PdfMatrix(1, 0, 0, 1, 0, 0)
        self._T_c     = 0.0  # Char space
        self._T_w     = 0.0  # Word space
        self._T_h     = 1.0  # Horizontal text scale
        self._T_l     = 0.0  # Text leading
        self._T_f     = None # Font
        self._T_fs    = None # Font scaling
        self._T_mode  = 0    # Text render mode
        self._T_rise  = 0.0  # Text rise
        self._Tm      = self.id_matrix
        self._Tlm     = self.id_matrix
        self._page    = page
        self._fonts   = page.Fonts
        self._in_text = False
    
    def _preop(self, op):
        """Method called before each operation is executed.
        TODO: Decide if I really want to keep these names."""
        pass
    def _postop(self, op):
        """Method called before each operation is executed."""
        pass
    def _post_write(self, glyph=None, tx=0.0, ty=0.0):
        """Method called when a new character is written.
        Arguments are the glyph written, and the resulting tx and ty shifts."""
        pass
    def _return(self):
        """Do any required finalization and return the parsed result.
        This is the only one of the class methods that absolutely must be 
        implemented by subclasses."""
        raise NotImplementedError

    def render(self):
        for op in self._page.Contents.operations:
            self._preop(op)
            op(self)
            self._postop(op)
        return self._return()

    def reset_T_m(self):
        """Reset the text matrix to the identity"""
        self._T_m  = self.id_matrix
    
    def reset_T_lm(self):
        """Reset the line matrix to the general text matrix"""
        self._T_lm = self._Tm.copy()
    
    def bytes_to_glyphs(self, string):
        """Converts a bytestring into a series of glyphs based upon the active
        font's encoding"""
        pass
    @property
    def active_font(self):
        return self._fonts[self._T_f]

    @property
    def id_matrix(self):
        return self._id_matrix
    
    def _get_glyph_width(self, glyph):
        return self.active_font.get_glyph_width(glyph)

    def write_glyph(self, glyph=None, T_j=0.0):
        """Write the glyph to the text output and update T_m.  See pp.409-10.

        Arguments:
            glyph - One character string
            T_j   - Real values spacing offset from a Tj operations (default 0.0)
        
        TODO: Vertical writing"""
        if glyph:
            w0 = self._get_glyph_width(glyph)
        else:
            w0 = 0.0
        
        tx = ((w0-T_j/1000.0)*self._T_fs+self._T_c+self._T_w)*self._T_h
        ty = 0.0 # <--- TODO: this
        self._T_m = PdfMatrix(1, 0, 0, 1, tx, ty)*self._T_m
        self._post_write(glyph, tx, ty)