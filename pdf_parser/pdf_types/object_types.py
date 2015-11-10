from .common         import PdfType
from .compound_types import PdfDict
from ..exc           import *

#PTVS nonsense
from builtins import *


class PdfIndirectObject(PdfType):
    def __init__(self, object_number, generation, offset, object, document):
        super().__init__()
        self._object_number = object_number
        self._generation    = generation
        self._offset        = offset
        self._object        = object
        self._document      = document
        self._parsed_obj    = None

    @property
    def value(self):
        return self._object
    @property
    def parsed_object(self):
        from ..pdf_page import PdfPage, PdfPageNode
        from ..pdf_font     import PdfFont, FontDescriptor, FontEncoding
        from ..pdf_doc  import PdfCatalog
        obj_types = {'Page'          : PdfPage,
                     'Pages'         : PdfPageNode,
                     'Font'          : PdfFont,
                     #'XObject'       : PdfXObject,   #TODO
                     'FontDescriptor': FontDescriptor,
                     'Encoding'      : FontEncoding,
                     #'ObjStm'        : ObjectStream, #TODO
                     #'XRef'          : XRef
                     'Catalog'       : PdfCatalog
                    }
        if self._parsed_obj is not None:
            return self._parsed_obj
        val = self.value
        if isinstance(val, PdfDict):
            try:
                self._parsed_obj = obj_types[val['Type']].from_object(val)
                return self._parsed_obj
            except KeyError:
                return val
        return val

class PdfObjectReference(PdfType):
    def __init__(self, object_number, generation, document=None):
        super().__init__()
        self._object_number = object_number
        self._generation    = generation
        self._document      = document

        
        if   not isinstance(self._object_number, int) \
          or not isinstance(self._generation,    int) \
          or self._object_number <= 0 or self._generation < 0:
            raise ValueError('Invalid indirect object identifier')
       
    def get_object(self, document=None):
        if not document and not self._document:
            raise PdfError('Evaluating indirect references requires a document')
        id = (self._object_number, self._generation)
        return (document if document else self._document).indirect_objects[id]
    @property
    def value(self):
        return self.get_object().value
    @property
    def parsed_object(self):
        return self.get_object().parsed_object

    def __str__(self): 
        return 'PdfObjectReference(%d, %d)'%(self._object_number, self._generation)
    def __repr__(self): 
        return 'PdfObjectReference(%d, %d)'%(self._object_number, self._generation)