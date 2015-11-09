from ..pdf_operation import PdfOperation

class Tc(PdfOperation):
    opcode  = 'Tc'
    @staticmethod
    def do_opcode(renderer, char_spacing):
        renderer._T_c = char_spacing

class Tw(PdfOperation):
    opcode  = 'Tw'
    @staticmethod
    def do_opcode(renderer, word_spacing):
        renderer._T_w = word_spacing

class Tz(PdfOperation):
    opcode  = 'Tz'
    @staticmethod
    def do_opcode(renderer, scale):
        renderer._T_z = scale

class TL(PdfOperation):
    opcode  = 'TL'
    @staticmethod
    def do_opcode(renderer, leading):
        renderer._T_l = leading

class Tf(PdfOperation):
    opcode  = 'Tf'
    @staticmethod
    def do_opcode(renderer, font, size):
        renderer._T_f  = font
        renderer._T_fs = size
        
class Tr(PdfOperation):
    opcode  = 'Tr'
    @staticmethod
    def do_opcode(renderer, render):
        renderer._T_mode = render

class Ts(PdfOperation):
    opcode  = 'Ts'
    @staticmethod
    def do_opcode(renderer, rise):
        renderer._T_rise = rise