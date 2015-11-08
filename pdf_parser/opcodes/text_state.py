from ..pdf_oper import PdfOper

class Tc(PdfOper):
    opcode  = 'Tc'
    @classmethod
    def do_opcode(cls, char_spacing):
        cls.parser._T_c = char_spacing

class Tw(PdfOper):
    opcode  = 'Tw'
    @classmethod
    def do_opcode(cls, word_spacing):
        cls.parser._T_w = word_spacing

class Tz(PdfOper):
    opcode  = 'Tz'
    @classmethod
    def do_opcode(cls, scale):
        cls.parser._T_z = scale

class TL(PdfOper):
    opcode  = 'TL'
    @classmethod
    def do_opcode(cls, leading):
        cls.parser._T_l = leading

class Tf(PdfOper):
    opcode  = 'Tf'
    @classmethod
    def do_opcode(cls, font, size):
        cls.parser._T_f  = font
        cls.parser._T_fs = size
        
class Tr(PdfOper):
    opcode  = 'Tr'
    @classmethod
    def do_opcode(cls, render):
        cls.parser._T_mode = render

class Ts(PdfOper):
    opcode  = 'Ts'
    @classmethod
    def do_opcode(cls, rise):
        cls.parser._T_rise = rise