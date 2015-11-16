from ..pdf_operation import PdfOperation
from ...pdf_matrix   import PdfMatrix

class Td(PdfOperation):
    opcode = 'Td'
    optype = PdfOperation.TEXT_POSITIONING

    @staticmethod
    def do_opcode(renderer, t_x, t_y):
        renderer.ts.T_m = PdfMatrix(1, 0, 0, 1, t_x, t_y)*renderer.ts.T_lm
        renderer.ts.reset_T_lm()

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
        renderer.ts.T_m = PdfMatrix(a, b, c, d, e, f)
        renderer.ts.reset_T_lm()

class Tstar(PdfOperation):
    opcode = 'T*'
    optype = PdfOperation.TEXT_POSITIONING

    @staticmethod
    def do_opcode(renderer):
        PdfOperation['Td'](0, renderer.ts.T_l)(renderer)