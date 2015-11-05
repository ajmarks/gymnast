if __name__ == '__main__':
    from exc import *
    from pdf_types import PdfIndirectObject, PdfComment, PdfLiteralString, \
                          PdfHexString, PdfStream, PdfXref, PdfTrailer
else:
    from .exc import *
    from .pdf_types import PdfIndirectObject, PdfComment, PdfLiteralString, \
                           PdfHexString, PdfStream, PdfXref, PdfTrailer
#PTVS nonsense
from builtins import *

class PdfParser(object):
    EOLS       = set([b'\r', b'\n', b'\r\n'])
    WHITESPACE = EOLS.union(set([b'\x00', b'\t', b'\f', b' ']))
    DELIMITERS = set([b'/', b'<', b'(', b'{', b'[', b'%'])
    ENDERS     = WHITESPACE.union(DELIMITERS)

    def _at_end(self, closer=None, clen=None):
        """Determin if we're at the end of a token or value, either by being 
        out of data, encountering whitespace or a new delimiter, or hitting 
        the current data structure's closing token"""

        if bytes(self._data[-1:]) in PdfParser.ENDERS:  return True
        return False
    
    def _is_token(self, value, closer=None, clen=None):
        """Is this a token?"""
        if closer and not clen:
            clen = len(closer)
        if   not self._data            : return True
        elif not value                 : return False
        elif value in PdfParser.obj_types and \
              (value+self._data[-1:]) not in PdfParser.obj_types:
            return True
        elif closer and self._data[-clen:] == closer[::-1]:
            return True
        elif bytes(self._data[-1:]) in PdfParser.ENDERS and \
              (value+self._data[-1:]) not in PdfParser.obj_types:
            return True
        return False

    def _consume_whitespace(self, whitespace=WHITESPACE):
        while bytes(self._data[-1:]) in whitespace and self._data:
            self._data.pop()

    def __init__(self, data):
        if not isinstance(data, (bytes, bytearray)):
            raise ValueError('Data to be parsed must be of '\
                             'type bytes or bytearray')
        self._data = bytearray(data)
        self._data.reverse() # Pop()ing from the right is very inefficient
        self._objects = {}

    def _next_byte(self):
        try:
            return bytes((self._data.pop(),))
        except ValueError:
            return b''

    def _pop_closer(self, closer):
        clen = len(closer)
        if self._data[-clen:] == closer:
            del self._data[-clen:]
        else:
            raise PdfParseError('Closer not found. Expected %s, found %s' %
                                    (repr(closer), repr(self._data[-clen:])))

    def _parse_file(self):
        # Do some stuff to parse the file header here
        data = self._parse_data()
        
    def _parse_data(self, closer=None):
        objects = []
        while self._data:
            token = self._get_next_token(closer)
            if token == closer: break
            element  = self._process_token(token, objects)
            if token != b'obj':
                objects.append(element)
        return objects

    def _get_next_token(self, closer=None):
        clen  = len(closer) if closer is not None else None
        token = b''
        self._consume_whitespace()
        while self._data and token != closer \
            and not self._is_token(token, closer, clen):

            token += self._next_byte()
        return token

    def _process_token(self, token, objects):
        try:
            return self.obj_types[token](self, objects)
        except KeyError:
            return self._parse_literal(token)

    def _parse_reference(self, objects):
        """References an indirect object, which may or may not have already 
        been defined.  If it has been defined, we can go ahead and deference
        (this may be changed in the future to facilitate re-saving), otherwise,
        return a PdfIndirectObject"""
        generation = objects.pop()
        obj_no     = objects.pop()
        try:
            return self._objects[(obj_no, generation)]
        except KeyError:
            return PdfIndirectObject(obj_no, generation)
    
    def _parse_dict(self, objects):
        """A dict is just a differently delimited array, so we'll call that
        to get the elements"""
        elems = self._parse_array(objects, b'>>')
        return dict(zip(elems[::2], elems[1::2]))

    def _parse_hex_string(self, objects):
        token = b''
        while self._data and not self._is_token(token, b'>', 1):
            token += self._next_byte()
        self._pop_closer(b'>')
        return PdfHexString(token)

    def _parse_literal_string(self, objects):
        token   = b''
        parens  = 0
        escaped = False
        while self._data:
            b = self._next_byte()
            if  escaped:
                escaped = False
            elif b == b'\\':
                escaped = True
            elif b == b'(': 
                parens += 1
            elif b == b')': 
                if parens == 0:
                    return PdfLiteralString(token)
                else:
                    parens -= 1
            token  += b
        raise PdfParseError('Unterminated string literal')
    def _parse_array(self, objects, closer=b']'):
        """The main method aready returns a list of the objects it found, 
        so that's easy"""
        elems = self._parse_data(closer)
        return elems

    def _parse_comment(self, objects):
        token = b''
        while self._data:
            b = self._next_byte()
            if b in PdfParser.EOLS: break
            token += b
        return PdfComment(token)

    def _parse_expression(self, objects):
        pass

    def _parse_object(self, objects):
        generation = objects.pop()
        obj_no     = objects.pop()
        obj        = self._parse_data(closer=b'endobj')
        self._objects[(obj_no, generation)] = obj[0] if obj else None

    def _parse_stream(self, objects):
        header = objects.pop()
        lngth  = header['Length']
        if self._data[-2:] == b'\n\r': # Remember, we're backwards
            del self._data[-2:]
        elif self._data[-1:] == b'\n':
            del self._data[-1]
        else:
            raise PdfParseError('stream keyword must be followed by \\r\\n or \\n')
        # Yes, I know we can do this with fancy slices
        s_data = self._data[-lngth-1:]
        s_data.reverse()
        del self._data[-lngth:]
        if self._data[-11:] == b'maertsdne\n\r': # \r\nendstream
            del self._data[-11:]
        elif self._data[-10:-1] == b'maertsdne' and self._data[-1:] == b'\n':
            del self._data[-10:]
        elif self._data[-9:] == b'maertsdne':
            del self._data[-9:]
        else:
            raise PdfParseError('endstream not found')
        return PdfStream(header, s_data)

    def _parse_xref(self, objects):
        """See p. 93"""
        xrefs = []
        self._consume_whitespace(PdfParser.EOLS)
        while self._data[-1:].isdigit():
            xrefs.append(self._get_xref())
        return PdfXref(xrefs)
        
    def _get_xref(self):
        """This method actually gets the xref table"""
        header = b''
        while bytes(self._data[-1:]) not in PdfParser.EOLS:
            header += self._next_byte()
        self._consume_whitespace(PdfParser.EOLS)
        lines = int(header.split()[1])
        # An xref line has _exactly_ 20 characters including the EOL
        xref = (header, self._data[-20*lines:])
        del self._data[-20*lines:]
        xref[1].reverse()
        return xref

    def _parse_trailer(self, objects):
        self._consume_whitespace()
        if self._data[-2:] != b'<<':
            raise PdfError('dict expected following trailer keyword')
        del self._data[-2:]
        trailer   = self._parse_dict(objects)
        self._consume_whitespace()
        if self._get_next_token() == b'startxref':
            startxref = self._get_next_token()
        return PdfTrailer(trailer, startxref)

    @staticmethod
    def _parse_literal(token):
        """Parse a simple literal number, boolean, or null"""
        token = bytes(token)
        if   token == b'true' : return True
        elif token == b'false': return False
        elif token == b'null' :  return None
        elif token[:1] == b'/':
            return PdfParser._parse_name(token)
        else:
            try:
                return PdfParser._parse_number(token)
            except ValueError:
                raise PdfParseError('Invalid token found: '+repr(token))

    @staticmethod
    def _parse_number(token):
        try:
            return int(token)
        except ValueError:
            return float(token)

    @staticmethod
    def _parse_name(token):
        """Parse names by stripping the leading / and replacing instances of 
        #YY with the character b'\\xYY', returning a unicode string."""
        name = token[1:]
        hash_pos = name.find(b'#')
        while hash_pos > 0:
            try:
                new_char = bytes((int(name[hash_pos+1:hash_pos+3], 16),))
            except ValueError:
                raise PdfError('Invalid hex code in name %s (%s)'\
                                    %(token, name[hash_pos:hash_pos+3]))
            name[hash_pos:hash_pos+3] = new_char
            hash_pos = name.find(b'#', hash_pos)
        return name.decode('utf-8')

    @property
    def remaining_data(self):
        """This is mostly for use in debugging"""
        return self._data[::-1]

    # dict of PDF object types besides literals to look for.
    # Keys are the token that identifies that beginning of that type,
    # and values are method that does the parsing
    # This dict does not need to include simple literals (numerics, booleans
    # nulls, and names).  Each of these processing functions takes one argument,
    # the current scope's objects list.
    obj_types = {b'<<'       : _parse_dict,            # Written
                 b'<'        : _parse_hex_string,      # Written
                 b'('        : _parse_literal_string,  # Written
                 b'['        : _parse_array,           # Written
                 b'%'        : _parse_comment,         # Written
                 b'{'        : _parse_expression,      #
                 b'R'        : _parse_reference,       # Written
                 b'obj'      : _parse_object,          # Written
                 b'stream'   : _parse_stream,          # Written
                 b'xref'     : _parse_xref,            # Written
                 b'trailer'  : _parse_trailer,         # Written
                }
if __name__ == '__main__':
    fname = 'S:/Research/Leisure/STR RevPar Data/US Weekly PDFs/Lodging Smith Travel Results 15-10-07.pdf'
    with open(fname, 'rb') as f:
        data = f.read()
    #data = data[:860]
    parser = PdfParser(data)
    elements = parser._parse_data()
    print(elements)