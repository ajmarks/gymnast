import re
from decimal   import Decimal

from .common       import PdfType
from .object_types import PdfObjectReference
from ..exc         import *

#PTVS nonsense
from builtins import *

class PdfXref(PdfType):
    LINE_PAT = re.compile(r'^(\d{10}) (\d{5}) (n|f)\s{0,2}$')

    #IDE type hints
    if False:
        from ..pdf_doc     import PdfDocument
        _id         = 0
        _offset     = 0
        _generation = 0
        _in_use     = True
        _document   = PdfDocument()

    def __init__(self, document, obj_no, offset, generation, in_use):
        super().__init__()
        self._obj_no     = obj_no
        self._offset     = offset
        self._generation = generation
        self._in_use     = in_use
        self._document   = document
    @property
    def key(self):
        return (self._obj_no, self._generation)

    @property
    def value(self):
        return self.get_object()

    def get_object(self):
        """Return the object referenced by this Xref.  If it's already parsed 
        in the document, great, otherwise parse it."""
        if self._in_use:
            objs = self._document.indirect_objects
            try:
                return objs[self.key]
            except KeyError:
                self._document.parse_object(self._offset)
                return objs[self.key]
        else:
            return None # TODO: implement free Xrefs

    def __str__(self):
        return '{:010d} {:010d} '.format(self._offset, self._generation)\
              +('n' if self._in_use else 'f')

    @classmethod
    def from_line(cls, document, id, line):
        """Takes a line in an xref subsection and returns a PdfXref object.

        Arguments:
            document - The PdfDocument in which the line resides
            id       - The xref line's object id based on the subsection header
            line     - The actual 18 to 20 byte line (possibly with whitespace)"""
        # TODO: consider using ReCacher here
        match = re.match(cls.LINE_PAT, line) 
        if not match:
            raise PdfParseError('Invalid xref line')
        return cls(document, id, int(match.group(1)), int(match.group(2)), 
                   match.group(3) == 'n')


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
        return self._root.value

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

class PdfRawData(PdfType, bytes):
    def __new__(cls, *args, **kwargs):
        val =  bytes.__new__(cls, *args, **kwargs)
        val.__init__(*args, **kwargs)
        return val
    def __init__(self, *args, **kwargs):
        PdfType.__init__(self)