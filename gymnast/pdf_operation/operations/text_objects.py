"""
Text Object operations - Reference p. 405
"""

from ..pdf_operation             import PdfOperation
from ...exc                      import PdfError
from ...renderer.renderer_states import TextState

def opcode_BT(renderer):
    if renderer.in_text:
        raise PdfError('Cannot being a new text object without ending the previous')
    renderer.in_text = True
    renderer.ts.T_m  = TextState.id_matrix
    renderer.ts.T_lm = TextState.id_matrix

def opcode_ET(renderer):
    if not renderer.in_text:
        raise PdfError('ET without a corresponding BT end text object')
    else:
        renderer.in_text = False
        renderer.ts.T_m  = None
        renderer.ts.T_lm = None

PdfOperation.register('BT', PdfOperation.TEXT_OBJECTS, opcode_BT)
PdfOperation.register('ET', PdfOperation.TEXT_OBJECTS, opcode_ET)
