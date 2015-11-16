from ..pdf_operation import PdfOperation

class PdfTextStateOp(PdfOperation):
    optype = PdfOperation.TEXT_STATE

class Tc(PdfTextStateOp):
    @staticmethod
    def do_opcode(renderer, char_spacing):
        renderer.ts.ts.T_c = char_spacing

class Tw(PdfTextStateOp):
    opcode  = 'Tw'
    @staticmethod
    def do_opcode(renderer, word_spacing):
        renderer.ts.T_w = word_spacing

class Tz(PdfTextStateOp):
    opcode  = 'Tz'
    @staticmethod
    def do_opcode(renderer, scale):
        renderer.ts.T_z = scale

class TL(PdfTextStateOp):
    opcode  = 'TL'
    @staticmethod
    def do_opcode(renderer, leading):
        renderer.ts.T_l = leading

class Tf(PdfTextStateOp):
    opcode  = 'Tf'
    @staticmethod
    def do_opcode(renderer, font, size):
        renderer.ts.T_f  = font
        renderer.ts.T_fs = size

class Tr(PdfTextStateOp):
    opcode  = 'Tr'
    @staticmethod
    def do_opcode(renderer, render):
        renderer.ts.T_mode = render

class Ts(PdfTextStateOp):
    opcode  = 'Ts'
    @staticmethod
    def do_opcode(renderer, rise):
        renderer.ts.T_rise = rise
