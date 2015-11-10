from .common import PdfType
from ..misc  import MetaNonelike, classproperty

class PdfNull(PdfType, metaclass=MetaNonelike):
    """None-like singleton representing PDF's equivalent of None."""
    @classproperty
    def value(cls):
        return cls

class PdfInt(PdfType, int):
    def __new__(cls, val):
        return int.__new__(cls, val)
    def __getattr__(self, name): 
        return int.__getattribute__(name)

class PdfReal(PdfType, float):
    """TODO: Decide if this should be a Decimal instead"""
    def __new__(cls, val):
        return float.__new__(cls, val)
    def __getattr__(self, name): 
        return float.__getattribute__(name)

class PdfBool(PdfType):
    """TODO: This"""
    pass