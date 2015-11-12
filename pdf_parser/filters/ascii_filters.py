from .stream_filter import StreamFilter

import base64
import codecs

#PTVS nonsense
from builtins import *

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
