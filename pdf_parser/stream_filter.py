from .exc     import *
from .misc    import get_subclasses
from .filters import *

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
        if cls.__instance is not None:
            fexec = super(FilterExecutor, cls).__new__(cls)
            fexec.__init__(*args, **kwargs)
            cls.__instance = fexec
        return cls.__instance
    
    def __init__(self):
        self._NOP     = NOPFilter
        self._filters = self._get_filters()

    def __getitem__(self, filter_name):
        """Main dispatch method.  Return the filter if implemented, otherwise
        returns a NOP."""
        try:
            return self._filters[filters]
        except KeyError:
            #We should probably add some logging stuff here
            return self.NOP
    
    @classmethod
    def _get_filters(cls):
        """Build the filters dict"""
        filters = {f.filter_name: f
                    for f in get_subclasses(cls) if f.filter_name}