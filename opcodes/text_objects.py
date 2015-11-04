from pdf_opcodes import PdfOper

class BT(PdfOper):
    """Begin a text object, resetting the text and line matricies"""
    opcode = b'BT'
    def do_opcode(cls):
        if cls.parser._text_mode:
            raise PdfError('Cannot being a new text object without ending the previous')
        cls.parser._in_text = True
        cls.parser._T_c     = 0.0  # Char space
        cls.parser._T_w     = 0.0  # Word space
        cls.parser._T_h     = 1.0  # Horizontal text scale
        cls.parser._T_l     = 0.0  # Text leading
        cls.parser._T_f     = None # Font
        cls.parser._T_fs    = None # Font scaling
        cls.parser._T_mode  = 0    # Text render mode
        cls.parser._T_rise  = 0.0  # Text rise
        cls.parser._reset_T_m()
        cls.parser._reset_T_lm()

class ET(PdfOper):
    """Begin a text object, resetting the text and line matricies"""
    opcode  = b'ET'
    @classmethod
    def do_opcode(cls):
        if not cls.parser._text_mode:
            raise PdfError('ET without a corresponding BT end text object')
        else:
            cls.parser._in_text = False