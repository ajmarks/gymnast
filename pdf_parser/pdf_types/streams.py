from functools import partial, reduce

from .common   import PdfType
from ..exc     import *
from ..filters import StreamFilter
from ..misc    import ensure_list




class PdfStream(PdfType):
    def __init__(self, header, data):
        super().__init__()
        self._header  = header
        self._objects = None
        
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
    def _filter_key(self):
        return 'FFilter'      if self._filedata else 'Filter'
    @property
    def _params_key(self):
        return 'FDecodeParms' if self._filedata else 'DecodeParms'

    def decode(self):
        """Decode the data in the stream by sequentially applying the
        filters with their parameters"""
        if self._decoded == True:
            return self._decoded_data
        # Need to use self._filter_key because, for some reason beyond my 
        # grasp, the key changes when the stream data is external
        # Also, since these may be lists, let's make that happen
        filters = ensure_list(self._header.get(self._filter_key, []))
        params  = ensure_list(self._header.get(self._params_key, []))
        if len(params) == 0:
            params = [{} for f in filters]
        composed_filters = chain_funcs([partial(StreamFilter[f].decode, **p) 
                                        for f, p in zip(filters, params)])
        decoded_data = composed_filters(self._data)
        self._decoded      = True
        self._decoded_data = decoded_data
        return self._decoded_data
    @property
    def data(self):
       return self.decode()

def chain_funcs(funcs):
    return lambda x: reduce(lambda f1, f2: f2(f1), funcs, x)