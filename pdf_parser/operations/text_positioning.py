from ..pdf_matrix    import PdfMatrix
from ..pdf_operation import PdfOperation

class Td(PdfOperation):
    opcode = 'Td'
    optype = PdfOperation.TEXT_POSITIONING

    @staticmethod
    def do_opcode(renderer, t_x, t_y):
        renderer._ts.T_m = PdfMatrix(1, 0, 0, 1, t_x, t_y)*renderer._ts.T_lm
        renderer._ts.reset_T_lm()

class TD(PdfOperation):
    opcode = 'TD'
    optype = PdfOperation.TEXT_POSITIONING

    @staticmethod
    def do_opcode(renderer, t_x, t_y):
        PdfOperation['TL'](-t_y)(renderer)
        PdfOperation['Td'](t_x, t_y)(renderer)

class Tm(PdfOperation):
    opcode = 'Tm'
    optype = PdfOperation.TEXT_POSITIONING

    @staticmethod
    def do_opcode(renderer, a, b, c, d, e, f):
        renderer._ts.T_m = PdfMatrix(a, b, c, d, e, f)
        renderer._ts.reset_T_lm()

class Tstar(PdfOperation):
    opcode = 'T*'
    optype = PdfOperation.TEXT_POSITIONING

    @staticmethod
    def do_opcode(renderer):
        PdfOperation['Td'](0, renderer._T_l)(renderer)