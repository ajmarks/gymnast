"""
Special graphics state operations - p. 219
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

PdfOperation.register('cm', PdfOperation.SPECIAL_GRAPHICS_STATE, opcode_cm)
PdfOperation.register('q',  PdfOperation.SPECIAL_GRAPHICS_STATE, opcode_q)
PdfOperation.register('Q',  PdfOperation.SPECIAL_GRAPHICS_STATE, opcode_Q)
