"""
PdfDict and PdfArray classes
"""

import six
from .common import PdfType

class PdfArray(PdfType, list):
    """PDF list type"""
    def __init__(self, *args, **kwargs):
        PdfType.__init__(self)
        list.__init__(self, *args, **kwargs)
    def pdf_encode(self):
        return b'['+b' '.join(i.pdf_encode() for i in self)+b']'

class PdfDict(PdfType, dict):
    """PDF dict type"""
    def __init__(self, *args, **kwargs):
        PdfType.__init__(self)
        dict.__init__(self, *args, **kwargs)

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
