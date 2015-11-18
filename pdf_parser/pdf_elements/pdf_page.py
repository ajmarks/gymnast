"""
PDF Document Page and Page Node elements
"""

import six

from .pdf_element    import PdfElement
from ..exc           import PdfParseError, PdfError
from ..pdf_types     import PdfType, PdfRaw, PdfArray
from ..pdf_parser    import PdfParser
from ..pdf_operation import PdfOperation

def parse_page(obj):
    """Parse a page like object into the appropraite subclass"""
    obj = obj.value
    if   obj['Type'] == 'Pages':
        return PdfPageNode(obj)
    elif obj['Type'] == 'Page':
        return PdfPage(obj)

class PdfPageResources(PdfElement):
    """Resources dict on page objects.  Technically, it's not a PDF
    object type, but this lets us re-use a lot of code."""
    pass

class PdfAbstractPage(PdfElement):
    """Base class for PDF Pages and Page Nodes."""
    def __init__(self, page, obj_key=None):
        """Create a new or node with properly inherited properties
        where applicable"""
        #Common and inheritable properties
        super(PdfAbstractPage, self).__init__(page, obj_key)
        self._resources = page.get('Resources')
        self._mediabox  = page.get('MediaBox')
        self._cropbox   = page.get('CropBox')
        self._rotate    = page.get('Rotate')
        self._fonts     = None

    @property
    def Resources(self):
        """Page resources, most notably fonts"""
        if   self._resources: return PdfPageResources.from_object(self._resources)
        elif self._parent:    return self.Parent.Resources
        else: raise PdfError('Resource dictionary not found')
    @property
    def MediaBox(self):
        """Size of the media"""
        if self._mediabox:  return self._mediabox.value
        elif self._parent: return self.Parent.MediaBox
        else: raise PdfError('MediaBox not found')
    @property
    def CropBox(self):
        """Visible area of the media"""
        box = self.raw_cropbox
        return box if box else self.MediaBox
    @property
    def raw_cropbox(self):
        """Inherited CropBox with no default value"""
        if self._cropbox:  return self._cropbox.value
        elif self._parent: return self.Parent.raw_cropbox
        else:              return None
    @property
    def Rotate(self):
        """Rotation angle.  Should be an integer multiple of 90."""
        if self._rotate:   return self._rotate
        elif self._parent: return self.Parent.Rotate
        else: return 0
    @property
    def Fonts(self):
        """Neatly processed dict of the page's fonts.  Serves as a shortcut
        to .Resources.Font"""
        if self._fonts is None:
            self._fonts = {k: v.parsed_object
                           for k,v in six.iteritems(self.Resources.Font)}
        return self._fonts

class PdfPageNode(PdfAbstractPage):
    """Page node object"""
    def __init__(self, node, obj_key=None):
        node = node.value
        if node['Type'] != 'Pages':
            raise ValueError('Type "Pages" expected, got "{}"'.format(node['Type']))
        super(PdfPageNode, self).__init__(node, obj_key)
    @property
    def Kids(self):
        """Child pages and nodes"""
        return [p.parsed_object for p in self._object['Kids'].value]
    #def __getitem__(self, key):
    #    return self._kids[key]
    #def __contains__(self, item):
    #    return self._kids.__contains__(item)
    #def __setitem__(self, key, value):
    #    return self._kids.__setitem__(key, value)
    #def __delitem__(self, key, value):
    #    return self._kids.__delitem__(key)
    #def __iter__(self):
    #    return self._kids.__iter__()
    #def __reversed__(self):
    #    return self._kids.__reversed__()
    #@property
    #def Count(self):
    #    return len(self._kids)
    #def __str__(self):
    #    return 'PdfPageNode - %d children'%self.Count

class PdfPage(PdfAbstractPage):
    """Abstract class for pages and page nodes"""

    def __init__(self, page, obj_key=None):
        page = page.value
        if page['Type'] != 'Page':
            raise PdfParseError('Page dicts must have Type = "Page"')
        super(PdfPage, self).__init__(page, obj_key)
        self._contents  = ContentStream(page.get('Contents', []))
        self._fonts     = None # Load these when they're called

    @property
    def Contents(self):
        return self._contents
    def __getattr__(self, name):
        #Default values
        defaults = {'BleedBox': 'MediaBox',
                    'TrimBox' : 'CropBox',
                    'ArtBox'  : 'CropBox'}
        try:
            val = super(PdfPage, self).__getattr__(name)
        except KeyError:
            try:
                val = self.__dict__[defaults[name]]
            except KeyError:
                raise AttributeError('Object has no attribute "{}"'.format(name))
        if isinstance(val, PdfType):
            return val.parsed_object
        else:
            return val

class ContentStream(object):
    """A page's content stream"""
    def __init__(self, contents):
        if not isinstance(contents, PdfArray):
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
        for op in PdfParser().iterparse(stream.value.data):
            if isinstance(op, PdfRaw):
                yield PdfOperation[op](*operands)
                operands = []
            else:
                operands.append(op)
