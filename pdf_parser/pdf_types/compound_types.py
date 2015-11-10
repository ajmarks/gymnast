from .common import PdfType

class PdfArray(PdfType, list):
    def __init__(self, *args, **kwargs):
        PdfType.__init__(self)
        list.__init__(self, *args, **kwargs)

class PdfDict(PdfType, dict):
    def __init__(self, *args, **kwargs):
        PdfType.__init__(self)
        dict.__init__(self, *args, **kwargs)