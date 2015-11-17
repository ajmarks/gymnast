"""
PdfDict and PdfArray classes
"""

import six
from six.moves import UserList, UserDict
from .common import PdfType


class PdfArray(PdfType, UserList):
    """PDF list type"""
    def __init__(self, *args, **kwargs):
        PdfType.__init__(self)
        UserList.__init__(self, *args, **kwargs)
    def pdf_encode(self):
        return b'['+b' '.join(i.pdf_encode() for i in self)+b']'

class PdfDict(PdfType, UserDict):
    """PDF dict type"""
    def __init__(self, *args, **kwargs):
        PdfType.__init__(self)
        UserDict.__init__(self, *args, **kwargs)

    def __getattr__(self, name):
        try:
            return self[name].parsed_object
        except AttributeError:
            return self[name]
        except KeyError:
            raise AttributeError('Object has no attribute "%s"'%name)
    def pdf_encode(self):
        return b'<<'+b' '.join(k.pdf_encode()+b' '+v.pdf_encode()
                               for k, v in six.iteritems(self))+b'>>'
