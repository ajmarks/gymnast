import re
from functools import wraps

class classproperty(object):
    def __init__(self, fget):
        self.fget = fget
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)

def iterbytes(bstring):
    for b in bstring:
        yield bytes((b,))

class ReCacher(object):
    """Passes calls and arguments through to re and caches the results.
    Usage:

    rc = ReCacher()
    if   rc.match(<pattern1>, <string>): do_something(rc.group(3))
    elif rc.match(<pattern1>, <string>): do_something(rc.group(2))
    
    The return value from the last call can also be accessed through the
    .value property."""
    
    def __init__(self):
        self._retval = None

    @property
    def value(self):
        return self._retval

    def __getattr__(self, name):
        try:
            re_attr = re.__getattribute__(name)
            if callable(re_attr):
                re_attr = self._cache_wrapper(re_attr)
            return re_attr
        except AttributeError:
            return self._retval.__getattribute__(name)

    def _cache_wrapper(self, fn):
        @wraps(fn)
        def cached(*args, **kwargs):
            self._retval = fn(*args, **kwargs)
            return self._retval
        return cached