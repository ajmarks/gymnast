"""
Text state operations - Reference p. 398
"""

from ..pdf_operation import PdfOperation

def opcode_Tc(renderer, char_spacing):
    """Set the character spacing"""
    renderer.ts.T_c = char_spacing

def opcode_Tw(renderer, word_spacing):
    """Set the word spacing"""
    renderer.ts.T_w = word_spacing

def opcode_Tz(renderer, scale):
    """Set the text scale"""
    renderer.ts.T_z = scale

def opcode_TL(renderer, leading):
    """Set the leading space"""
    renderer.ts.T_l = leading

def opcode_Tf(renderer, font, size):
    """Set the font and font size"""
    renderer.ts.T_f  = font
    renderer.ts.T_fs = size

def opcode_Tr(renderer, render):
    """Set the render mode"""
    renderer.ts.T_mode = render

def opcode_Ts(renderer, rise):
    """Set the rise"""
    renderer.ts.T_rise = rise

PdfOperation.register('Tc', PdfOperation.TEXT_STATE, opcode_Tc)
PdfOperation.register('Tw', PdfOperation.TEXT_STATE, opcode_Tw)
PdfOperation.register('Tz', PdfOperation.TEXT_STATE, opcode_Tz)
PdfOperation.register('TL', PdfOperation.TEXT_STATE, opcode_TL)
PdfOperation.register('Tf', PdfOperation.TEXT_STATE, opcode_Tf)
PdfOperation.register('Tr', PdfOperation.TEXT_STATE, opcode_Tr)
PdfOperation.register('Ts', PdfOperation.TEXT_STATE, opcode_Ts)
