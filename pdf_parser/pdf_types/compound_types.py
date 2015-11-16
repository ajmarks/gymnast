from .common import PdfType

class PdfArray(PdfType, list):
    def __init__(self, *args, **kwargs):
        PdfType.__init__(self)
        list.__init__(self, *args, **kwargs)

class PdfDict(PdfType, dict):
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
