"""
Special graphics state operations - p. 219
"""

from ..pdf_operation import PdfOperation
from ...pdf_matrix   import PdfMatrix

def opcode_cm(renderer, a, b, c, d, e, f):
    renderer._gs.CTM = PdfMatrix(a, b, c, d, e, f)

def opcode_q(renderer):
    renderer.push_state()

def opcode_Q(renderer):
    renderer.pop_state()

PdfOperation.register('cm', PdfOperation.SPECIAL_GRAPHICS_STATE, opcode_cm)
PdfOperation.register('q',  PdfOperation.SPECIAL_GRAPHICS_STATE, opcode_q)
PdfOperation.register('Q',  PdfOperation.SPECIAL_GRAPHICS_STATE, opcode_Q)
