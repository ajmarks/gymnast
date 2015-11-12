from .stream_filter import StreamFilter

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

