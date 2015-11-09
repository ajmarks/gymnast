import io
from datetime import datetime

from .exc           import *
from .pdf_types     import *
from .pdf_parser    import PdfParser
from .pdf_doc       import PdfDocument
from .pdf_operation import PdfOperation

class PdfPage(object):
    #Type hints
    if False:
        _parent        = PdfIndirectObject()
        _last_modified = datetime()
        _resources     = dict()

    def __init__(self, page):
        if isinstance(page, PdfObjectReference):
            page = page.value
        if page['Type'] != 'Page':
            raise PdfParseError('Page dicts must have Type = "Page"')
        self._page      = page
        self._parent    = page['Parent']
        self._resources = page.get('Resources')
        self._mediabox  = page.get('MediaBox')
        self._cropbox   = page.get('CropBox')
        self._contents  = ContentStream(page.get('Contents', []))
        self._rotate    = page.get('Rotate')

    @property
    def Parent(self):
        return self._parent.value
    @property
    def Resources(self):
        if self._resources: return self._resources
        else: return self.Parent.Resources
    @property
    def MediaBox(self):
        if self._mediabox: return self._mediabox
        else: return self.Parent.MediaBox
    @property
    def CropBox(self):
        if self._mediabox: return self._mediabox
        else: return self.Parent.CropBox
    @property
    def Contents(self):
        return self._contents
    @property
    def Rotate(self):
        if self._rotate: return self._rotate
        else: return self.Parent.Rotate
    def __getattr__(self, attr):
        val = self._page.get(attr)
        if isinstance(val, PdfObjectReference):
            return val.value
        else:
            return val

class ContentStream(object):
    def __init__(self, contents):
        if not isinstance(contents, list):
            contents = [contents]
        self._contents = contents
    @property
    def operations(self):
        for stream in self._contents:
            for oper in ContentStream._extract_stream_ops(stream.value):
                yield oper
    
    @staticmethod
    def _extract_stream_ops(stream):
        operands = []
        data = io.BufferedReader(io.BytesIO(stream.value))
        for op in PdfParser().iterparse(data):
            if isinstance(op, PdfRaw):
                yield PdfOperation[op](*operands)
                operands = []
            else:
                operands.append(op)