from .pdf_element import PdfElement
from ..exc        import *

#PTVS nonsense
from builtins import *

class PdfCatalog(PdfElement):
    def __init__(self, obj, obj_key=None):
        if obj['Type'] != 'Catalog':
            raise ValueError('Type "Catalog" expected, got "%s"'%obj['Type'])
        if 'Pages' not in obj:
            raise PdfError('Catalog dictionaries must contain Pages')
        super().__init__(obj, obj_key)