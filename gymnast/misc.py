"""
Miscellaneous functions and classes that get used in various places
"""

import io
import re
import struct
from functools import wraps

from .pdf_constants import WHITESPACE

__all__ = [
    # Static functions
    'buffer_data', 'ensure_str', 'ensure_list', 'is_digit',
    'read_until', 'force_decode', 'consume_whitespace',
    'int_from_bytes', 'int_to_bytes',
    # Decorators
    'classproperty',
    # Classes
    'ReCacher', 'BlackHole', 'defaultlist',
    # Metaclasses
    'MetaGettable', 'MetaNonelike',
    ]

def int_from_bytes(val):
    """Converts val to an unsinged int assuming a BE byte order"""
    try:
        return int.from_bytes(val, 'big')
    except AttributeError:
        # Older Python, so pad it and unpack
        return struct.unpack('>L', b'\x00'*(4-len(val))+val)[0]

def int_to_bytes(val, len):
    """Converts val to bigendian bytes"""
    try:
        return val.to_bytes(len, 'big')
    except AttributeError:
        # Older Python, so pack it and strip the padding
        return struct.pack('>q', val)[-len:]

def _is_buffered_bytesio(data):
    """Check if the argument is a buffered bytes io object"""
    if   not isinstance(data, io.BufferedIOBase):              return False
    elif not data.readable():                                  return False
    elif isinstance(data.raw, io.BytesIO):                     return True
    elif isinstance(data.raw, io.FileIO) and 'b' in data.mode: return True
    return False

def read_until(data, char_set):
    """Reads buffered io object until an element of char_set is encountered,
    returning the read data without the terminator."""
    result = io.BytesIO()
    char_set = set(char_set)
    c = data.read(1)
    while c and c not in char_set:
        result.write(c)
        c = data.read(1)
    return result.getvalue()

def is_digit(val):
    """Returns True if chr(val) is a digit 0-9"""
    return  48 <= val <= 57

def consume_whitespace(data, whitespace=WHITESPACE):
    """Reads buffered io object data until a non-whitespace byte is encountered
    and leaves the file position at that character."""
    whitespace = set(whitespace)
    for c in whitespace:
        break
    while c and c in whitespace:
        c = data.read(1)
    if c and c not in whitespace:
        data.seek(-1, 1) # Rewind 1 byte

def force_decode(bstring):
    """Tries to decode a bytestring to text.  If that fails, just repr it."""
    try:
        return bstring.decode()
    except UnicodeDecodeError:
        return repr(bstring)[2:-1]

def buffer_data(data):
    """Wrap the data in a BufferedReader if we need to."""
    if _is_buffered_bytesio(data):
        return data
    elif isinstance(data, io.BytesIO):
        return io.BufferedReader(data)
    elif isinstance(data, (bytes, bytearray)):
        return io.BufferedReader(io.BytesIO(data))
    else:
        try:
            return io.BufferedReader(io.BytesIO(bytes(data)))
        except TypeError:
            raise TypeError('Data to be parsed must be either bytes, '
                            'bytesarray, or a read()able stream.')

class classproperty(object):
    """Like the @property method, but for classes instead of instances"""
    def __init__(self, fget):
        self.fget = fget
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)

class defaultlist(list):
    """Like collections.defaultdict, but a list"""
    def __init__(self, item_factory, *args, **kwargs):
        """Creates a defaultlist with values from item_factory()"""
        self._item_factory = item_factory
        super().__init__(*args, **kwargs)

    def __getitem__(self, index):
        """Get the item, expanding the list as needed"""
        try:
            return super().__getitem__(index)
        except IndexError:
            # Slices won't IndexError, and that's how we want it
            if index >= 0:
                self.extend([self._item_factory()]*(index - len(self) + 1))
                return super().__getitem__(index)
            else: #Too large a negative index has no obvious meaning
                raise

    def __setitem__(self, index, value):
        """Set the item, expanding the list as needed"""
        try:
            super().__setitem__(index, value)
        except IndexError:
            # Slices won't IndexError, and that's how we want it (probably)
            if index >= 0:
                self.extend([self._item_factory()]*(index - len(self) + 1))
                return super().__setitem__(index, value)
            else: #Too large a negative index has no obvious meaning
                raise

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
    def __eq__(cls, other): return (None is other)
    def __ne__(cls, other): return (None is not other)
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
    """Converts the argument to a string if it isn't one already"""
    if isinstance(val, str):
        return val
    elif isinstance(val, (bytes, bytearray)):
        return val.decode()
    else:
        raise ValueError('Expected bytes or string')
def ensure_list(val):
    """Converts the argument to a list, wrapping in [] if needed"""
    return val if isinstance(val, list) else [val]

#def iterbytes(bstring):
#    """Turn a bytes object into a generator that yields bytes instead of ints"""
#    for b in bstring:
#        yield bytes((b,))

#def get_subclasses(cls):
#    """Get all known subclasses of cls"""
#    subs = cls.__subclasses__()
#    for s in subs:
#        subs += get_subclasses(s)
#    return subs

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
        """Whatever the last method call returned"""
        return self._retval

    def __getattr__(self, name):
        try:
            re_attr = getattr(re, name)
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
    def __get__(self, instance, owner):  return BlackHole()
    def __set__(self, instance, value):  pass
    def __delete__(self, instance):      pass
    def __getitem__(self, key):          return BlackHole()
    def __setitem__(self, key, value):   pass
    def __delitem__(self, key):          pass
    def __contains__(self, item):        return False
    def __iter__(self):                  return iter([])
    def __next__(self):                  raise StopIteration
    def __bool__(self):                  return False
    def __repr__(self):                  return ''
    def __str__(self):                   return ''
    def __bytes__(self):                 return b''
    def __len__(self):                   return 0
    def __int__(self):                   return 0
    def __float__(self):                 return 0.0
    def __complex__(self):               return complex()
    def __round__(self, n=0):            return round(self.float, n)
    def __call__(self, *args, **kwargs): pass
    def __add__(self, other):            return other
    def __sub__(self, other):            return other
    def __mul__(self, other):            return other
    def __matmul__(self, other):         return other
    def __truediv__(self, other):        return other
    def __floordiv__(self, other):       return other
    def __mod__(self, other):            return other
    def __divmod__(self, other):         return other
    def __pow__(self, other):            return other
    def __lshift__(self, other):         return other
    def __rshift__(self, other):         return other
    def __and__(self, other):            return other
    def __xor__(self, other):            return other
    def __or__(self, other):             return other
    def __getattr__(self, name):         return BlackHole()
    def __setattr__(self, name, value):  pass
