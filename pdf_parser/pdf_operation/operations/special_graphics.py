import copy

from ..pdf_operation import PdfOperation
from ...pdf_matrix   import PdfMatrix


class cm(PdfOperation):
    opcode = 'cm'
    optype = PdfOperation.SPECIAL_GRAPHICS_STATE
    
    @staticmethod
    def do_opcode(renderer, a, b, c, d, e, f):
        renderer._gs.CTM = PdfMatrix(a, b, c, d, e, f)

class q(PdfOperation):
    opcode = 'q'
    optype = PdfOperation.SPECIAL_GRAPHICS_STATE
    
    @staticmethod
    def do_opcode(renderer):
        renderer.push_state()

class Q(PdfOperation):
    opcode = 'Q'
    optype = PdfOperation.SPECIAL_GRAPHICS_STATE
    
    @staticmethod
    def do_opcode(renderer):
        renderer.pop_state()