from .common import PdfType
from ..misc  import MetaNonelike, classproperty

class PdfNull(PdfType, metaclass=MetaNonelike):
    """None-like singleton representing PDF's equivalent of None."""
    @classproperty
    def value(cls):
        return cls
    def pdf_encode(self):
        return b'null'

class PdfInt(PdfType, int):
    """Pdf int type"""
    def __new__(cls, val):
        return int.__new__(cls, val)
    def __getattr__(self, name):
        return int.__getattribute__(name)
    def pdf_encode(self):
        return bytes(str(self))

class PdfReal(PdfType, float):
    """PDF real type
    TODO: Decide if this should be a Decimal instead"""
    def __new__(cls, val):
        return float.__new__(cls, val)
    def __getattr__(self, name):
        return float.__getattribute__(name)
    def pdf_encode(self):
        return bytes(str(self))

class PdfBool(PdfType):
    """TODO: This"""
    def pdf_encode(self):
        return b'true' if self else b'false'
    
