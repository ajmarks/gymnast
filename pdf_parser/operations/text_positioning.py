import numpy as np
from ..pdf_operation import PdfOperation

class Td(PdfOperation):
    opcode = 'Td'
    optype = PdfOperation.TEXT_POSITIONING

    @staticmethod
    def do_opcode(renderer, t_x, t_y):
        renderer._T_m = np.matrix([[1,  0,  0],
                                   [0,  1,  0],
                                   [t_x,t_y,0]])*renderer._T_lm
        renderer.reset_T_lm()

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
        renderer._T_m = np.matrix([[a, b, 0],
                                   [c, d, 0],
                                   [e, f, 1]])
        renderer.reset_T_lm()

class Tstar(PdfOperation):
    opcode = 'T*'
    optype = PdfOperation.TEXT_POSITIONING

    @staticmethod
    def do_opcode(renderer):
        PdfOperation['Td'](0, renderer._T_l)(renderer)