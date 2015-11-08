from stream_filter import StreamFilter

import base64

#PTVS nonsense
from builtins import *

class ASCIIHexDecode(StreamFilter):
    filter_name = 'ASCIIHexDecode'
    EOD         = b'>'
    
    @staticmethod
    def decode_data(data):
        return bytes.fromhex(data)

class ASCII85Decode(StreamFilter):
    filter_name = 'ASCII85Decode'
    EOD         = b'~>'
    
    @staticmethod
    def decode_data(data):
        return base64.a85decode(data)
