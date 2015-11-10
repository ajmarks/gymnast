from contextlib import contextmanager
import io

from .exc       import *
from .pdf_types import *
from .misc      import ReCacher, BlackHole

#PTVS nonsense
from builtins import *

class PdfParser(object):
    EOLS       = set([b'\r', b'\n', b'\r\n'])
    WHITESPACE = EOLS.union(set([b'\x00', b'\t', b'\f', b' ']))
    DELIMITERS = set([b'/', b'<', b'(', b'{', b'[', b'%'])
    ENDERS     = WHITESPACE.union(DELIMITERS)

    def __init__(self, document=None):
        from .pdf_doc import PdfDocument
        if document is None or isinstance(document, PdfDocument):
            self._doc = document
        else:
            raise PdfParseError('document must be either None or a PdfParser')

    @staticmethod
    @contextmanager
    def file_context(file):
        """Context manager for loading the data if needed.  If the file was 
        opened by a different function, we're not going to close it here."""
        if PdfParser._is_buffered_bytesio(file):
            yield file
        elif isinstance(file, str):
            f = open(file, 'rb')
            yield f
            f.close()
        elif isinstance(file, io.BytesIO):
            yield io.BufferedReader(file)
        elif isinstance(file, (bytes, bytearray)):
            yield io.BufferedReader(io.BytesIO(file))
        else:
            try:
                yield io.BufferedReader(io.BytesIO(bytes(file)))
            except TypeError:
                raise ValueError('Data to be parsed must be either bytes, '
                                 'bytesarray, a file name, or a read()able stream.')

    def parse(self, data, full_file=True, allow_invalid=False):
        with PdfParser.file_context(data) as data:
            return self._parse(data, full_file, allow_invalid)
    
    def iterparse(self, data):
        """Generator-parser for use in content streams."""
        with PdfParser.file_context(data) as data:
            yield from self._iterparse(data)

    def _parse(self, data, full_file=True, allow_invalid=False):
        if not PdfParser._is_buffered_bytesio(data):
            raise PdfParseError(\
                'data must be a readable, binary io.BufferedIOBase object')
        self._data          = data
        self._ind_objects   = {}   # Store the indirect objects here
        self._xrefs         = []   # Store our Xref tables here
        self._offsets       = []   # Keep track of object offsets for ind_objects
        self._allow_invalid = allow_invalid
        if full_file:
            header      = self._get_header()
        doc_objects = self._get_objects()
        if full_file:
            return header, self._ind_objects, doc_objects, self._xrefs
        else:
            return doc_objects

    def _iterparse(self, data):
        """Generator-parser for use in content streams."""
        self._data          = data
        self._allow_invalid = True
        self._offsets       = BlackHole()
        while not self._eod:
            token = self._get_next_token(None)
            if not token: continue
            element  = self._process_token(token, None)
            yield element

    def _iter_get_objects(self):
        objects = []
        while not self._eod:
            token = self._get_next_token(None)
            if not token: continue
            element  = self._process_token(token, objects)
            yield element

    def _get_objects(self, closer=None):
        objects = []
        while not self._eod:
            token = self._get_next_token(closer)
            if not token: continue
            if token == closer: break
            element  = self._process_token(token, objects)
            if token not in (b'obj', b'xref'):
                objects.append(element)
        return objects

    @staticmethod
    def _is_buffered_bytesio(file):
        if   not isinstance(file, io.BufferedIOBase)             : return False
        elif not file.readable()                                 : return False
        elif isinstance(file.raw, io.BytesIO)                    : return True
        elif isinstance(file.raw, io.FileIO) and 'b' in file.mode: return True
        return False

    @property
    def _eod(self):
        return not bool(self._peek(1))
    
    def _peek(self, n=1):
        return self._data.peek(n)[:n]      

    def _get_header(self):
        if self._data.read(1) != b'%':
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
        next_chars = self._peek(5)
        if next_chars[:1] == b'%' and \
          all(next_chars[i] > 128 for i in range(1,5)):
            self._parse_comment(None)
        return header

    def _is_token(self, value, closer=None, clen=None):
        """Is this a token?"""
        if closer and not clen: 
            clen = len(closer)
        
        if self._eod  : return True
        elif not value: return False

        next_char = self._peek(1)
        not_obj   = (value+next_char) not in PdfParser.obj_types

        if value in PdfParser.obj_types and not_obj:
            return True
        elif closer and self._peek(clen) == closer \
            and value+self._peek(clen-len(value)) != closer: #The last clause covers an issue
            return True                                     #the dict as the last element of a dict
        elif next_char in PdfParser.ENDERS and not_obj:
            return True
        return False

    def _consume_whitespace(self, whitespace=WHITESPACE):
        # Get an initial value for c
        for c in whitespace:
            break
        while not self._eod and c in whitespace:
            c = self._data.read(1)
        if c not in whitespace:
            self._data.seek(-1, 1) # Rewind 1 byte

    def _get_objects(self, closer=None):
        objects = []
        while not self._eod:
            token = self._get_next_token(closer)
            if not token: continue
            if token == closer: break
            element  = self._process_token(token, objects)
            if token not in (b'obj', b'xref'):
                objects.append(element)
        return objects

    def _get_next_token(self, closer=None):
        clen  = len(closer) if closer is not None else None
        token = io.BytesIO()
        self._consume_whitespace()
        
        while not self._eod and token.getvalue() != closer \
           and not self._is_token(token.getvalue(), closer, clen):
            token.write(self._data.read(1))
        return token.getvalue()

    def _process_token(self, token, objects):
        self._store_offset(token)
        try:
            return self.obj_types[token](self, objects)
        except KeyError:
            try:
                return self._parse_literal(token)
            except PdfParseError:
                #This lets us use this parse Content Streams
                if self._allow_invalid:
                    return PdfRaw(token)
                else:
                    raise

    def _store_offset(self, token):
        """Store the offset at the begining of the token.  We'll need 
        this to handle xrefs."""
        self._offsets.append(self._data.tell()-len(token))

    def _parse_reference(self, objects):
        """References an indirect object, which may or may not have already
        been defined."""
        generation = objects.pop()
        obj_no     = objects.pop()
        return PdfObjectReference(obj_no, generation, self._doc)

    def _parse_dict(self, objects):
        """A dict is just a differently delimited array, so we'll call that
        to get the elements"""
        elems = self._parse_array(objects, b'>>')
        return PdfDict(zip(elems[::2], elems[1::2]))

    def _parse_hex_string(self, objects):
        # TODO: Eliminate all of these getvalue() calls
        token = io.BytesIO(self._data.read(1))
        while not self._eod and token.getvalue()[-1:] != b'>':
            token.write(self._data.read(1))
        return PdfHexString(token.getvalue()[:-1])

    def _parse_literal_string(self, objects):
        token   = io.BytesIO()
        parens  = 0
        escaped = False
        while not self._eod:
            b = self._data.read(1)
            if  escaped:
                escaped = False
            elif b == b'\\':
                escaped = True
            elif b == b'(':
                parens += 1
            elif b == b')':
                if parens == 0:
                    return PdfLiteralString(token.getvalue())
                else:
                    parens -= 1
            token.write(b)
        raise PdfParseError('Unterminated string literal')
    def _parse_array(self, objects, closer=b']'):
        """The main method aready returns a list of the objects it found,
        so that's easy"""
        elems = self._get_objects(closer)
        return PdfArray(elems)

    def _parse_comment(self, objects):
        token = io.BytesIO()
        while not self._eod:
            b = self._data.read(1)
            if b in PdfParser.EOLS: break
            token.write(b)
        if token.getvalue() == b'%EOF':
            return PdfEOF()
        else:
            return PdfComment(token.getvalue())

    def _parse_expression(self, objects):
        """TODO: This"""
        pass

    def _parse_ind_object(self, objects):
        gen     = objects.pop()
        obj_no  = objects.pop()
        id      = (obj_no, gen)
        offset  = self._offsets[-3]
        obj     = self._get_objects(closer=b'endobj')
        self._ind_objects[id] = \
            PdfIndirectObject(obj_no, gen, offset, 
                              obj[0] if obj else None, self._doc)

    def _parse_stream(self, objects):
        header = objects.pop()
        lngth  = header['Length']
        if self._peek(2) == b'\r\n':
            self._data.read(2)
        elif self._peek(1) == b'\n':
            self._data.read(1)
        else:
            raise PdfParseError('stream keyword must be followed by \\r\\n or \\n')
        s_data = self._data.read(lngth)
        if self._peek(11)   == b'\r\nendstream':
            self._data.read(11)
        elif self._peek(10) == b'\nendstream':
            self._data.read(10)
        elif self._peek(9)  == b'endstream':
            self._data.read(9)
        else:
            raise PdfParseError('endstream not found')
        return PdfStream(header, s_data)

    def _parse_xref(self, objects):
        """See p. 93"""
        xrefs = []
        self._consume_whitespace(PdfParser.EOLS)
        while self._peek(1).isdigit():
            xrefs.append(self._get_xref_block())
        self._xrefs.append(PdfXref(xrefs, self._offsets[-1]))

    def _get_xref_block(self):
        """This method actually gets the xref table"""
        header = b''
        while bytes(self._peek(1)) not in PdfParser.EOLS:
            header += self._data.read(1)
        self._consume_whitespace(PdfParser.EOLS)
        id0, nlines = map(int, header.split())
        # An xref line has _exactly_ 20 characters including the EOL
        lines = self._data.read(20*nlines).decode().splitlines()
        return [PdfXrefLine.from_line(id0+i, l) for i, l in enumerate(lines)]

    def _parse_trailer(self, objects):
        self._consume_whitespace()
        if self._data.read(2) != b'<<':
            raise PdfError('dict expected following trailer keyword')
        trailer   = self._parse_dict(objects)
        self._consume_whitespace()
        return PdfTrailer(trailer)
    
    def _parse_startxref(self, objects):
        self._consume_whitespace()
        xref = self._parse_literal(self._get_next_token())
        if not isinstance(xref, int):
            raise PdfParseError('startxref value must be an int')
        return PdfStartXref(xref)        

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
        return PdfName(name.decode())

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
                 b'startxref': _parse_startxref
                }
    
    # List methods 
    def append(self):    return None