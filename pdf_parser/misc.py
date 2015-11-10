import re
import numbers
from functools import wraps

class classproperty(object):
    """Like the @property method, but for classes instead of instances"""
    def __init__(self, fget):
        self.fget = fget
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)

class MetaGettable(type):
    """Metaclass to allow classes to be treated as dictlikes with MyClass[key].
    Instance classes should implement a classmethod __getitem__(cls, key)."""
    def __getitem__(cls, key):
        return cls.__getitem__(key)
class MetaNonelike(type):
    """Metaclass to make a class as None-like as possible."""
    def __call__(cls):
        return cls
    def __str__(cls):       return cls.__name__
    def __repr__(cls):      return cls.__name__
    def __hash__(cls):      return id(cls)
    def __bool__(cls):      return False
    def __lt__(cls, other): return (None <  other)
    def __le__(cls, other): return (None <= other)
    def __eq__(cls, other): return (None == other)
    def __ne__(cls, other): return (None != other)
    def __gt__(cls, other): return (None >  other)
    def __ge__(cls, other): return (None >= other)

###Not currently using these, but they are clever, if bad, ideas
#class MetaCallable(type):
#    """Metaclass to allow classes to be treated as callables. With this,
#    MyClass(*args, **kwargs) will call a _classmethod_ MyClass.__call__
#    instead of returning a new object.  Obviously, anything with this
#    metaclass will be a singleton."""
#    def __call__(cls, *args, **kwargs):
#        return cls.__call__(*args, **kwargs)
#class MetaMixin(type):
#    """MetaMetaclass for inheriting multiple metaclasses. Typical use:
#    class A(object, metaclass=MetaMixin('MetaA', (Meta1, Meta1))"""
#    def __new__(cls, metaname, metaclasses, attributes={}):
#        return type(metaname, metaclasses, attributes)
#    # Defining __init__ just to help IDEs with the docstring
#    def __init__(cls, name, bases, attributes={}):
#        """Combines multiple metaclasses into one.  Arguments correspond to
#        those of type()."""
#        super().__init__()

def ensure_str(val):
    if isinstance(val, str):
        return val
    elif isinstance(val, (bytes, bytearray)):
        return val.decode()
    else:
        raise ValueError('Expected bytes or string')
def ensure_list(val):
    return val if isinstance(val, list) else [val]

def iterbytes(bstring):
    for b in bstring:
        yield bytes((b,))

def get_subclasses(cls):
    subs = cls.__subclasses__()
    for s in subs:
        subs += get_subclasses(s)
    return subs

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

class BlackHole(object):  
    """The ultimate NOP object.  Stick it just about anywhere, 
    and it will successfully do nothing."""
    def __get__(*args, **kwargs)     : return None
    def __set__(*args, **kwargs)     : pass
    def __getitem__(*args, **kwargs) : return None
    def __setitem__(*args, **kwargs) : pass
    def __delitem__(*args, **kwargs) : pass
    def __contains__(*args, **kwargs): return False
    def __iter__(*args, **kwargs)    : return args[0]
    def __next__(*args, **kwargs)    : raise StopIteration
    def __bool__(*args, **kwargs)    : return False
    def __str__(*args, **kwargs)     : return ''
    def __bytes__(*args, **kwargs)   : return b''
    def __len__(*args, **kwargs)     : return 0
    def __int__(*args, **kwargs)     : return 0
    def __float__(*args, **kwargs)   : return 0.0
    def __complex__(*args, **kwargs) : return complex()
    def __round__(self, n)           : return round(self.float, n)
    def __call__(*args, **kwargs)    : pass
    def __add__(self, other)         : return other
    def __sub__(self, other)         : return other
    def __mul__(self, other)         : return other
    def __matmul__(self, other)      : return other
    def __truediv__(self, other)     : return other
    def __floordiv__(self, other)    : return other
    def __mod__(self, other)         : return other
    def __divmod__(self, other)      : return other
    def __pow__(self, other, *args)  : return other
    def __lshift__(self, other)      : return other
    def __rshift__(self, other)      : return other
    def __and__(self, other)         : return other
    def __xor__(self, other)         : return other
    def __or__(self, other)          : return other
    def __getattr__(*args, **kwargs) : return BlackHole()