from .exc          import *
from .pdf_types    import *
from .pdf_parser   import PdfParser
from .pdf_elements import PdfCatalog, PdfPageNode

#PTVS nonsense
from builtins import *

class PdfDocument(object):
    def __init__(self, file):
        self._file = file

    def parse(self):
        self._pages = None

        parser = PdfParser(self)
        
        header, ind_objects, doc_objects, xrefs = parser.parse(self._file)
        self._version     = header.version
        self._ind_objects = ind_objects
        self._offsets     =  {i._offset:i for i in ind_objects.values()}
        self._offsets.update({i._offset:i for i in xrefs})
        self._build_doc(self._get_trailer(doc_objects))
        return self
   
    def _get_trailer(self, elements):
        final_trailer = {}
        for e in elements:
            if isinstance(e, PdfTrailer):
                final_trailer.update(e)
        return final_trailer

    def _build_doc(self, trailer):
        try:
            self._root    = trailer['Root'].parsed_object
        except KeyError:
            raise PdfError('PDF file lacks a root element')
        self._version = trailer.get('Version', self._version)
        try:
            self._info = trailer['Info'].parsed_object
        except KeyError:
            self._info = None
        self._size = trailer['Size']
        try:
            self._encrypt = trailer['Encrypt'].parsed_object
        except KeyError:
            self._encrypt = None
        try:
            self._id = trailer['ID'].value
        except KeyError:
            self._id = None

    @property
    def Root(self):
        return self._root
    @property
    def Info(self):
        return self._info
    @property
    def Size(self):
        return self._size
    @property
    def Encrypt(self):
        return self._encrypt
    @property
    def ID(self):
        return self._id

    @property
    def Pages(self):
        """Alias for self.Root.Pages.Kids"""
        if self._pages is None:
            self._pages = self.Root.Pages.Kids
        return self._pages

    @property
    def indirect_objects(self):
        return self._ind_objects
    def get_object(self, object_number, generation):
        try:
            return self._ind_objects[(object_number, generation)].object
        except KeyError:
            raise PdfError('No object exists with that number and generation')
    def get_offset(self, offset):
        try:
            return self._offsets[offset]
        except KeyError:
            raise PdfError('No object exists at that offset')

class PdfElementList(object):
    def __init__(self, *args, **kwargs):
        self._list = list(*args, **kwargs)
    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self._get_value(i) for i in self._list(key)]
        else:
            return self._get_value(self._list[key])
    def __delitem__(self, key):
        self._list.__delitem__(key)
    def __len__(self):
        return self._list.__len__()
    def __str__(self):
        return str(self._list)
    def __repr__(self):
        return repr(self._list)
    
    @staticmethod
    def _get_value(item):
        if isinstance(item, PdfObjectReference):
            return item.value
        else:
            return item