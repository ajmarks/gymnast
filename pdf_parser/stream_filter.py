from .exc     import *
from .misc    import get_subclasses, ensure_str, classproperty, MetaGettable

#PTVS nonsense
from builtins import *

class StreamFilter(object, metaclass=MetaGettable):
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
        from .filters.ascii_filters import ASCIIHexDecode, ASCII85Decode
        from .filters.crypt_filters import Crypt
        from .filters.image_filters import DCTDecode
        from .filters.lzw_and_flate import LZWDecode, FlateDecode
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

class FilterExecutor(object):
    """Singleton that maintains the collection of all known filters and 
    dispatches them.  Once initiated, filters can be called by invoking 
    FilterExecutor[filter_name](data, **kwargs)"""

    __instance = None
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            fexec = super(FilterExecutor, cls).__new__(cls)
            fexec.__init__(*args, **kwargs)
            cls.__instance = fexec
        return cls.__instance
    
    def __init__(self):
        self._NOP     = NOPFilter
        self._filters = self._get_filters(StreamFilter)

    def __getitem__(self, filter_name):
        """Main dispatch method.  Return the filter if implemented, otherwise
        returns a NOP."""
        try:
            return self._filters[filter_name]
        except KeyError:
            #We should probably add some logging stuff here
            return self.NOP
    
    @staticmethod
    def _get_filters(cls):
        """Build the filters dict"""
        return {f.filter_name: f
                    for f in get_subclasses(cls) if f.filter_name}
        

import base64
import codecs

class ASCIIHexDecode(StreamFilter):
    filter_name = 'ASCIIHexDecode'
    EOD         = b'>'
    
    @staticmethod
    def decode_data(data):
        return codecs.decode(data, 'hex')

    @staticmethod
    def encode_data(data):
        return codecs.encode(data, 'hex')


class ASCII85Decode(StreamFilter):
    filter_name = 'ASCII85Decode'
    EOD         = b'~>'
    
    @staticmethod
    def decode_data(data):
        return base64.a85decode(data)

    @staticmethod
    def encode_data(data):
        return base64.a85encode(data)

class Crypt(StreamFilter):
    filter_name = 'Crypt'
    EOD         = None
    
    @staticmethod
    def decode_data(data, Type={}, Name='Identity'):
        raise NotImplementedError

    @staticmethod
    def encode_data(data):
        raise NotImplementedError

import PIL


class DCTDecode(StreamFilter):
    filter_name = 'DCTDecode'
    EOD         = None
    
    @staticmethod
    def decode_data(data):
        raise NotImplementedError

    @staticmethod
    def encode_data(data):
        raise NotImplementedError

from io import BytesIO
import zlib

class LZWDecode(StreamFilter):
    filter_name = 'LZWDecode'
    EOD         = None
    
    @staticmethod
    def decode_data(data, **kwargs):
        """Based on code from http://rosettacode.org/wiki/LZW_compression""" 
        # Build the dictionary.
        dict_size = 256
        dictionary = {bytes((i,)): bytes((i,)) for i in range(dict_size)}
 
        # use StringIO, otherwise this becomes O(N^2)
        # due to string concatenation in a loop
        result = BytesIO()
        compressed = bytearray(data)
        w = compressed.pop(0)
        result.write(w)
        for k in compressed:
            if k in dictionary:
                entry = dictionary[k]
            elif k == dict_size:
                entry = w + w[0]
            else:
                raise ValueError('Bad compressed k: %s' % k)
            result.write(entry)
 
            # Add w+entry[0] to the dictionary.
            dictionary[dict_size] = w + entry[0]
            dict_size += 1
 
            w = entry
        return result.getvalue()

class FlateDecode(StreamFilter):
    filter_name = 'FlateDecode'
    EOD         = None
    
    @staticmethod
    def decode_data(data, CloseTarget=False, Predictor=None, 
                    Columns=None, BitsPerComponent=None):
        #TODO: use these parameters
        return zlib.decompress(data)
