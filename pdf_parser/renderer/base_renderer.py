"""
Base page renderer class
"""

from .renderer_states import TextState, GraphicsState
from ..exc           import *
from ..pdf_elements  import PdfPage
from ..pdf_matrix    import PdfMatrix

import copy
import io


#Nonsense to make PTVS happy


class PdfBaseRenderer(object):
    """PdfRenderer object.  PdfOperations act on this to produce a
    representation of the contents of the pdf document.  This class primarily
    serves to maintain the global state as the page is drawn.

    Usage:
        redered_page = PdfRenderer(page).render()

    TODO: Better encapsulate internals with setters and getters
    TODO: Vertical writing support
    TODO: Figure out graphics stuff"""

    def __init__(self, page):
        self.ts      = TextState()   # Text state
        self._gs      = GraphicsState() # Graphics state
        self._page    = page
        self._fonts   = page.Fonts
        self.in_text = False
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

    def bytes_to_glyphs(self, string):
        """Converts a bytestring into a series of glyphs based upon the active
        font's encoding"""
        pass
    @property
    def active_font(self):
        return self._fonts[self.ts.T_f]

    @property
    def text_coords(self):
        """Return the current text matrix coordinates"""
        return self._T_rm.current_coords

    def push_state(self):
        """Push the current graphics state onto the stack"""
        self._state_stack.append(copy.deepcopy(self._gs))
    def pop_state(self):
        """Pop the last graphics state off the stack"""
        self._gs = self._state_stack.pop()

    def _compute_T_rm(self, **kwargs):
        T_m = kwargs.get('T_m', self.ts.T_m)
        CTM = kwargs.get('CTM', self._gs.CTM)
        ts = self.ts
        return PdfMatrix(ts.T_fs*ts.T_h,     0,
                                0,        ts.T_fs,
                                0,       ts.T_rise)*T_m*CTM
    @property
    def _T_rm(self):
        """Text rendering matrix.  See Referecne pp. 409-410"""
        return self._compute_T_rm()

    def _get_glyph_width(self, glyph):
        #TODO: use font transformations
        return self.active_font.get_glyph_width(glyph)/1000.0

    def render_text(self, string, TJ=False):
        """Write the string to the text output and, depending on the mode,
        updates T_m.  See pp.409-10.

        Arguments:
            glyph - One character string (default: None)
            TJ    - Are we in TJ mode (so don't auto-shift)
        TODO: Vertical writing"""
        # This shortcut works.  Check the math.
        ts = self.ts
        widths = sum(self._get_glyph_width(glyph) for glyph in string)
        t_x = (widths*ts.T_fs + ts.T_c + ts.T_w) * ts.T_h
        t_y = 0.0 # <--- TODO: Vertical writing mode
        T_m = PdfMatrix(1, 0, 0, 1, t_x, t_y) * ts.T_m
        self._render_text(string, self._compute_T_rm(T_m=T_m))
        if not TJ:
            self.ts.T_m = T_m
    def move_text_cursor(self, t):
        ts  = self.ts
        t_x = (-t/1000.0*ts.T_fs + ts.T_c + ts.T_w) * ts.T_h
        t_y = 0.0 # <--- TODO: Vertical writing mode
        T_m = PdfMatrix(1, 0, 0, 1, t_x, t_y)*ts.T_m
        self._move_text_cursor(T_m)
        self.ts.T_m = T_m
