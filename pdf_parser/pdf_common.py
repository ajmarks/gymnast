from .exc       import *
from .pdf_types import PdfType

#PTVS nonsense
from builtins import *

class PdfObject(object):
    _object = None
    @classmethod
    def from_object(cls, obj):
        return cls(obj.value)
    def __init__(self, obj):
        self._object = obj.value
    def __getitem__(self, key):
        val = self._object[key]
        if isinstance(val, PdfType):
            return val.parsed_object
        else:
            return val
    def __getattr__(self, key):
        try:
            val = self._object[key]
        except KeyError:
            raise AttributeError('Object has no attribute "%s"'%key)
        if isinstance(val, PdfType):
            return val.parsed_object
        else:
            return val
    @property
    def parsed_object(self):
        return self
    def __repr__(self):
        return str(self._object)