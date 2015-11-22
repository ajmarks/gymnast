"""
Implement and register our stream filters
"""

import base64
import codecs
import io
import zlib
from .stream_filter import StreamFilter
from .predictors    import predictor_encode, predictor_decode

# The best are the ones that are already done for us
def a85decode(data, params=None):
    """Ascii Base 85 decoding."""
    if params:
        raise ValueError('a85decode does not take any parameters')
    return base64.a85decode(data)
def a85encode(data, params=None):
    """Ascii Base 85 encode."""
    if params:
        raise ValueError('a85encode does not take any parameters')
    return base64.a85decode(data)
def hex_decode(data):
    return codecs.decode(data, 'hex')
def hex_encode(data):
    return codecs.encode(data, 'hex')
StreamFilter.register('ASCII85Decode',  a85decode, b'~>', a85encode)
StreamFilter.register('ASCIIHexDecode', hex_decode, b'>', hex_encode)


def flate_decode(data, params=None):
    """Zlib decompress and predictors"""
    data = zlib.decompress(data)
    if not params:
        return data
    else:
        return predictor_decode(data, params.get('Predictor', 1), params)
def flate_encode(data, params=None):
    """Apply predictors and zlib compress"""
    data = zlib.compress(data)
    if not params:
        return data
    else:
        return predictor_encode(data, params.get('Predictor', 1), params)

def _lzw_decode(data):
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
def lzw_decode(data, params=None):
    """Zlib decompress and predictors"""
    data = _lzw_decode(data)
    if not params:
        return data
    else:
        return predictor_decode(data, params.get('Predictor', 1), params)
StreamFilter.register('FlateDecode', flate_decode, None, flate_encode)
StreamFilter.register('LZWDecode', lzw_decode)
