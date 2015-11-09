import PyPDF2
import numpy as np
import re
from PyPDF2.pdf  import ContentStream

from .exc      import *
from .pdf_oper import OpcodeExecutor

#Nonsense to make PTVS happy
from builtins import *


class TextRenderer(object):
    def __init__(self):
        self._Tm      = self.id_matrix
        self._Tlm     = self.id_matrix
        self._in_text = False
        self._opcodes = OpcodeExecutor(self)
    
    def _reset_Tm(self):
        """Reset the text matrix to the identity"""
        self._Tm  = self.id_matrix
    def _reset_Tlm(self):
        """Reset the line matrix to the general text matrix"""
        self._Tlm = np.copy(self._Tm)
    
    def parse(self, page, tab_size=4.0, line_size=1.1):
        """Parse the page, replacing blanks of tab_size spaces with tabs"""
        
        self._tab_size  = tab_size
        self._line_size = line_size
        content = page.getContents().getObject()
        if not isinstance(content, ContentStream):
            content = ContentStream(content, page.pdf)
            
        self._words = []
        self._fonts = {k: PdfFont(v) for
                         k,v in page['Resources']['Font'].items()}
        
        for args, oper in content.operations:
            self._opcodes[oper](*args)

    @property
    def id_matrix(self):
        return np.matrix([[1, 0, 0],
                          [0, 1, 0],
                          [0, 0, 1]])

    @property 
    def active_font(self):
        if self._T_f:
            return self._fonts[self._T_f]
        else:
            return None
    
    @property
    def _space_width(self):
        """The width of a space in the current font"""
        return self.active_font['Widths'][ord(' ')-self.active_font['FirstChar']]
    
    @property
    def _cap_height(self):
        """The height of a capital letter in the current font"""
        return self.active_font['FontDescriptor']['CapHeight']
    
    def _get_glyph_width(self, glyph):
        w_idx = ord(glyph)-self._fonts[self._T_f]['FirstChar']
        return self._fonts[self._T_f]['Widths'][w_idx]
    
    def _write_glyph(self, glyph=None, T_j=0.0):
        """rite the glyph to the text output and update T_m.  See pp.409-10.
        Returns the change in cursor position."""
        if glyph:
            self._text += glyph
            w0 = self._get_glyph_width(glyph)
        else:
            w0 = 0.0
        
        tx = ((w0-T_j/1000.0)*self._T_fs+self._T_c+self._T_w)*self._T_h
        return self._set_Tm(np.matrix([[1, 0, 0],
                                       [0, 1, 0],
                                       [tx,0, 1]])*self._Tm)