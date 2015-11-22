"""
Abstract base class for stream filters
"""
import six
from collections import namedtuple
from warnings    import warn
from ..misc      import ensure_str, MetaGettable

base = namedtuple('StreamFilter', ('filter_name','decoder', 'EOD', 'encoder'))
base.__new__.__defaults__ = (None, None)
class StreamFilterBase(base):
    """Stream filter class."""
    def decode(self, data, params):
        """Decode the encoded stream."""
        if self.EOD:
            end = data.find(bytes(self.EOD))
            return self.decoder(data[:end if end > 0 else None], params)
        else:
            return self.decoder(data, params)
    def encode(self, data, params):
        """Encode the stream data."""
        if self.encoder:
            return self.encoder(data, params) + (self.EOD if self.EOD else b'')
        else:
            warn('Encoding for {} not implemented'.format(self.filter_name))
            return data + (self.EOD if self.EOD else b'')

@six.add_metaclass(MetaGettable)
class StreamFilter(object):
    """PDF stream filter stream dispatcher.  Stream filters are registered by
    calling PdfOperation.register() and passing a subclass of StreamFilterBase.

    Information on filters at can be found at
    https://partners.adobe.com/public/developer/en/ps/sdk/TN5603.Filters.pdf"""
    # Nothing to see here.  Pay no attention to that man behind the curtain.
    _filters    = {}
    _nop_filter = StreamFilterBase('NOPFilter', lambda x: x)

    @classmethod
    def register(cls, filter_name, decoder, eod=None, encoder=None):
        """Register a new stream filter"""
        new_filt = StreamFilterBase(filter_name, decoder, eod, encoder)
        cls._filters[filter_name] = new_filt

    @classmethod
    def __getitem__(cls, filter_name):
        filter_name = ensure_str(filter_name)
        try:
            return cls._filters[filter_name]
        except KeyError:
            return cls._nop_filter
