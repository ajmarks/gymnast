import io
import numbers
import re
from decimal   import Decimal
from functools import partial, reduce

from .exc           import *
from .misc          import iterbytes
from .stream_filter import FilterExecutor


#PTVS nonsense
from builtins import *

LINEBREAKS = set([b'\r', b'\n', b'\r\n'])
WHITESPACE = LINEBREAKS.union([b'\x00', b'\x09', b'\x0A', b'\x20'])

class PdfType(object):
    """Abstract base class for PDF objects"""
    def pdf_encode(self):
        """Translate the object into bytes in PDF format"""
        raise NotImplementedError


class PdfString(PdfType):
    #Type hints for the IDE
    if False:
        _parsed_bytes = bytes()
        _raw_bytes    = bytes()
    
    """Base class from which all of our string-like classes
    will inherit"""
    def __lt__(self, other): return self._parsed_bytes.__lt__(other)
    def __le__(self, other): return self._parsed_bytes.__le__(other)
    def __eq__(self, other): return self._parsed_bytes.__eq__(other)
    def __ne__(self, other): return self._parsed_bytes.__ne__(other)
    def __gt__(self, other): return self._parsed_bytes.__gt__(other)
    def __ge__(self, other): return self._parsed_bytes.__ge__(other)
    def __bool__(self):      return self._parsed_bytes.__bool__()
    def __bytes__(self):     return self._parsed_bytes
    def __str__(self):       return self._text
    def __hash__(self):      return self._parsed_bytes.__hash__()
    def __repr__(self):
        return self.__class__.__name__+"("+self._raw_bytes.__repr__()+")"
    
       
    def __init__(self, data):
        super().__init__()
        self._raw_bytes    = data
        self._parsed_bytes = self.parse_bytes(data)
                
    @staticmethod
    def parse_bytes(data):
        raise NotImplementedError

class PdfLiteralString(PdfString):
    ESCAPES = {b'n'   : b'\n',
               b'r'   : b'\r',
               b't'   : b'\t',
               b'b'   : b'\b',
               b'f'   : b'\f',
               b'('   : b'(' ,
               b')'   : b')' ,
               b'\\'  : b'\\',
               b'\n'  : b'',
              #b'\r'  : b'' , # Stupid \r\n
               b'\r\n': b''}
            
    @staticmethod
    def parse_bytes(data):
        iter    = iterbytes(data)
        escaped = 0 # (0, 1, 2, 3) = (Unescaped, Normal escape, escape-\r, escape-digit)
        e_str   = b''
        result  = io.BytesIO()
        for d in iter:
            if escaped:
                escaped = False
                try:
                    result.write(PdfLiteralString.ESCAPES[e_str+d])
                    continue
                except KeyError: pass
                if not e_str:
                    e_str   = d
                    escaped = True
                    continue
                elif e_str == b'\r': pass # If we're here, it means that e_str == \r, d != \n
                #Octals
                elif e_str.isdigit():
                    if not d.isdigit():
                        result.write(bytes((min(int(e_str  , 8),255),)))
                    elif len(e_str) == 2:
                        result.write(bytes((min(int(e_str+d, 8),255),)))
                        continue
                    else:
                        e_str += d
                        escaped = True
                        continue
                else: raise PdfParseError('Invalid escape sequence in literal string')

            if d == b'\\':
                e_str   = b''
                escaped = True
            else:
                result.write(d)
        return result.getvalue()

class PdfHexString(PdfString):
    @property
    def _text(self):
        return '0x'+self._raw_bytes.decode()
           
    @staticmethod
    def parse_bytes(token):
        return bytes.fromhex(token.decode())

class PdfIndirectObject(PdfType):
    def __init__(self, object_number, generation, offset, object):
        super().__init__()
        self._object_number = object_number
        self._generation    = generation
        self._offset        = offset
        self._object        = object

    def get_object(self):
        return self._object
    object = property(get_object)

