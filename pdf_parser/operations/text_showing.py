import numbers

from ..pdf_operation import PdfOperation
from ..pdf_elements  import PdfFont
from ..misc          import classproperty
from ..exc           import *

#PTVS nonsense
from builtins import *

class TextOper(PdfOperation):
    optype = PdfOperation.TEXT_SHOWING

    #Type hints
    if False:
        parser.active_font = PdfFont()

    @staticmethod
    def get_glyph_width(renderer, glyph_code):
        return renderer.active_font.get_glyph_width(glyph_code)

    @staticmethod
    def get_char_code(renderer, glyph_name):
        return renderer.active_font.get_char_code(glyph_name)

    @classproperty
    def space_width(renderer):
        return renderer.active_font.space_width
    
class Tj(TextOper):
    opcode  = 'Tj'
    @staticmethod
    def do_opcode(renderer, string):
        for glyph in string:
            renderer.write_glyph(glyph)

class TJ(TextOper):
    opcode  = 'TJ'
    @staticmethod
    def do_opcode(renderer, args):
        for op in args:
            if isinstance(op, str):
                for glyph in op:
                    renderer.write_glyph(glyph)
            elif isinstance(op, numbers.Real):
                renderer.write_glyph(T_j=op)
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
