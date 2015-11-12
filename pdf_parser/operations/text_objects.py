from ..pdf_operation import PdfOperation

class BT(PdfOperation):
    """Begin a text object, resetting the text and line matricies"""
    opcode  = b'BT'
    optype = PdfOperation.TEXT_OBJECTS

    @staticmethod
    def do_opcode(renderer):
        if renderer._in_text:
            raise PdfError('Cannot being a new text object without ending the previous')
        renderer._in_text = True
        renderer._T_c     = 0.0  # Char space
        renderer._T_w     = 0.0  # Word space
        renderer._T_h     = 1.0  # Horizontal text scale
        renderer._T_l     = 0.0  # Text leading
        renderer._T_f     = None # Font
        renderer._T_fs    = None # Font scaling
        renderer._T_mode  = 0    # Text render mode
        renderer._T_rise  = 0.0  # Text rise
        renderer.reset_T_m()
        renderer.reset_T_lm()

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