class PdfObjectReference(PdfType):
    def __init__(self, object_number, generation, document=None):
        super().__init__()
        self._object_number = object_number
        self._generation    = generation
        self._document      = document
        
        if   not isinstance(self._object_number, int) \
          or not isinstance(self._generation,    int) \
          or self._object_number <= 0 or self._generation < 0:
            raise ValueError('Invalid indirect object identifier')
       
    def get_object(self, document=None):
        if not document and not self._document:
            raise PdfError('Evaluating indirect references requires a document')
        id = (self._object_number, self._generation)
        return (document if document else self._document).indirect_objects[id]
    object = property(get_object)

    def __str__(self): 
        return 'PdfObjectReference(%d, %d)'%(self._object_number, self._generation)
    def __repr__(self): 
        return 'PdfObjectReference(%d, %d)'%(self._object_number, self._generation)

class PdfStream(PdfType):
    filters = FilterExecutor()

    def __init__(self, header, data):
        super().__init__()
        self._header  = header
        
        # This is obnoxious, but the PDF standard allows the stream header to
        # to specify another file with the data, ignoring the stream data.
        # Also, for some reason, some header keys change when that happens.
        try:
            with open(header['F'], 'rb') as f:
                data = f.read()
        except KeyError:
            self._data     = data
            self._filedata = False
        else:
            self._filedata = True
        self._decoded  = bool(headers.get(self._filter_key))

    @property
    def _filter_key(self):
        return 'FFilter' if self._filedata else 'Filter'
    @property
    def _params_key(self):
        return 'FDecodeParms' if self._filedata else 'DecodeParms'

    def decode(self):
        if self._decoded == True:
            return self._decoded_data
        data = self._data
        filter_names = list(self._header.get(self._filter_key, []))
        params       = list(self._header.get(self._params_key, []))
        if len(params) == 0:
            params = [{} for f in filters]
        decoded_data = reduce(lambda f1, f2: f2(f1), 
                              [partial(self.filters[f], **p) 
                               for f, p in zip(filter_names, params)], data)
        self._decoded      = True
        self._decoded_data = decoded_data
        return self._decoded_data
    decoded_data = property(decode)


class PdfXref(PdfType):
    LINE_PAT = re.compile(r'(\d{10}) (\d{5}) (n|f)$')

    def __init__(self, id, offset, generation, in_use):
        super().__init__()
        self._id         = id
        self._offset     = offset
        self._generation = generation
        self._in_use     = in_use

    def get_object(self, document):
        if self._in_use:
            return document.get_offset(self._offset)
        else:
            return None # TODO: implement free Xrefs

    def __str__(self):
        return '{:010d} {:010d} '.format(self._offset, self._generation)\
              +('n' if self._in_use else 'f')

    @staticmethod
    def from_line(id, line):
        # TODO: change to fullmatch once 3.4+ is standard
        match = re.match(PdfXref.LINE_PAT, line)
        if not match:
            raise PdfParseError('Invalid xref line')
        return PdfXref(id, int(match.group(1)), int(match.group(2)), 
                       True if match.group(3) == 'n' else False)


class PdfComment(PdfType, str):
    def __new__(cls, obj):
        if isinstance(obj, (bytes, bytearray)):
            obj = obj.decode(errors='surrogateescape')
        return str.__new__(cls, obj)
    def __init__(self, *args, **kwargs):
        PdfType.__init__(self)

class PdfTrailer(PdfType):
    def __init__(self, trailer, startxref):
        super().__init__()
        self._trailer   = trailer
        self._startxref = startxref

class PdfHeader(PdfType):
    def __init__(self, version, adobe_version=None):
        super().__init__()
        self.version       = Decimal(version)
        self.adobe_version = Decimal(adobe_version) if adobe_version else None
    def __str__(self):
        vers = '%'
        if self.adobe_version:
            vers += '!PS-Adobe-'+str(self.adobe_version)+' '
        return vers+'PDF-'+str(self.version)
    def __bytes__(self):
        return bytes(str(self))

###These were so unnecessary
#

