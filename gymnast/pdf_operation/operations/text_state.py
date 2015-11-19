"""
Text state operations - Reference p. 397-98.

Also see the comments in renderer.renderer_states.TextState
"""

from ..pdf_operation import PdfOperation

def opcode_Tc(renderer, char_spacing):
    """Set the character spacing"""
    renderer.ts.c = char_spacing

def opcode_Tw(renderer, word_spacing):
    """Set the word spacing"""
    renderer.ts.w = word_spacing

def opcode_Tz(renderer, scale):
    """Set the horizontal text scale"""
    renderer.ts.h = scale/100.0

def opcode_TL(renderer, leading):
    """Set the leading space"""
    renderer.ts.l = leading

def opcode_Tf(renderer, font, size):
    """Set the font and font size"""
    renderer.ts.f  = font
    renderer.ts.fs = size

def opcode_Tr(renderer, render):
    """Set the render mode"""
    renderer.ts.mode = render

def opcode_Ts(renderer, rise):
    """Set the rise"""
    renderer.ts.rise = rise

PdfOperation.register('Tc', PdfOperation.TEXT_STATE, opcode_Tc)
PdfOperation.register('Tw', PdfOperation.TEXT_STATE, opcode_Tw)
PdfOperation.register('Tz', PdfOperation.TEXT_STATE, opcode_Tz)
PdfOperation.register('TL', PdfOperation.TEXT_STATE, opcode_TL)
PdfOperation.register('Tf', PdfOperation.TEXT_STATE, opcode_Tf)
PdfOperation.register('Tr', PdfOperation.TEXT_STATE, opcode_Tr)
PdfOperation.register('Ts', PdfOperation.TEXT_STATE, opcode_Ts)
