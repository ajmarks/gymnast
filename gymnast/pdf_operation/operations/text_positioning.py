"""
Text positioning operations - Reference p. 406
"""

from ..pdf_operation import PdfOperation
from ...pdf_matrix   import PdfMatrix

def opcode_Td(renderer, t_x, t_y):
    """Move to a new line, parallel to the current one, at text space
    coordinates offset from the start of the current line by (t_x, t_y)"""
    renderer.ts.m = PdfMatrix(1, 0, 0, 1, t_x, t_y)*renderer.ts.lm
    renderer.ts.reset_lm()

def opcode_TD(renderer, t_x, t_y):
    """Set the text-space leading, T_l, to -t_y and start a new line
    offset from the start of the current one by (t_x, t_y)"""
    PdfOperation['TL'](-t_y)(renderer)
    PdfOperation['Td'](t_x, t_y)(renderer)

def opcode_Tm(renderer, a, b, c, d, e, f):
    """Set the text matrix (T_m) and line matrix (T_lm)"""
    renderer.ts.m = PdfMatrix(a, b, c, d, e, f)
    renderer.ts.reset_lm()

def opcode_Tstar(renderer):
    """Move the start of new line, offset vertically by the text leading."""
    # N.B. The description on p. 406 is missing a minus sign.  As written, it
    # would move _up_ the page.
    PdfOperation['Td'](0, -renderer.ts.l)(renderer)

PdfOperation.register('Td', PdfOperation.TEXT_POSITIONING, opcode_Td)
PdfOperation.register('TD', PdfOperation.TEXT_POSITIONING, opcode_TD)
PdfOperation.register('Tm', PdfOperation.TEXT_POSITIONING, opcode_Tm)
PdfOperation.register('T*', PdfOperation.TEXT_POSITIONING, opcode_Tstar)
