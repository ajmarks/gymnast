"""
Stream filters for encryption
"""

from ..stream_filter import StreamFilter

class Crypt(StreamFilter):
    """Encryption filter"""
    filter_name = 'Crypt'
    EOD         = None

    @staticmethod
    def decode_data(data, Type=None, Name='Identity'):
        raise NotImplementedError

    @staticmethod
    def encode_data(data):
        raise NotImplementedError
