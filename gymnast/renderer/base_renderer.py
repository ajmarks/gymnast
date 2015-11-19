"""
Base page renderer class
"""

from .renderer_states import TextState, GraphicsState
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

    TODO: Vertical writing support
    TODO: Figure out graphics stuff"""

    def __init__(self, page):
        self.ts      = TextState()     # Text state
        self.gs      = GraphicsState() # Graphics state
        self._page   = page
        self._fonts  = page.Fonts
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

    def render(self, *args, **kwargs):
        """Render the page"""
        self._pre_render(*args, **kwargs)
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
        """The PdfBaseFont representing the font specified by T_f"""
        return self._fonts[self.ts.f]

    @property
    def text_coords(self):
        """The current text matrix coordinates"""
        return self.ts.m.current_coords

    def push_state(self):
        """Push the current graphics state onto the stack"""
        self._state_stack.append(copy.deepcopy(self.gs))
    def pop_state(self):
        """Pop the last graphics state off the stack"""
        self.gs = self._state_stack.pop()

    def _compute_T_rm(self, m=None, CTM=None):
        """Compute the text rendering matrix (T_rm) based either on the current
        text matrix and CTM, or using the specified overrides"""
        ts = self.ts
        if not m:
            m = ts.m
        if not CTM:
            CTM = self.gs.CTM
        return PdfMatrix(ts.fs*ts.h,    0,
                                0,    ts.fs,
                                0,   ts.rise)*m*CTM

    def _get_glyph_width(self, glyph):
        """Get the glyph's width in _text_ space.

        IDEA: Consider adding a helper method in fonts for this"""
        raw_width = self.active_font.get_glyph_width(glyph)
        return self._gs_to_ts(raw_width, 0)[0]

    def _gs_to_ts(self, x, y):
        """Convert coordinates from glyph space to text space"""
        return self.active_font.text_space_coords(x, y)

    def _extra_space(self, glyph):
        """Compute the appropriate amount of extra spacing to apply based on
        the last glyph drawn and the character- and word-spacing parameters in
        the current text state.

        Equivalent to T_c + T_w in the formulae on p. 410"""
        return self.ts.w if glyph == ' ' else self.ts.w

    def render_text(self, string):
        """Write the string to the text output and, depending on the mode,
        updates T_m.  See pp.409-10.

        TODO: Vertical writing"""
        # This shortcut works.  Check the math.
        ts = self.ts
        widths = (self._get_glyph_width(glyph)*ts.fs + self._extra_space(glyph)
                  for glyph in string)
        t_x = sum(widths) * ts.h
        t_y = 0.0 # <--- TODO: Vertical writing mode
        T_m = PdfMatrix(1, 0, 0, 1, t_x, t_y) * ts.m
        self._render_text(string, T_m)
        self.ts.m = T_m

    def move_text_cursor(self, t, last_glyph=b''):
        """Reposition the current text coordinates by a factor of t as is done
        in TJ operations (see Reference pp. 408-410"""
        ts  = self.ts
        t_x = -t/1000.0 * ts.fs * ts.h
        t_y = 0.0 # <--- TODO: Vertical writing mode
        T_m = PdfMatrix(1, 0, 0, 1, t_x, t_y)*ts.m
        self._move_text_cursor(T_m)
        self.ts.m = T_m
