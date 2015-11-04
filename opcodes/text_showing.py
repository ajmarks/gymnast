import numpy as np

from ..pdf_opcodes   import PdfOper
from ..pdf_extractor import TextParser
from ..pdf_font      import PdfFont
from ..misc          import classproperty

from builtins import *

class TextOper(PdfOper):
    is_text = True

    #Type hints
    if False:
        parser.active_font = PdfFont()

    @classmethod
    def get_glyph_width(cls, glyph_code):
        return cls.parser.active_font.get_glyph_width(glyph_code)

    @classmethod
    def get_char_code(cls, glyph_name):
        return cls.parser.active_font.get_char_code(glyph_name)

    @classproperty
    def space_width(cls):
        return cls.parser.active_font.space_width

class Tj(TextOper):
    opcode  = b'Tj'
    @classmethod
    def do_opcode(cls, string):
        if not isinstance(string, bytes):
            glyphs = string.get_original_bytes()
        else:
            glyphs = string
        for g in glyphs:
            raise NotImplementedError

class TJ(TextOper):
    opcode  = b'TJ'
    @classmethod
    def do_opcode(cls, string):
        raise NotImplementedError

class Apostrophe(TextOper):
    opcode  = b"'"
    @classmethod
    def do_opcode(cls, string):
        cls.opcodes['T*']()
        cls.opcodes['Tj'](string)

class Quote(TextOper):
    opcode  = b'"'
    @classmethod
    def do_opcode(cls, a_w, a_c, string):
        cls.opcodes['Tw'](a_w)
        cls.opcodes['Tc'](a_c)
        cls.opcodes['\''](string)
