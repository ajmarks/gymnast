import io
import numbers
import re
from decimal   import Decimal
from functools import partial, reduce

from .exc           import *
from .misc          import iterbytes, MetaNonelike, classproperty
from .stream_filter import FilterExecutor


#PTVS nonsense
from builtins import *

LINEBREAKS = set([b'\r', b'\n', b'\r\n'])
WHITESPACE = LINEBREAKS.union([b'\x00', b'\x09', b'\x0A', b'\x20'])

class PdfType(object):
    """Abstract base class for PDF objects"""
    def pdf_encode(self):
        """Translate the object into bytes in PDF format"""
        raise NotImplementedError
    @property
    def value(self):
        """Objects, references, and such will override this in clever
        ways."""
        return self








#These may seem unecessary, but it lets us assume that every pdf element
#has a .value property so we needn't worry about constantly trying to 
#deference.  It will also help when we implement a PDF writer, allowing us
#to simply call obj.pdf_encode()



#class PdfBoolean(PdfSimpleType):
#    """We'll probably kill this class later"""
#    _instances = None
#    def __new__(cls, val):
#        if PdfBoolean._instances is None:
#            PdfBoolean._instances = (super(PdfBoolean, cls).__new__(cls),
#                                     super(PdfBoolean, cls).__new__(cls))
#            PdfBoolean._instances[0].__init__(val)
#            PdfBoolean._instances[1].__init__(val)
#            PdfBoolean._instances[0]._bool = False
#            PdfBoolean._instances[1]._bool = True
#        if   val in (b'true', 'true') or val is True:
#            return PdfBoolean._instances[1]
#        elif val in (b'false', 'false') or val is False:
#            return PdfBoolean._instances[0]
#        else: raise ValueError('PdfBoolean value must be "true" or "false"')
#    
#    def __init__(self, val):
#        super().__init__()
#
#    def __str__(self):       return 'true' if self else 'false'
#    def __repr__(self):      return 'PdfBoolean(%s)'%str(self)
#    # Guido has decreed that we can't inherit from bool, so we need
#    # to do all of this junk manually
#    def __lt__(self, other): return self._bool.__lt__(other)
#    def __le__(self, other): return self._bool.__le__(other)
#    def __eq__(self, other): return self._bool.__eq__(other)
#    def __ne__(self, other): return self._bool.__ne__(other)
#    def __gt__(self, other): return self._bool.__gt__(other)
#    def __ge__(self, other): return self._bool.__ge__(other)
#    def __bool__(self):      return self._bool
#    def __bytes__(self):     return self._bool.__bytes()
#    def __hash__(self):      return self._bool.__hash__()
#
#class PdfNumeric(PdfSimpleType):
#    """Base class for PdfNumeric types.  Numbers can be initialized as
#    PdfNumeric(12) or PdfNumeric('-12.43'), and the appropriate subtype
#    will be returned"""
#    def __new__(cls, val):
#        if isinstance(val, numbers.Integral):
#            return PdfInt(val)
#        elif isinstance(val, numbers.Real):
#            return PdfReal(val)
#        try:
#            return PdfInt(val)
#        except ValueError:
#            return PdfReal(val)
#
#class PdfInt(PdfNumeric, int):
#    def __new__(cls, val):
#        return int.__new__(cls, val)
#
#class PdfReal(PdfNumeric, float):
#    def __new__(cls, val):
#        return float.__new__(cls, val)
#        
#    @staticmethod
#    def find_string_end(data):
#        """Given bytes beginning with a name string, returns the end
#        of the slice containing the string data"""
#        for i in range(1, len(data)):
#            if data[i:i+1] in WHITESPACE:
#                return i
#        raise PdfParseError('Name not terminated')