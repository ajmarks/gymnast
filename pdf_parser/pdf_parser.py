from .exc import *
from .pdf_types import PdfObjectReference, PdfComment, PdfLiteralString, \
                       PdfHexString, PdfStream, PdfXref, PdfTrailer,     \
                       PdfHeader, PdfIndirectObject
from .pdf_doc   import PdfDocument
from .misc      import ReCacher

import io

#PTVS nonsense
from builtins import *

class PdfParser(object):
    EOLS       = set([b'\r', b'\n', b'\r\n'])
    WHITESPACE = EOLS.union(set([b'\x00', b'\t', b'\f', b' ']))
    DELIMITERS = set([b'/', b'<', b'(', b'{', b'[', b'%'])
    ENDERS     = WHITESPACE.union(DELIMITERS)

    def parse(self, file):
        self._data  = bytearray(self._read_data(file))
        self._fsize = len(self._data)
        self._data.reverse()     # Pop()ing from the right is very inefficient
        self._ind_objects = {}   # Store the indirect objects here
        self._offsets     = []   # Keep track of object offsets for ind_objects
        header      = self._get_header()
        doc_objects = self._get_objects()
        return PdfDocument(header, doc_objects, self._ind_objects)

    def _read_data(self, file):
        if isinstance(file, str):
            with open(file, 'rb') as f:
                data = f.read()
        elif isinstance(file, io.IOBase) and hasattr(file, 'read'):
            data = file.read()
        elif not isinstance(file, (bytes, bytearray)):
            raise ValueError('Data to be parsed must be either bytes, '\
                    'bytesarray, a file name, or a read()able stream.')
        return data

    def _get_header(self):
        if self._pop_byte() != b'%':
            raise PdfParseError('PDF version header not found')
        hline = self._parse_comment(None)
        rc = ReCacher()
        # TODO: change these to fullmatch once 3.4+ is standard
        if   rc.match(r'PDF\-(\d+\.\d+)$', hline):
            header = PdfHeader(rc.group(1))
        elif rc.match(r'\!PS\?Adobe\?(\d+.\d+) PDF\?(\d+\.\d+)$', hline):
            header = PdfHeader(rc.group(2), rc.group(1))
        else:
            raise PdfError('Invalid PDF version header')
        # Optional binary line (bottom of p. 92): toss it out
        self._consume_whitespace()
        if self._data[-1:] == b'%' and \
          all(self._data[-i] > 128 for i in range(2,6)):
            x = self._parse_comment(None)
        return header


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
        elif closer and self._data[-clen:] == closer[::-1] \
            and value+self._data[-(clen-len(value)):] != closer: #The last clause covers an issue
            return True                                          #the dict as the last element of a dict
        elif bytes(self._data[-1:]) in PdfParser.ENDERS and \
              (value+self._data[-1:]) not in PdfParser.obj_types:
            return True
        return False

    def _consume_whitespace(self, whitespace=WHITESPACE):
        while bytes(self._data[-1:]) in whitespace and self._data:
            self._data.pop()

    def _pop_byte(self):
        try:
            return bytes((self._data.pop(),))
        except ValueError:
            return b''

    def _get_objects(self, closer=None):
        objects = []
        while self._data:
            token = self._get_next_token(closer)
            if not token: continue
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
            token += self._pop_byte()
        return token

    def _process_token(self, token, objects):
        self._store_offset(token)
        try:
            return self.obj_types[token](self, objects)
        except KeyError:
            return self._parse_literal(token)

    def _store_offset(self, token):
        """Store the offset at the begining of the token.  We'll need 
        this to handle xrefs."""
        self._offsets.append(self._fsize - len(self._data)-len(token))

    def _parse_reference(self, objects):
        """References an indirect object, which may or may not have already
        been defined.  If it has been defined, we can go ahead and deference
        (this may be changed in the future to facilitate re-saving), otherwise,
        return a PdfObjectReference"""
        generation = objects.pop()
        obj_no     = objects.pop()
        try:
            return self._ind_objects[(obj_no, generation)]
        except KeyError:
            return PdfObjectReference(obj_no, generation)

    def _parse_dict(self, objects):
        """A dict is just a differently delimited array, so we'll call that
        to get the elements"""
        elems = self._parse_array(objects, b'>>')
        return dict(zip(elems[::2], elems[1::2]))

    def _parse_hex_string(self, objects):
        token = self._pop_byte()
        while self._data and token[-1:] != b'>':
            token += self._pop_byte()
        return PdfHexString(token[:-1])

    def _parse_literal_string(self, objects):
        token   = b''
        parens  = 0
        escaped = False
        while self._data:
            b = self._pop_byte()
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
        elems = self._get_objects(closer)
        return elems

    def _parse_comment(self, objects):
        token = b''
        while self._data:
            b = self._pop_byte()
            if b in PdfParser.EOLS: break
            token += b
        return PdfComment(token)

    def _parse_expression(self, objects):
        """TODO: This"""
        pass

    def _parse_ind_object(self, objects):
        gen     = objects.pop()
        obj_no  = objects.pop()
        id      = (obj_no, gen)
        if id in self._ind_objects:
            raise PdfParseError('Indirect object identifiers must be unique. '\
                                'Duplicate value: '+str(id))
        offset  = self._offsets[-3]
        obj     = self._get_objects(closer=b'endobj')
        self._ind_objects[id] = \
            PdfIndirectObject(obj_no, gen, offset, obj[0] if obj else None)

    def _parse_stream(self, objects):
        header = objects.pop()
        lngth  = header['Length']
        if self._data[-2:] == b'\n\r': # Remember, we're backwards
            del self._data[-2:]
        elif self._data[-1:] == b'\n':
            del self._data[-1]
        else:
            raise PdfParseError('stream keyword must be followed by \\r\\n or \\n')
        # Yes, I know we can do this with fancy slices instead of .reverse()
        s_data = self._data[-lngth-1:]
        s_data.reverse()
        del self._data[-lngth:]
        if self._data[-11:] == b'maertsdne\n\r': # \r\nendstream
            del self._data[-11:]
        elif self._data[-10:] == b'maertsdne\n':
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
            xrefs.append(self._get_xref_block())
        return xrefs

    def _get_xref_block(self):
        """This method actually gets the xref table"""
        header = b''
        while bytes(self._data[-1:]) not in PdfParser.EOLS:
            header += self._pop_byte()
        self._consume_whitespace(PdfParser.EOLS)
        id0, nlines = map(int, header.split())
        # An xref line has _exactly_ 20 characters including the EOL
        lines = self._data[-20*nlines:][::-1].decode().splitlines()
        del self._data[-20*nlines:]
        return [PdfXref.from_line(id0+i, l) for i, l in enumerate(lines)]

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
        elif token == b'null' : return None
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
        return name.decode()

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
    obj_types = {b'<<'       : _parse_dict,
                 b'<'        : _parse_hex_string,
                 b'('        : _parse_literal_string,
                 b'['        : _parse_array,
                 b'%'        : _parse_comment,
                 b'{'        : _parse_expression,      # TODO
                 b'R'        : _parse_reference,
                 b'obj'      : _parse_ind_object,
                 b'stream'   : _parse_stream,
                 b'xref'     : _parse_xref,
                 b'trailer'  : _parse_trailer,
                }