"""
Text Showing operations - Reference p. 407
"""
import numbers

from ..pdf_operation import PdfOperation
from ...exc          import PdfError

def opcode_Tj(renderer, string=b''):
    """Show a text string and move the position based on its length"""
    renderer.render_text(string)

def opcode_TJ(renderer, args=()):
    """Show one or more strings with individual positioning"""
    for op in args:
        if isinstance(op, str):
            renderer.render_text(op)
        elif isinstance(op, numbers.Real):
            renderer.move_text_cursor(op)
        else:
            raise PdfError('Invalid TJ operand')

def opcode_tick(renderer, string):
    """Move to the next line and show a text string"""
    PdfOperation['T*'](renderer)
    PdfOperation['Tj'](string)(renderer)

def opcode_quote(renderer, a_w, a_c, string):
    """Set the word and character spacing, move to a new line, and show a
    text string"""
    PdfOperation['Tw'](a_w)(renderer)
    PdfOperation['Tc'](a_c)(renderer)
    PdfOperation['\''](string)(renderer)

PdfOperation.register('Tj', PdfOperation.TEXT_SHOWING, opcode_Tj)
PdfOperation.register('TJ', PdfOperation.TEXT_SHOWING, opcode_TJ)
PdfOperation.register("'",  PdfOperation.TEXT_SHOWING, opcode_tick)
PdfOperation.register('"',  PdfOperation.TEXT_SHOWING, opcode_quote)
