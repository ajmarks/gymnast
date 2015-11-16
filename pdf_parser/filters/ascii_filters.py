"""
Stream filters for parsing ASCII-encoded binary data
"""

from .stream_filter import StreamFilter

import base64
import codecs




class ASCIIHexDecode(StreamFilter):
    """Hex-encoded ASCII"""
    filter_name = 'ASCIIHexDecode'
    EOD         = b'>'
        
    @staticmethod
    def decode_data(data):
        return codecs.decode(data, 'hex')

    @staticmethod
    def encode_data(data):
        return codecs.encode(data, 'hex')


class ASCII85Decode(StreamFilter):
    """ASCII Base 85 encoded data"""
    filter_name = 'ASCII85Decode'
    EOD         = b'~>'
    
    @staticmethod
    def decode_data(data):
        return base64.a85decode(data)

    @staticmethod
    def encode_data(data):
        return base64.a85encode(data)
