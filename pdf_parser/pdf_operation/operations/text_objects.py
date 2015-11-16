from ..pdf_operation import PdfOperation
from ...renderer     import TextState
from ...exc          import PdfError

class BT(PdfOperation):
    """Begin a text object, resetting the text and line matricies"""
    opcode  = 'BT'
    optype = PdfOperation.TEXT_OBJECTS

    @staticmethod
    def do_opcode(renderer):
        if renderer.in_text:
            raise PdfError('Cannot being a new text object without ending the previous')
        renderer.in_text = True
        renderer.ts.T_m  = TextState.id_matrix
        renderer.ts.T_lm = TextState.id_matrix


class ET(PdfOperation):
    """Begin a text object, resetting the text and line matricies"""
    opcode  = 'ET'
    optype = PdfOperation.TEXT_OBJECTS

    @staticmethod
    def do_opcode(renderer):
        if not renderer.in_text:
            raise PdfError('ET without a corresponding BT end text object')
        else:
            renderer.in_text = False
            renderer.ts.T_m  = None
            renderer.ts.T_lm = None