#class PdfCompountType(PdfType):
#    pass
#class PdfArray(PdfCompountType, list):
#    def __init__(self, *args, **kwargs):
#        PdfCompountType.__init__(self)
#        list.__init__(self, *args, **kwargs)
#class PdfDict(PdfCompountType, dict):
#    def __init__(self, *args, **kwargs):
#        PdfCompountType.__init__(self)
#        dict.__init__(self, *args, **kwargs)
#class PdfNull(PdfType):
#    _instance = None
#    
#    def __new__(cls): 
#        if PdfNull._instance is not None:
#            null = super(PdfNull, cls).__new__(cls)
#            null.__init__(null)
#            PdfNull._instance = null
#        return PdfNull._instance
#
#    def __str__(self):       return 'PdfNull'
#    def __repr__(self):      return 'PdfNull()'
#    def __bool__(self):      return False
#    def __hash__(self):      return id(self)
#    def __eq__(self, other): return (None == other)
#    def __ne__(self, other): return (None != other)
#class PdfBoolean(PdfSimpleType):
#    """We'll probably kill this class later"""
#    _instances = None
#    def __new__(cls, val):
#        if PdfBoolean._instances is None:
#            PdfBoolean._instances = (super(PdfBoolean, cls).__new__(cls),
#                                     super(PdfBoolean, cls).__new__(cls))
#            PdfBoolean._instances[0].__init__(val)
#            PdfBoolean._instances[1].__init__(val)
#            PdfBoolean._instances[0]._bool = False
#            PdfBoolean._instances[1]._bool = True
#        if   val in (b'true', 'true') or val is True:
#            return PdfBoolean._instances[1]
#        elif val in (b'false', 'false') or val is False:
#            return PdfBoolean._instances[0]
#        else: raise ValueError('PdfBoolean value must be "true" or "false"')
#    
#    def __init__(self, val):
#        super().__init__()
#
#    def __str__(self):       return 'true' if self else 'false'
#    def __repr__(self):      return 'PdfBoolean(%s)'%str(self)
#    # Guido has decreed that we can't inherit from bool, so we need
#    # to do all of this junk manually
#    def __lt__(self, other): return self._bool.__lt__(other)
#    def __le__(self, other): return self._bool.__le__(other)
#    def __eq__(self, other): return self._bool.__eq__(other)
#    def __ne__(self, other): return self._bool.__ne__(other)
#    def __gt__(self, other): return self._bool.__gt__(other)
#    def __ge__(self, other): return self._bool.__ge__(other)
#    def __bool__(self):      return self._bool
#    def __bytes__(self):     return self._bool.__bytes()
#    def __hash__(self):      return self._bool.__hash__()
#
#class PdfNumeric(PdfSimpleType):
#    """Base class for PdfNumeric types.  Numbers can be initialized as
#    PdfNumeric(12) or PdfNumeric('-12.43'), and the appropriate subtype
#    will be returned"""
#    def __new__(cls, val):
#        if isinstance(val, numbers.Integral):
#            return PdfInt(val)
#        elif isinstance(val, numbers.Real):
#            return PdfReal(val)
#        try:
#            return PdfInt(val)
#        except ValueError:
#            return PdfReal(val)
#
#class PdfInt(PdfNumeric, int):
#    def __new__(cls, val):
#        return int.__new__(cls, val)
#
#class PdfReal(PdfNumeric, float):
#    def __new__(cls, val):
#        return float.__new__(cls, val)
#class PdfName(PdfString):   
#    # Needs to be string-like for key purposes
#    def __eq__(self, other):  return (self._text == other)
#    def __hash__(self):       return self._parsed_bytes.__hash__()
#    
#    @property
#    def _text(self):
#        return self._parsed_bytes.decode('utf-8')
#    
#    @staticmethod
#    def parse_bytes(data):
#        data = bytearray(data)
#        dlen = len(data)
#        i = 0
#        while i <= dlen:
#            if data[i:i+1] == b'#':
#                data[i:i+3] = int(data[i+1:i+3], 16).to_bytes(1, 'big')
#                dlen -= 2
#                i += 1
#            i += 1
#        return bytes(data[1:])
#        
#    @staticmethod
#    def find_string_end(data):
#        """Given bytes beginning with a name string, returns the end
#        of the slice containing the string data"""
#        for i in range(1, len(data)):
#            if data[i:i+1] in WHITESPACE:
#                return i
#        raise PdfParseError('Name not terminated')