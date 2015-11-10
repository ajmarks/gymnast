import io
from datetime import datetime

from .exc           import *
from .pdf_common    import PdfObject
from .pdf_types     import *
from .pdf_parser    import PdfParser
from .pdf_operation import PdfOperation

def parse_page(obj):
    obj = obj.value
    if   obj['Type'] == 'Pages':
        return PdfPageNode(obj)
    elif obj['Type'] == 'Page':
        return PdfPage(obj)

class PdfAbstractPage(PdfObject):
    """Base class for PDF Pages and Page Nodes."""
    def __init__(self, page):
        #Common and inheritable properties
        super().__init__(page)
        self._resources = page.get('Resources')
        self._mediabox  = page.get('MediaBox')
        self._cropbox   = page.get('CropBox')
        self._rotate    = page.get('Rotate')
        self._fonts     = None

    @property
    def Resources(self):
        if   self._resources: return self._resources.value
        elif self._parent:    return self.Parent.Resources
        else: raise PdfError('Resource dictionary not found')
    @property
    def MediaBox(self):
        if self._mediabox:  return self._mediabox.value
        elif self._parent: return self.Parent.MediaBox
        else: raise PdfError('MediaBox not found')
    @property
    def CropBox(self):
        box = self._get_cropbox()
        return box if box else self.MediaBox    
    def _get_cropbox(self):
        if self._cropbox:  return self._cropbox.value
        elif self._parent: return self.Parent._get_cropbox()
        else:              return None
    @property
    def Rotate(self):
        if self._rotate:   return self._rotate
        elif self._parent: return self.Parent.Rotate
        else: return 0
    @property
    def Fonts(self):
        if self._fonts is None:
            self._fonts = {k: v.parsed_object 
                           for k,v in self._object.get('Resources', {})\
                                          .get('Font',{}).items()}
        return self._fonts

class PdfPageNode(PdfAbstractPage):
    """Page node object"""
    def __init__(self, node):
        node = node.value
        if node['Type'] != 'Pages':
            raise ValueError('Type "Pages" expected, got "%s"'%node['Type'])
        super().__init__(node)
        self._kids = [p.parsed_object for p in node['Kids'].value]

    def __getitem__(self, key):
        return self._kids[key]
    def __contains__(self, item):
        return self._kids.__contains__(item)
    def __setitem__(self, key, value):
        return self._kids.__setitem__(key, value)
    def __delitem__(self, key, value):
        return self._kids.__delitem__(key)
    def __iter__(selfe):
        return self._kids.__iter__()
    def __reversed__(self):
        return self._kids.__reversed__()
    @property
    def Count(self):
        return len(self._kids)
    @property
    def Kids(self):
        return self._kids
    def __str__(self):
        return 'PdfPageNode - %d children'%self.Count
    


class PdfPage(PdfAbstractPage):
    #Type hints
    if False:
        _parent        = PdfIndirectObject()
        _last_modified = datetime()
        _resources     = dict()

    def __init__(self, page):
        page = page.value
        if page['Type'] != 'Page':
            raise PdfParseError('Page dicts must have Type = "Page"')
        super().__init__(page)
        self._page      = page
        self._contents  = ContentStream(page.get('Contents', []))
        self._fonts     = None # Load these when they're called

    @property
    def Contents(self):
        return self._contents
    # Default values.
    # TODO: make this more concise, probably by folding it into 
    # __getattr__
    def __getattr__(self, attr):
        #Default values
        defaults = {'BleedBox': self.MediaBox,
                    'TrimBox' : self.CropBox,
                    'ArtBox'  : self.CropBox}
        try:
            val = super().__getitem__(attr)
        except KeyError:
            return defaults[attr]
        if isinstance(val, PdfObjectReference):
            return val.parsed_object
        else:
            return val

class ContentStream(PdfObject):
    """A page's content stream"""
    def __init__(self, contents):
        if not isinstance(contents, list):
            contents = [contents]
        self._contents = contents
    @property
    def operations(self):
        """Iterator over the various PDF operations in the content stream.
        Each element is an instance of a subclass of PdfOperation, which can 
        then be rendered by the page by calling e.g. next(operations)(renderer)
        where renderer is a PdfRenderer object."""
        for stream in self._contents:
            for oper in self._extract_stream_ops(stream):
                yield oper
    
    @staticmethod
    def _extract_stream_ops(stream):
        operands = []
        data = io.BufferedReader(io.BytesIO(stream.value.data))
        for op in PdfParser().iterparse(data):
            if isinstance(op, PdfRaw):
                yield PdfOperation[op](*operands)
                operands = []
            else:
                operands.append(op)