"""
PdfTypes for indirect objects and references to them
"""

from .common         import PdfType
from .compound_types import PdfDict
from ..exc           import PdfError


class PdfIndirectObject(PdfType):
    """PDF indirect object definition"""
    def __init__(self, object_number, generation, obj, document):
        super(PdfIndirectObject, self).__init__()
        self._object_number = object_number
        self._generation    = generation
        self._object        = obj
        self._document      = document
        self._parsed_obj    = None

    @property
    def object_key(self):
        return (self._object_number, self._generation)
    @property
    def value(self):
        return self._object
    @property
    def parsed_object(self):
        """The PdfElement corresponding to the object

        TODO: Move most of this somewhere more sane."""
        from .. import pdf_elements
        obj_types = {'Page'          : pdf_elements.PdfPage,
                     'Pages'         : pdf_elements.PdfPageNode,
                     'Font'          : pdf_elements.PdfFont,
                     #'XObject'       : PdfXObject,   #TODO
                     'FontDescriptor': pdf_elements.FontDescriptor,
                     'Encoding'      : pdf_elements.FontEncoding,
                     #'ObjStm'        : ObjectStream, #TODO
                     'Catalog'       : pdf_elements.PdfCatalog
                    }
        if self._parsed_obj is not None:
            return self._parsed_obj
        val = self.value
        if isinstance(val, PdfDict):
            try:
                self._parsed_obj = obj_types[val['Type']]\
                                       .from_object(val, self.object_key, self._document)
                return self._parsed_obj
            except KeyError:
                return val
        return val

class PdfObjectReference(PdfType):
    """PDF indirect object reference"""
    def __init__(self, object_number, generation, document=None):
        super(PdfObjectReference, self).__init__()
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
        obj_id = (self._object_number, self._generation)
        return (document if document else self._document).get_object(*obj_id)

    @property
    def document(self):
        """Object reference's document"""
        return self._document

    @property
    def value(self):
        """Object referenced"""
        return self.get_object().value
    @property
    def parsed_object(self):
        """Object referenced, parsed"""
        return self.get_object().parsed_object

    def __str__(self):
        return 'PdfObjectReference({0}, {1})'.format(self._object_number,
                                                     self._generation)
    def __repr__(self):
        return str(self)
    def pdf_encode(self):
        return '{0} {1} R'.format(self._object_number,
                                  self._generation).encode()
