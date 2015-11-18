"""
PDF string-like objects
"""

import binascii
import codecs
import io

from .common     import PdfType
from ..exc       import PdfParseError
from ..misc      import iterbytes
from ..pdf_codec import register_codec

# Go ahead and register the codec here, I guess.
register_codec()

class PdfString(PdfType):
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
    def __hash__(self):      return self._parsed_bytes.__hash__()
    def __repr__(self):
        return self.__class__.__name__+"("+self._raw_bytes.__repr__()+")"

    def __init__(self, data):
        super(PdfString, self).__init__()
        self._raw_bytes    = data
        self._parsed_bytes = self.parse_bytes(data)

    @staticmethod
    def parse_bytes(data):
        raise NotImplementedError

class PdfLiteralString(str, PdfString):
    """PDF Literal strings"""
    def __new__(cls, data):
        try:
            string = cls._decode_bytes(cls.parse_bytes(data))
        except UnicodeDecodeError:
            string = codecs.encode(cls.parse_bytes(data), 'hex_codec').decode()
        obj = str.__new__(cls, string)
        obj.__init__(data)
        return obj

    def __init__(self, data):
        PdfString.__init__(self, data)
        str.__init__(self)

    @staticmethod
    def _decode_bytes(data):
        """Detect the encoding method and return the decoded string"""
        # Are we UTF-16BE?  Good.
        if data[:2] == '\xFE\xFF':
            return data.decode('utf_16_be')
        # If the string isn't UTF-16BE, it follows PDF standard encoding
        # described in Appendix D of the reference.
        return data.decode('pdf_doc')

    ESCAPES = {b'n'   : b'\n',
               b'r'   : b'\r',
               b't'   : b'\t',
               b'b'   : b'\b',
               b'f'   : b'\f',
               b'('   : b'(',
               b')'   : b')',
               b'\n'  : b'',
               b'\r'  : b''}

    @staticmethod
    def parse_escape(data):
        r"""Handle escape sequences in literal PDF strings.  This should be
        pretty straightforward except that there are line continuations,
        so \\n, \\r\n, and \\r are ignored. Moreover, actual newline characters
        are also valid.  It's very stupid. See pp. 53-56 in the Reference if 
        you want to be annoyed.

        Arguments:
            data - io.BytesIO-like object

        Returns the unescaped bytes"""
        e_str = data.read(1)
        try:
            val = PdfLiteralString.ESCAPES[e_str]
        except KeyError:
            # Not a normal escape, hopefully it's an octal
            if not e_str.isdigit():
                print(e_str)
                raise PdfParseError('Invalid escape sequence in literal string')
        else:
            # Handle \\r\n by skipping the next character
            if e_str == b'\r' and data.peek(1)[:1] == b'\n':
                data.seek(1,1)
            return val
        # If it's not one of the above, it must be an octal of
        # length at most 3
        for i in range(2):
            e_str += data.read(1)
            if not e_str.isdigit():
                data.seek(-1, 1)
                return bytes((min(int(e_str[:-1], 8),255),))
        return bytes((min(int(e_str, 8),255),))

    @staticmethod
    def parse_bytes(data):
        """Extract a PDF escaped string into a nice python bytes object."""

        iodata  = io.BufferedReader(io.BytesIO(data))
        escaped = 0 # (0, 1, 2, 3) = (Unescaped, Normal escape, escape-\r, escape-digit)
        e_str   = b''
        result  = io.BytesIO()
        char = iodata.read(1)
        while char:
            if char == b'\\':
                result.write(PdfLiteralString.parse_escape(iodata))
            else:
                result.write(char)
            char = iodata.read(1)
        return bytes(result.getvalue())

class PdfHexString(PdfString):
    """Hex strings, mostly used for ID values"""
    def __init__(self, data):
        super(PdfHexString, self).__init__(data)
    @property
    def _text(self):
        return '0x'+binascii.hexlify(self._parsed_bytes).decode()
    @staticmethod
    def parse_bytes(token):
        hstr = token.decode()
        if len(hstr) % 2:
            hstr += '0'
        return codecs.decode(hstr, 'hex_codec')
    def __repr__(self):
        return str(self)
    def pdf_encode(self):
        return b'<'+self._raw_bytes+b'>'

class PdfComment(PdfType, str):
    """Comments"""
    def __new__(cls, obj):
        if isinstance(obj, (bytes, bytearray)):
            obj = obj.decode(errors='surrogateescape')
        return str.__new__(cls, obj)
    def __init__(self, *args, **kwargs):
        PdfType.__init__(self)
        str.__init__(self)
    def pdf_encode(self):
        return b'%' + bytes(self.parsed_object)

class PdfName(PdfType, str):
    """PDF name objects, mostly use for dict keys"""
    def __new__(cls, *args, **kwargs):
        return str.__new__(cls, *args, **kwargs)
    def __init__(self, *args, **kwargs):
        PdfType.__init__(self)
        str.__init__(self)
