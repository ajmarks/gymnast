import binascii
import codecs
import io

from .common     import PdfType
from ..exc       import *
from ..misc      import iterbytes
from ..pdf_codec import register_codec

#PTVS nonsense
from builtins import *


# Go ahead and register the codec here, I guess.
register_codec()

class PdfString(PdfType):
    """Base class from which all of our string-like classes
    will inherit"""
    #Type hints for the IDE
    if False:
        _parsed_bytes = bytes()
        _raw_bytes    = bytes()

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

class PdfLiteralString(str, PdfString):
    def __new__(cls, data):
        try:
            string = cls._decode_bytes(cls.parse_bytes(data))
        except UnicodeDecodeError:
            string = codecs.encode(cls.parse_bytes(data), 'hex_codec').decode()
        obj = str.__new__(cls, string)
        obj.__init__(data)
        return obj
    @staticmethod
    def _decode_bytes(data):
        """Detect the encoding method and return the decoded string"""
        # Are we UTF-16BE?  Good.
        if data[:2] == '\xFE\xFF':
            return data.decode('utf_16_be')
        # If the string isn't UTF-16BE, it follows PDF standard encoding 
        # described in Appendix D of the reference.
        return data.decode('pdf_doc')

    """Class for PDF literal strings"""
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
        #TODO: Make this less disgusting
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
        return bytes(result.getvalue())

class PdfHexString(PdfString):
    def __init__(self, data):
        return super().__init__(data)
    @property
    def _text(self):
        return '0x'+binascii.hexlify(self._parsed_bytes).decode()
    @staticmethod
    def parse_bytes(token):
        hstr = token.decode()
        if len(hstr) % 2:
            hstr += '0'
        return bytes.fromhex(hstr)
    def __repr__(self):
        return str(self)

class PdfComment(PdfType, str):
    def __new__(cls, obj):
        if isinstance(obj, (bytes, bytearray)):
            obj = obj.decode(errors='surrogateescape')
        return str.__new__(cls, obj)
    def __init__(self, *args, **kwargs):
        PdfType.__init__(self)

class PdfName(PdfType, str):   
    # Needs to be string-like for key purposes
    def __new__(cls, *args, **kwargs):
        return str.__new__(cls, *args, **kwargs)