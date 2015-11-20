from .pdf_element import PdfElement
from ..exc        import PdfError

class PdfCatalog(PdfElement):
    """PDF Root catalog element."""
    def __init__(self, obj, obj_key=None, document=None):
        if obj['Type'] != 'Catalog':
            raise PdfError('Type "Catalog" expected, got "{}"'.format(obj['Type']))
        if 'Pages' not in obj:
            raise PdfError('Catalog dictionaries must contain Pages')
        super(PdfCatalog, self).__init__(obj, obj_key, document)
