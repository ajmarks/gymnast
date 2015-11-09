from .exc        import *
from .pdf_types  import *
from .pdf_parser import PdfParser

#PTVS nonsense
from builtins import *

class PdfDocument(object):
    def __init__(self, file):
        self._file = file

    def parse(self):
        parser = PdfParser(self)
        
        header, ind_objects, doc_objects, xrefs = parser.parse(self._file)
        self._header      = header
        self._elements    = doc_objects
        self._ind_objects = ind_objects
        self._offsets     =  {i._offset:i for i in ind_objects.values()}
        self._offsets.update({i._offset:i for i in xrefs})
        print(None)

    @property
    def indirect_objects(self):
        return self._ind_objects
    def get_object(self, object_number, generation):
        try:
            return self._ind_objects[(object_number, generation)].object
        except KeyError:
            raise PdfError('No object exists with that number and generation')
    def get_offset(self, offset):
        try:
            return self._offsets[offset]
        except KeyError:
            raise PdfError('No object exists at that offset')