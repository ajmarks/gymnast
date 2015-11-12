from .stream_filter import StreamFilter

import PIL


class Crypt(StreamFilter):
    filter_name = 'Crypt'
    EOD         = None
    
    @staticmethod
    def decode_data(data, Type={}, Name='Identity'):
        raise NotImplementedError

    @staticmethod
    def encode_data(data):
        raise NotImplementedError