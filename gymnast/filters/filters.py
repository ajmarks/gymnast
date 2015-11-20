"""
Implement and register our stream filters
"""

import base64
import codecs
import io
import zlib
from .stream_filter import StreamFilter

# The best are the ones that are already done for us
def a85decode(data, **kwargs):
    return base64.a85decode(data)
def a85encode(data, **kwargs):
    return base64.a85decode(data)

def flate_decode(data, **kwargs):
    return zlib.decompress(data)
def flate_encode(data, **kwargs):
    return zlib.compress(data)
StreamFilter.register('ASCII85Decode', a85decode, b'~>', a85encode)
StreamFilter.register('FlateDecode', flate_decode, None, flate_encode)


def hex_decode(data):
    return codecs.decode(data, 'hex')
def hex_encode(data):
    return codecs.encode(data, 'hex')
StreamFilter.register('ASCIIHexDecode', hex_decode, b'>', hex_encode)


def lzw_decode(data, **kwargs):
    """Based on code from http://rosettacode.org/wiki/LZW_compression"""
    # Build the dictionary.
    dict_size = 256
    dictionary = {bytes((i,)): bytes((i,)) for i in range(dict_size)}

    # use StringIO, otherwise this becomes O(N^2)
    # due to string concatenation in a loop
    result = io.BytesIO()
    compressed = bytearray(data)
    w = compressed.pop(0)
    result.write(w)
    for k in compressed:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[0]
        else:
            raise ValueError('Bad compressed k: {}'.format(k))
        result.write(entry)

        dictionary[dict_size] = w + entry[0]
        dict_size += 1
        w = entry
    return result.getvalue()
StreamFilter.register('LZWDecode', lzw_decode)
