"""
PDF Parser object
"""

from contextlib import contextmanager
import io

from .exc           import PdfParseError
from .pdf_types     import PdfRaw, PdfRawData, PdfDict, PdfObjectReference,\
                           PdfLiteralString, PdfHexString, PdfComment, \
                           PdfIndirectObject, PdfArray, PdfName, PdfStream
from .misc          import BlackHole, buffer_data, consume_whitespace
from .pdf_constants import EOLS, WHITESPACE

__all__ = ['PdfParser']

class PdfParser(object):
    """Parser for PDF files.  Takes raw PDF data and turns it into PDF _types_,
    which can then be assembled into a document and document elements."""
    DELIMITERS = set([b'/', b'<', b'(', b'{', b'[', b'%'])
    ENDERS     = WHITESPACE.union(DELIMITERS)

    def __init__(self, document=None):
        """Initialize the PdfParser with a default PdfDocument"""
        from .pdf_doc import PdfDocument
        if document is None or isinstance(document, PdfDocument):
            self._doc = document
        else:
            raise PdfParseError('document must be either None or a PdfParser')

    def parse_simple_object(self, data, position=None):
        """Parse and return the simple object (i.e., not an indirect object)
        described in the first argument located at either current stream
        position or the position specified by the optional argument.  The
        stream's position will be left at the end of the object.

        This method should only be used in places where an indirect object
        reference is not valid."""
        if position is not None:
            data.seek(position)
        token = self._get_next_token(data)
        return self._process_token(data, token, None)

    def parse_indirect_object(self, data, position=None):
        """Parse and return the indirect object described in the first argument
        located at either current stream position or the position specified by
        the optional argument.  The stream's position will be left at the end of the object."""
        if position is not None:
            data.seek(position)
        obj_no  = self._process_token(data, self._get_next_token(data), None)
        obj_gen = self._process_token(data, self._get_next_token(data), None)
        if not isinstance(obj_no, int) or not isinstance(obj_gen, int):
            raise PdfParseError('Object identification not found')
        token   =  self._get_next_token(data)
        if token != b'obj':
            raise PdfParseError("Expected 'obj', got '%s'"%token)
        return self._parse_ind_object(data, [obj_no, obj_gen])

    def _get_objects(self, data, closer=None):
        """Get all of the objects in data starting from the current position
        until hitting EOF or the optional closer argument.  Returns a list of
        PdfTypes, ints, floats, and bools.

        TODO: Restore PdfInt, etc."""
        objects = []
        while data.peek(1):
            token = self._get_next_token(data, closer)
            if not token: continue
            if token == closer: break
            element  = self._process_token(data, token, objects)
            if token not in (b'obj', b'xref'):
                objects.append(element)
        return objects

    def parse_list(self, data, allow_invalid=False, disallowed=frozenset()):
        """Parse the data and return a list"""
        data = buffer_data(data)
        return [i for i in self.iterparse(data, allow_invalid, disallowed)]

    def iterparse(self, data, allow_invalid=True,
                  disallowed=frozenset({b'R', b'obj', b'stream'})):
        """Generator-parser primarily for use in content streams."""
        data = buffer_data(data)
        while data.peek(1):
            token = self._get_next_token(data, disallowed=disallowed)
            if not token: continue
            element  = self._process_token(data, token, BlackHole(),
                                           allow_invalid)
            yield element
            if isinstance(element, PdfRaw) and element == b'BI':
                for i in self._parse_inline_image(data, disallowed):
                    yield i

    def _parse_inline_image(self, data, disallowed):
        """Special method for handling inline images in content streams because
        they are absolutely awful.

        See Reference pp. 352-355"""
        attrs = []
        token = None
        while data.peek(1) and token != b'ID':
            token = self._get_next_token(data, disallowed=disallowed)
            if not token: continue
            attrs.append(self._process_token(data,token,BlackHole, True))
        yield PdfDict({attrs[i]:attrs[i+1] for i in range(0,len(attrs)-1,2)})
        data.read(1)
        img = io.BytesIO()
        buf = bytes(2)
        while buf != b'EI':
            buf = buf[1:]+data.read(1)
            img.write(buf[1:])
        yield PdfRawData(img.getvalue()[:-2]) # This is such an ugly hack
        yield PdfRaw(b'EI')

    @staticmethod
    def _eod(data):
        return not bool(data.peek(1))

    @staticmethod
    def _peek(data, n=1):
        """Peek ahead, returning the requested number of characters.  If peek()
        doesn't yield enough data, read and backup."""
        if n <= 0: return b''
        res = data.peek(n)[:n]
        if len(res) == n:
            return res
        res += data.read(n-len(res))
        data.seek(-len(res), 1)
        return res

    @classmethod
    def _get_next_token(cls, data, closer=None, disallowed=frozenset()):
        """Get the next token in the stream, data.  Closer is an optional
        argument specifying the ending token of the current data structure,
        e.g., >> for dicts."""
        clen  = len(closer) if closer is not None else None
        token = io.BytesIO()
        cls._consume_whitespace(data)

        while data.peek(1) and (token.getvalue() != closer) \
           and not cls._is_token(data, token.getvalue(),
                                 closer, clen, disallowed):
            token.write(data.read(1))
        return token.getvalue()

    @classmethod
    def _is_token(cls, data, value, closer=None, clen=None,
                  disallowed=frozenset()):
        """Is this a token?"""
        if closer and not clen:
            clen = len(closer)

        if   cls._eod(data): return True
        elif not value:      return False

        next_char = cls._peek(data, 1)
        not_obj   = (value+next_char) not in cls.obj_types

        if value in cls.obj_types and not_obj and value not in disallowed:
            return True
        elif closer and cls._peek(data, clen) == closer \
            and value+cls._peek(data, clen-len(value)) != closer: #Last clause covers an issue with
            return True                                       #a dict as the last element of a dict
        elif next_char in cls.ENDERS and not_obj:
            return True
        return False

    def _process_token(self, data, token, objects, allow_invalid=False):
        """Process the data at the current position in the stream data into the
        data type indicated by token.

        Optional arguments:
            objects       - A list of objects already known.
            allow_invalid - Don't raise an exception when an invalid token is
                            encountered, instead returning a PdfRaw object."""
        try:
            return self.obj_types[token](self, data, objects)
        except KeyError:
            try:
                return self._parse_literal(token)
            except PdfParseError:
                #This lets us use this parse Content Streams
                if allow_invalid: return PdfRaw(token)
                else:             raise

    @staticmethod
    def _consume_whitespace(data, whitespace=WHITESPACE):
        consume_whitespace(data, whitespace)

    def _parse_reference(self, data, objects):
        """References an indirect object, which may or may not have already
        been defined."""
        generation = objects.pop()
        obj_no     = objects.pop()
        return PdfObjectReference(obj_no, generation, self._doc)

    def _parse_dict(self, data, objects):
        """A dict is just represented as a differently delimited array, so
        we'll call that to get the elements"""
        elems = self._parse_array(data, objects, b'>>')
        return PdfDict(zip(elems[::2], elems[1::2]))

    def _parse_hex_string(self, data, objects):
        # TODO: Eliminate all of these getvalue() calls
        token = io.BytesIO(data.read(1))
        token.seek(0, 2)
        while data.peek(1) and token.getvalue()[-1:] != b'>':
            token.write(data.read(1))
        return PdfHexString(token.getvalue()[:-1])

    def _parse_literal_string(self, data, objects):
        token   = io.BytesIO()
        parens  = 0
        escaped = False
        while data.peek(1):
            b = data.read(1)
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
    def _parse_array(self, data, objects, closer=b']'):
        """The main method aready returns a list of the objects it found,
        so that's easy"""
        elems = self._get_objects(data, closer)
        return PdfArray(elems)

    def _parse_comment(self, data, objects):
        token = io.BytesIO()
        while data.peek(1):
            b = data.read(1)
            if b in EOLS: break
            token.write(b)
        else:
            return PdfComment(token.getvalue())

    def _parse_expression(self, data, objects):
        """TODO: This"""
        pass

    def _parse_ind_object(self, data, objects):
        gen     = objects.pop()
        obj_no  = objects.pop()
        obj     = self._get_objects(data, closer=b'endobj')
        return  PdfIndirectObject(obj_no, gen, obj[0] if obj else None,
                                  self._doc)

    def _parse_stream(self, data, objects):
        header = objects.pop()
        lngth  = header['Length']
        if isinstance(lngth, PdfObjectReference):
            lngth = lngth.value
        if data.peek(1)[:1] == b'\r': data.read(1)
        if data.peek(1)[:1] == b'\n': data.read(1)
        s_data = data.read(lngth)
        # Long peeks are not guaranteed to work, so we're going to do this
        # hackish read/seek for now
        close = data.read(11)
        if   close      == b'\r\nendstream':
            pass
        elif close[:-1] == b'\nendstream':
            data.seek(-1, 1)
        elif close[:-2] == b'endstream':
            data.seek(-2, 1)
        else:
            raise PdfParseError('endstream not found')
        return PdfStream(header, s_data)

    @staticmethod
    def _parse_literal(token):
        """Parse a simple literal number, boolean, or null"""
        token = bytes(token)
        if   token == b'true':  return True
        elif token == b'false': return False
        elif token == b'null':  return None
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
        name = bytearray(token[1:])
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

    #def _parse_trailer(self, objects):
    #    self._consume_whitespace()
    #    if self._data.read(2) != b'<<':
    #        raise PdfError('dict expected following trailer keyword')
    #    trailer   = self._parse_dict(objects)
    #    self._consume_whitespace()
    #    return PdfTrailer(trailer)

    #def _parse_startxref(self, objects):
    #    self._consume_whitespace()
    #    xref = self._parse_literal(self._get_next_token())
    #    if not isinstance(xref, int):
    #        raise PdfParseError('startxref value must be an int')
    #    return PdfStartXref(xref)

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
                 #b'xref'     : _parse_xref,
                 #b'trailer'  : _parse_trailer,
                 #b'startxref': _parse_startxref
                }

    # List methods
    def append(self):    return None
