import numpy as np
import re

from .exc           import *
from .pdf_page      import PdfPage
from .pdf_operation import PdfOperation

#Nonsense to make PTVS happy
from builtins import *

class PdfRenderer(object):
    """PdfRenderer object.  PdfOperations act on this to produce a
    representation of the contents of the pdf document.  This class primarily
    serves to maintain the global state as the page is drawn."""
    
    #Type hints
    if False:
        _page = PdfPage()
    
    def __init__(self, page):
        self._Tm      = self.id_matrix
        self._Tlm     = self.id_matrix
        self._page    = page
        self._in_text = False
    
    def render(self):
        for op in self._page.Contents.operations:
            op(self)

    def _reset_Tm(self):
        """Reset the text matrix to the identity"""
        self._Tm  = self.id_matrix
    
    def _reset_Tlm(self):
        """Reset the line matrix to the general text matrix"""
        self._Tlm = np.copy(self._Tm)

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

class TextRenderer(PdfRenderer):
    pass