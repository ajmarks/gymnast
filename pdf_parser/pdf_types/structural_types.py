import re
from decimal   import Decimal

from .common       import PdfType
from .object_types import PdfObjectReference
from ..exc   import *

#PTVS nonsense
from builtins import *

class PdfXref(PdfType):
    def __init__(self, xrefs, offset):
        super().__init__()
        self._xrefs  = xrefs
        self._offset = offset

class PdfXrefLine(PdfType):
    LINE_PAT = re.compile(r'(\d{10}) (\d{5}) (n|f)$')

    def __init__(self, id, offset, generation, in_use):
        super().__init__()
        self._id         = id
        self._offset     = offset
        self._generation = generation
        self._in_use     = in_use

    def get_object(self, document):
        if self._in_use:
            return document.get_offset(self._offset)
        else:
            return None # TODO: implement free Xrefs

    def __str__(self):
        return '{:010d} {:010d} '.format(self._offset, self._generation)\
              +('n' if self._in_use else 'f')

    @staticmethod
    def from_line(id, line):
        # TODO: change to fullmatch once 3.4+ is standard
        match = re.match(PdfXrefLine.LINE_PAT, line)
        if not match:
            raise PdfParseError('Invalid xref line')
        return PdfXrefLine(id, int(match.group(1)), int(match.group(2)), 
                       True if match.group(3) == 'n' else False)


class PdfTrailer(PdfType, dict):
    #Type hints:
    if False:
        _root = PdfObjectReference()
        _info = PdfObjectReference()

    def __init__(self, trailer):
        PdfType.__init__(self)
        dict.__init__(self, trailer)
        #self._document = document
        #self._size     = trailer['Size']
        #self._root     = trailer['Root']
        #self._prev     = trailer.get('Prev')
        #self._encrypt  = trailer.get('Encrypt')
        #self._info     = trailer.get('Info', {})
        #self._id       = trailer.get('ID')
    @property
    def root(self):
        return self._root.object

class PdfStartXref(PdfType):
    def __init__(self, offset):
        super().__init__()
        self._offset = offset
    def lookup(self, document):
        return document.get_offset(self._offset)

class PdfHeader(PdfType):
    def __init__(self, version, adobe_version=None):
        super().__init__()
        self.version       = Decimal(version)
        self.adobe_version = Decimal(adobe_version) if adobe_version else None
    def __str__(self):
        vers = '%'
        if self.adobe_version:
            vers += '!PS-Adobe-'+str(self.adobe_version)+' '
        return vers+'PDF-'+str(self.version)
    def __bytes__(self):
        return bytes(str(self))

class PdfEOF(PdfType):
    """Singleton to mark ends of files"""
    def __new__(cls):
        return cls

class PdfRaw(PdfType, bytes):
    def __new__(cls, *args, **kwargs):
        val =  bytes.__new__(cls, *args, **kwargs)
        val.__init__(*args, **kwargs)
        return val
    def __init__(self, *args, **kwargs):
        PdfType.__init__(self)