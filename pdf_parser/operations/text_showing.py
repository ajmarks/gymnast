import numpy as np

from ..pdf_operation import PdfOperation
from ..font          import PdfFont
from ..misc          import classproperty

#PTVS nonsense
from builtins import *

class TextOper(PdfOperation):
    is_text = True

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
    opcode  = b'Tj'
    @staticmethod
    def do_opcode(renderer, string):
        if not isinstance(string, bytes):
            glyphs = string.get_original_bytes()
        else:
            glyphs = string
        for g in glyphs:
            raise NotImplementedError

class TJ(TextOper):
    opcode  = b'TJ'
    @staticmethod
    def do_opcode(renderer, string):
        raise NotImplementedError

class Apostrophe(TextOper):
    opcode  = b"'"
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
