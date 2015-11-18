"""
PDF objects that represent the low-level document structure
"""

import re
from decimal   import Decimal

from .common       import PdfType
from ..exc         import PdfParseError

class PdfXref(PdfType):
    """Cross reference objects.  These forms the basic scaffolding of the PDF
    file, indicating where in the file each object is located."""
    LINE_PAT = re.compile(r'^(\d{10}) (\d{5}) (n|f)\s{0,2}$')

    def __init__(self, document, obj_no, offset, generation, in_use):
        super(PdfXref, self).__init__()
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
    def pdf_encode(self):
        fstr = '{0d10} {1d05} {2}\r\n'
        return fstr.format(self._offset, self._generation,
                           'n' if self._in_use else 'f').encode()

    def __str__(self):
        return '{:010d} {:010d} '.format(self._offset, self._generation)\
              +('n' if self._in_use else 'f')

    @classmethod
    def from_line(cls, document, obj_id, line):
        """Takes a line in an xref subsection and returns a PdfXref object.

        Arguments:
            document - The PdfDocument in which the line resides
            obj_id   - The xref line's object id based on the subsection header
            line     - The actual 18 to 20 byte line (possibly with whitespace)"""
        # TODO: consider using ReCacher here
        match = re.match(cls.LINE_PAT, line)
        if not match:
            raise PdfParseError('Invalid xref line')
        return cls(document, obj_id, int(match.group(1)), int(match.group(2)),
                   match.group(3) == 'n')

class PdfHeader(PdfType):
    """PDF version header.  Probably not super necessary to have."""
    def __init__(self, version, adobe_version=None):
        super(PdfHeader, self).__init__()
        self.version       = Decimal(version)
        self.adobe_version = Decimal(adobe_version) if adobe_version else None
    def __str__(self):
        vers = '%'
        if self.adobe_version:
            vers += '!PS-Adobe-'+str(self.adobe_version)+' '
        return vers+'PDF-'+str(self.version)
    def __bytes__(self):
        return bytes(str(self))
    def pdf_encode(self):
        return str(self).encode()

class PdfRaw(PdfType, bytes):
    """Raw PDF token"""
    def __new__(cls, *args, **kwargs):
        val =  bytes.__new__(cls, *args, **kwargs)
        val.__init__(*args, **kwargs)
        return val
    def __init__(self, *args, **kwargs):
        PdfType.__init__(self)
        bytes.__init__(self)
    def pdf_encode(self):
        return self

class PdfRawData(PdfType, bytes):
    """Raw, unparsed PDF data that should be treated as data, not a token."""
    def __new__(cls, *args, **kwargs):
        val =  bytes.__new__(cls, *args, **kwargs)
        val.__init__(*args, **kwargs)
        return val
    def __init__(self, *args, **kwargs):
        PdfType.__init__(self)
        bytes.__init__(self)
    def pdf_encode(self):
        return self
