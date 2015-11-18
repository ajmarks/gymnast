"""
PDF Element base class definition
"""

import six
from pprint     import pformat
try:
    from collections.abc import MutableMapping
except ImportError:
    from collections     import MutableMapping
if six.PY3:
    from functools       import reduce

from ..pdf_types import PdfType, PdfName

class PdfElement(MutableMapping):
    """Base class for all PDF page elements.  Generally invoked by passing as
    object dictionary to PdfElement.from_object(), though a convenience
    method, parsed_object, is defined on PdfIndirectObject and
    PdfObjectReference types.

    TODO: Move the object type detection out of pdf_types.PdfIndirectObject
    to somewhere more sane, probably here."""

    _object             = None
    # All of the attributes that must be defined __in the particular object__.
    # Do not include inheritable attributes.  Currently, this is only checked
    # when attempting to delete attributes.

    required_properties = set(('Type', ))
    @classmethod
    def from_object(cls, obj, object_key=None):
        return cls(obj.value, object_key)

    @property
    def parsed_object(self):
        return self
    def __init__(self, obj, obj_key=None):
        super(PdfElement, self).__init__()
        self._object  = obj.value
        self._obj_key = obj_key

    #Mapping stuff
    def __getitem__(self, key):
        val = self._object[key]
        if isinstance(val, PdfType):
            return val#.parsed_object
        else:
            return val
    def __setitem__(self, name, value):
        if name == 'Type':
            raise KeyError('A document object\'s type cannot be changed')
        self._object[PdfName(name)] = value
    def __delitem__(self, name):
        if name in self.required_properties:
            raise KeyError("'%s' is a required attribute and cannot be "
                           "deleted"%name)
        del self._object[name]
    def __len__(self):
        return len(self.__all_properties().union(self._object))
    def __iter__(self):
        return self._object.__iter__()

    # OO style access
    def __getattr__(self, name):
        try:
            val = self.__dict__[name]
        except KeyError:
            try:
                val = self._object[name]
            except KeyError:
                raise AttributeError('Object has no attribute "%s"'%name)
        if isinstance(val, PdfType):
            return val.parsed_object
        else:
            return val
    def __repr__(self):
        o = '\n'.join(['    '+l for l in pformat(dict(self)).splitlines()])
        txt = '{}(\n{}'.format(self.__class__.__name__, o)
        if self._obj_key:
            txt += ', '+pformat(self._obj_key)
        return txt +'\n)'
    def __dir__(self):
        return set(super(PdfElement, self).__dir__()).union(set(self._object.keys()))
    def __all_properties(self):
        """Get all properties defined on the object.  Probably only going to
        use this in __len__.  We need to go up the mro because properties are
        defined on the class, not the instance."""
        return reduce(lambda x, y: x.union(y),
                      [{k for k,v in six.iteritems(b.__dict__)
                        if isinstance(v, property)
                       } for b in self.__class__.__mro__
                      ]
                     )
