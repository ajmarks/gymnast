"""
Graphics state operations listed on p. 219
"""

from ..pdf_operation import PdfOperation
from ...pdf_matrix   import PdfMatrix

def opcode_cm(renderer, a, b, c, d, e, f):
    """Set the current transformation matrix (CTM)"""
    renderer.gs.CTM = PdfMatrix(a, b, c, d, e, f)

def opcode_q(renderer):
    """Store the current graphics state on top of the stack"""
    renderer.push_state()

def opcode_Q(renderer):
    """Retore the graphics state from the top of the stack"""
    renderer.pop_state()

def opcode_w(renderer, line_width):
    """Set line width"""
    renderer.gs.line_width = line_width

def opcode_J(renderer, line_cap):
    """Set line cap style (see p. 216)"""
    renderer.gs.line_cap = line_cap

def opcode_j(renderer, line_join):
    """Set line join style (see p. 216)"""
    renderer.gs.line_join = line_join

def opcode_M(renderer, miter_limit):
    """Set miter limit (see p. 217)"""
    renderer.gs.miter_limit = miter_limit

def opcode_d(renderer, dash_array, dash_phase):
    """Set dash array and phase (see p. 217)"""
    renderer.gs.dash_array = dash_array
    renderer.gs.dash_phase = dash_phase

def opcode_ri(renderer, intent):
    """Set the rendering intent (see p. 260)"""
    renderer.gs.intent = intent

def opcode_i(renderer, flatness):
    """Set the flatness tolerance (see p. 260)"""
    renderer.gs.intent = intent

#TODO: gs

PdfOperation.register('cm',  PdfOperation.SPECIAL_GRAPHICS_STATE, opcode_cm)
PdfOperation.register('q',   PdfOperation.SPECIAL_GRAPHICS_STATE, opcode_q)
PdfOperation.register('Q',   PdfOperation.SPECIAL_GRAPHICS_STATE, opcode_Q)
PdfOperation.register('w',   PdfOperation.GENERAL_GRAPHICS_STATE, opcode_w)
PdfOperation.register('J',   PdfOperation.GENERAL_GRAPHICS_STATE, opcode_J)
PdfOperation.register('j',   PdfOperation.GENERAL_GRAPHICS_STATE, opcode_j)
PdfOperation.register('M',   PdfOperation.GENERAL_GRAPHICS_STATE, opcode_M)
PdfOperation.register('d',   PdfOperation.GENERAL_GRAPHICS_STATE, opcode_d)
PdfOperation.register('ri',  PdfOperation.GENERAL_GRAPHICS_STATE, opcode_ri)
PdfOperation.register('i',   PdfOperation.GENERAL_GRAPHICS_STATE, opcode_i)
