from ..stream_filter import StreamFilter

from io import BytesIO
import zlib

#PTVS nonsense
from builtins import *

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
