from .common import PdfType
from ..exc   import *

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

    @property
    def value(self):
        return self._object

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

    def __str__(self): 
        return 'PdfObjectReference(%d, %d)'%(self._object_number, self._generation)
    def __repr__(self): 
        return 'PdfObjectReference(%d, %d)'%(self._object_number, self._generation)