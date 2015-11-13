from ..exc           import *
from ..pdf_elements  import PdfPage
from ..pdf_matrix    import PdfMatrix
from ..pdf_operation import PdfOperation

import io


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
        self._CTM     = self.id_matrix
        self._page    = page
        self._fonts   = page.Fonts
        self._in_text = False
        self._state_stack = []
        self._raw_glyphs = io.StringIO()
    
    def _preop(self, op):
        """Method called before each operation is executed.
        TODO: Decide if I really want to keep these names."""
        pass
    def _postop(self, op):
        """Method called before each operation is executed."""
        pass
    def _render_text(self, text, new_state):
        """Method called when a new text string is written. Arguments are the 
        string to be written and the rendering matrix that would result based 
        on the glyph widths."""
        pass
    def _move_text_cursor(self, newT_m):
        """Called before a TJ operand moves the next cursor.  Arugment is the 
        new updated text matrix after the move."""
        pass
    def _pre_render(self):
        """Method called at the start of page rendering"""
    def _return(self):
        """Do any required finalization and return the parsed result.
        This is the only one of the class methods that absolutely must be 
        implemented by subclasses."""
        raise NotImplementedError

    def render(self):
        self._pre_render()
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
    def text_coords(self):
        """Return the current text matrix coordinates"""
        return self._T_rm.current_coords

    def push_state(self):
        """Push the current graphics state onto the stack"""
        self._state_stack.append((self._CTM,))
    def pop_state(self):
        """Pop the last graphics state off the stack"""
        self._CTM, *args = self._state_stack.pop()

    def _compute_T_rm(self, **kwargs):
        T_m = kwargs.get('T_m', self._T_m)
        CTM = kwargs.get('CTM', self._CTM)
        return PdfMatrix(self._T_fs*self._T_h,    0, 
                                  0,          self._T_fs, 
                                  0,          self._T_rise)*T_m*CTM
    @property
    def _T_rm(self):
        """Text rendering matrix.  See Referecne pp. 409-410"""
        return self._compute_T_rm()

    @property
    def id_matrix(self):
        return self._id_matrix
    
    def _get_glyph_width(self, glyph):
        return self.active_font.get_glyph_width(glyph)/1000.0

    def render_text(self, string, TJ=False):
        """Write the string to the text output and, depending on the mode,
        updates T_m.  See pp.409-10.

        Arguments:
            glyph - One character string (default: None)
            TJ    - Are we in TJ mode (so don't auto-shift)
        TODO: Vertical writing"""
        # This shortcut works.  Check the math.
        widths = sum(self._get_glyph_width(glyph) for glyph in string)
        t_x = (widths*self._T_fs+self._T_c+self._T_w)*self._T_h
        t_y = 0.0
        T_m = PdfMatrix(1, 0, 0, 1, t_x, t_y)*self._T_m
        self._render_text(string, self._compute_T_rm(T_m=T_m))
        if not TJ:
            self._T_m = T_m
    def move_text_cursor(self, t):
        t_x = (-t/1000.0*self._T_fs+self._T_c+self._T_w)*self._T_h
        t_y = 0.0 # <--- TODO: this
        T_m = PdfMatrix(1, 0, 0, 1, t_x, t_y)*self._T_m
        self._move_text_cursor(T_m)
        self._T_m = T_m
        
        
