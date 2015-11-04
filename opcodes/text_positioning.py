import numpy as np
from ..pdf_opcodes import PdfOper

class Td(PdfOper):
    opcode  = 'Td'
    @classmethod
    def do_opcode(cls, t_x, t_y):
        cls.parser._T_m = np.matrix([[1,  0,  0],
                                     [0,  1,  0],
                                     [t_x,t_y,0]])*cls.parser._T_lm
        cls.parser.reset_T_lm()

class TD(PdfOper):
    opcode  = 'TD'
    @classmethod
    def do_opcode(cls, t_x, t_y):
        cls.opcodes['TL'](-t_y)
        cls.opcodes['Td'](t_x, t_y)

class Tm(PdfOper):
    opcode  = 'Tm'
    @classmethod
    def do_opcode(cls, a, b, c, d, e, f):
        cls.parser._T_m = np.matrix([[a, b, 0],
                                     [c, d, 0],
                                     [e, f, 1]])
        cls.parser.reset_T_lm()

class Tstar(PdfOper):
    opcode  = 'T*'
    @classmethod
    def do_opcode(cls):
        cls.opcodes['Td'](0, cls.parser._T_l)