import numbers

from ..pdf_operation import PdfOperation
from ...exc           import *
from ...misc          import classproperty
from ...pdf_elements  import PdfFont


class TextOper(PdfOperation):
    optype = PdfOperation.TEXT_SHOWING

class Tj(TextOper):
    opcode  = 'Tj'
    @staticmethod
    def do_opcode(renderer, string):
        renderer.render_text(string)

class TJ(TextOper):
    opcode  = 'TJ'
    @staticmethod
    def do_opcode(renderer, args):
        x=1
        for op in args:
            if isinstance(op, str):
                renderer.render_text(op, True)
            elif isinstance(op, numbers.Real):
                renderer.move_text_cursor(op)
            else:
                raise PdfError('Invalid TJ operand')

class Apostrophe(TextOper):
    opcode  = "'"
    @staticmethod
    def do_opcode(renderer, string):
        PdfOperation['T*'](renderer)
        PdfOperation['Tj'](string)(renderer)

class Quote(TextOper):
    opcode  = b'"'
    @staticmethod
    def do_opcode(renderer, a_w, a_c, string):
        PdfOperation['Tw'](a_w)(renderer)
        PdfOperation['Tc'](a_c)(renderer)
        PdfOperation['\''](string)(renderer)
