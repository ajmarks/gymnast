"""
Abstract base class for stream filters
"""
import six
from ..misc    import get_subclasses, ensure_str, classproperty, MetaGettable

@six.add_metaclass(MetaGettable)
class StreamFilter(object):
    """Abstract stream filter class.  Specify new filters by inheriting
    and setting filter_name and eod.

    Information on filters at can be found at
    https://partners.adobe.com/public/developer/en/ps/sdk/TN5603.Filters.pdf"""
    filter_name = None
    EOD         = None

    @classmethod
    def decode(cls, data, **kwargs):
        """Decode the encoded stream. Keyword arguments are the parameters from
        the stream dictionary."""
        if cls.EOD:
            end = data.find(bytes(cls.EOD))
            return cls.decode_data(data[:end if end > 0 else None], **kwargs)
        else:
            return cls.decode_data(data, **kwargs)

    @classmethod
    def encode(cls, data, **kwargs):
        """Encode the stream data. Keyword arguments are the parameters from
        the stream dictionary."""
        return cls.encode_data(data, **kwargs) + (cls.EOD if cls.EOD else b'')

    @staticmethod
    def decode_data(data, **kwargs):
        raise NotImplementedError

    @staticmethod
    def encode_data(data, **kwargs):
        raise NotImplementedError

    # Nothing to see here.  Pay no attention to that man behind the curtain.
    __filters = None

    @classproperty
    def filters(cls):
        if cls.__filters is None:
            cls.__init_filter()
        return cls.__filters

    @staticmethod
    def __init_filter():
        # Need to do the imports here to prevent circular imports.
        from .ascii_filters import ASCIIHexDecode, ASCII85Decode
        from .crypt_filters import Crypt
        from .image_filters import DCTDecode
        from .lzw_and_flate import LZWDecode, FlateDecode
        filters = {ensure_str(o.filter_name): o
                   for o in get_subclasses(StreamFilter) if o.filter_name}
        StreamFilter.__filters = filters
    @classmethod
    def __getitem__(cls, filter_name):
        filter_name = ensure_str(filter_name)
        try:
            return cls.filters[filter_name]
        except KeyError:
            #TODO: Leave PdfStream._decoded and ._decoded_data alone
            #this will probably mean that PdfStream objects will need to
            #operate on the stream, not the stream data, which, frankly, is
            #more elegant anyway
            return NOPFilter

class NOPFilter(StreamFilter):
    """NOP filter."""
    @staticmethod
    def decode_data(data, **kwargs):
        return data
    @staticmethod
    def encode_data(data, **kwargs):
        return data