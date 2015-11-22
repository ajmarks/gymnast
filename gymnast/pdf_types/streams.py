"""
PDF stream objects - Reference p. 60
"""

import io
from functools import partial, reduce

from .common       import PdfType
from .object_types import PdfIndirectObject
from ..filters import StreamFilter
from ..misc    import ensure_list

class PdfStream(PdfType):
    """PDF stream type"""
    def __init__(self, header, data, document=None):
        super(PdfStream, self).__init__()
        self._header   = header
        self._objects  = None
        self._document = document

        # This is obnoxious, but the PDF standard allows the stream header to
        # to specify another file with the data, ignoring the stream data.
        # Also, for some reason, some header keys change when that happens.
        try:
            with open(header['F'], 'rb') as f:
                data = f.read()
        except KeyError:
            self._data     = data
            self._filedata = False
        else:
            self._filedata = True

        if self._filter_key in header:
            self._decoded  = False
        else:
            self._decoded  = True
            self._decoded_data = self._data
    @property
    def header(self):
        """Stream header"""
        return self._header
    @property
    def _filter_key(self):
        return 'FFilter'      if self._filedata else 'Filter'
    @property
    def _params_key(self):
        return 'FDecodeParms' if self._filedata else 'DecodeParms'

    def decode(self):
        """Decode the data in the stream by sequentially applying the
        filters with their parameters"""
        if self._decoded:
            return self._decoded_data
        # Need to use self._filter_key because, for some reason beyond my
        # grasp, the key changes when the stream data is external
        # Also, since these may be lists, let's make that happen
        filters = ensure_list(self._header.get(self._filter_key, []))
        params  = ensure_list(self._header.get(self._params_key, []))
        if not params:
            params = [{} for f in filters]
        composed_filters = chain_funcs((partial(StreamFilter[f].decode, **p)
                                        for f, p in zip(filters, params)))
        decoded_data = composed_filters(self._data)
        self._decoded      = True
        self._decoded_data = decoded_data
        return self._decoded_data
    @property
    def data(self):
        return self.decode()

def chain_funcs(funcs):
    """Compose the functions in iterable funcs"""
    return lambda x: reduce(lambda f1, f2: f2(f1), funcs, x)

class PdfObjStream(PdfStream):
    """Subclass of PdfStream for object streams.  See pp. 100-105 for an 
    example of yet another thing slapped onto the PDF standard late in the
    game."""

    def __init__(self, header, data, document=None):
        """Create a new object stream"""
        from ..pdf_parser import PdfParser

        super(PdfObjStream, self).__init__(header, data)
        self._offsets = None
        self._obj_nos = None
        self._parser  = PdfParser(document)
        self._objects = self._header['N']*[None]

    def _parse_offsets(self):
        """Build the offsets and object numbers lists.
        
        TODO: Python 2-ify"""
        lines = (l for l in self.data.splitlines() if l.strip()[0] != b'%')
        nums = [int(n) for n in next(line).split()]
        self._obj_nos = [nums[i]   for i in range(0, len(nums), 2)]
        self._offsets = [nums[i+1] for i in range(0, len(nums), 2)]

    def get_nth_object(self, n):
        """Get the nth object in this stream"""
        if self._objects[n] is None:
            obj = self._parser.parse_simple_object(
                            self._data, self._header['First']+self._offsets[n])
            self._objects[n] = obj
        return self._objects[n]
