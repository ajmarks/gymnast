"""
Text positioning operations - Reference p. 406
"""

from ..pdf_operation import PdfOperation
from ...pdf_matrix   import PdfMatrix

def opcode_Td(renderer, t_x, t_y):
    renderer.ts.T_m = PdfMatrix(1, 0, 0, 1, t_x, t_y)*renderer.ts.T_lm
    renderer.ts.reset_T_lm()

def opcode_TD(renderer, t_x, t_y):
    PdfOperation['TL'](-t_y)(renderer)
    PdfOperation['Td'](t_x, t_y)(renderer)

def opcode_Tm(renderer, a, b, c, d, e, f):
    renderer.ts.T_m = PdfMatrix(a, b, c, d, e, f)
    renderer.ts.reset_T_lm()

def opcode_Tstar(renderer):
    PdfOperation['Td'](0, renderer.ts.T_l)(renderer)

PdfOperation.register('Td', PdfOperation.TEXT_POSITIONING, opcode_Td)
PdfOperation.register('TD', PdfOperation.TEXT_POSITIONING, opcode_TD)
PdfOperation.register('Tm', PdfOperation.TEXT_POSITIONING, opcode_Tm)
PdfOperation.register('T*', PdfOperation.TEXT_POSITIONING, opcode_Tstar)
