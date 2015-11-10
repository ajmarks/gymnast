#PTVS nonsense
from builtins import *

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
