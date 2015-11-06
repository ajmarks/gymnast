import io

try:
    from .exc       import *
    from .pdf_types import PdfObjectReference, PdfComment, PdfLiteralString, \
                           PdfHexString, PdfStream, PdfXref, PdfTrailer
except SystemError as e:
    if 'not loaded, cannot perform relative import' not in e.args[0]:
        raise
    from exc       import *
    from pdf_types import PdfObjectReference, PdfComment, PdfLiteralString, \
                          PdfHexString, PdfStream, PdfXref, PdfTrailer


#PTVS nonsense
from builtins import *

class PdfDocument(object):
    def __init__(self, header, elements=[], indirect_objects={}):
        self._header      = header
        self._elements    = elements
        self._ind_objects = indirect_objects
        self._offsets     = {i._offset:i for i in indirect_objects.values()}

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