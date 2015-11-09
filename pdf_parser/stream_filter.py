from .exc     import *
from .misc    import get_subclasses

#PTVS nonsense
from builtins import *

class StreamFilter(object):
    """Abstract stream filter class.  Specify new filters by inheriting 
    and setting filter_name and eod.
    
    Information on filters at can be found at 
    https://partners.adobe.com/public/developer/en/ps/sdk/TN5603.Filters.pdf"""
    filter_name = None
    EOD         = None

    @classmethod
    def decode(cls, data, **kwargs):
        if cls.EOD:
            end = data.find(bytes(cls.EOD))
            return cls.decode_data(data[:end if end > 0 else None], **kwargs)
        else:
            return cls.decode_data(data, **kwargs)

    @classmethod
    def encode(cls, data, **kwargs):
        return cls.encode_data(data, **kwargs) + (cls.EOD if cls.EOD else b'')

    @staticmethod
    def decode_data(data, **kwargs):
        raise NotImplementedError
    @staticmethod
    def encode_data(data, **kwargs):
        raise NotImplementedError

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
