from ..pdf_operation import PdfOperation
from ...renderer import TextState

class BT(PdfOperation):
    """Begin a text object, resetting the text and line matricies"""
    opcode  = b'BT'
    optype = PdfOperation.TEXT_OBJECTS

    @staticmethod
    def do_opcode(renderer):
        if renderer._in_text:
            raise PdfError('Cannot being a new text object without ending the previous')
        renderer._in_text = True
        renderer._ts      = TextState()

class ET(PdfOperation):
    """Begin a text object, resetting the text and line matricies"""
    opcode  = b'ET'
    optype = PdfOperation.TEXT_OBJECTS
    
    @staticmethod
    def do_opcode(renderer):
        if not renderer._in_text:
            raise PdfError('ET without a corresponding BT end text object')
        else:
            renderer._in_text = False
            renderer._ts      = None