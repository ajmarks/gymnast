import io

from .exc       import *
from .pdf_types import PdfBoolean, PdfNull, PdfNumeric, \
                       PdfString, PdfArray, PdfDict, PdfIndirectObject

#PTVS nonsense
from builtins import *

class PdfDocument(object):
    def __init__(self, file):
        self._objects        = {}
        self._file_structure = None
        self._doc_structure  = None
        self._content_stream = None
        #self._raw_data = self._read_file(file)

    def _read_file(self, file):
        if   isinstance(file, io.IOBase):
            return file.read()
        elif isinstance(file, str):
            with open(file, 'rb') as f:
                return f.read()

    @property
    def indirect_objects(self):
        return self._objects
    def get_object(self, object_number, generation):
        if (object_number, generation) in self._objects:
            return self._objects[(object_number, generation)]
        else:
            return PdfIndirectObject(self, object_number, generation)

    def _parse_data(self, data, closer=None):
        """Loop through the data, parsing it into PDF Objects.  This is 
        definitely the ugliest codes in the whole thing.
        
        TODO: Refactor this into its own class with a bunch of nice, neat 
        methods."""

        data     = bytes(data)
        dlen     = len(data)
        i        = 0
        tokens   = []
        comments = []
        clen     = len(closer) if closer else None
        DELIMITERS = set([b'/',b'<',b'{',b'[',b'('])
        BREAKS   = WHITESPACE.union(DELIMITERS)
        
        is_end = lambda i:   data[i:i+1] in BREAKS                \
                          or (closer and data[i:i+clen] == closer) \
                          or data[i:i+1] == b''

        while i < dlen:
            if closer and data[i:i+clen] == closer:
                return tokens, comments, i+clen+1
            elif  data[i:i+1] in WHITESPACE:
                i += 1
            elif data[i:i+2] == b'<<':              # Dict
                elems, comms, n = self._parse_data(data[i+2:], b'>>')
                if len(elems) % 2:
                    raise PdfParseError('Dictionary keys and values don\'t align')
                elif not(all([isinstance(elems[i], PdfName) 
                              for i in range(0, len(elems), 2)])):
                    raise PdfParseError('Dictionary keys must be names')
                token = PdfDict({elems[i]: elems[i+1] 
                                 for i in range(0, len(elems), 2)})
                token.comments = comms
                tokens.append(token)
                i += n + 1
            elif data[i:i+1] == b'[':               # Array
                elems, comms, n = self._parse_data(data[i+1:], b']')
                token = PdfArray(elems)
                token.comments = comms
                tokens.append(token)
                i += n
            elif data[i:i+1] in (b'(', b'<', b'/'): # String
                consumed = PdfString.find_string_end(data[i:])
                tokens.append(PdfString(data[i:i+consumed]))
                i += consumed
            elif data[i:i+1] == b'%':               # Comment
                for j in range(i+1, dlen):
                    if data[j:j+1] in LINEBREAKS: break
                comments.append(data[i+1:j])
                i = j
            elif data[i:i+1] == b'{':               # Expression
                pass
            elif data[i:i+3] == b'obj'   and is_end(i+3): # Indirect Object
                elems, comms, n = self._parse_data(data[i+3:], b'endobj')
                generation = tokens.pop()
                obj_no     = tokens.pop()
                if len(elems) == 1:
                    elems = elems[0]
                elif not elems:
                    elems = PdfNull()
                self._objects[(obj_no,generation)] = elems
                i += n + 2
            elif data[i:i+1] == b'R'   and is_end(i+1):   # Indirect Reference
                generation = tokens.pop()
                obj_no     = tokens.pop()
                #tokens.append(PdfIndirectObject(self, obj_no, generation))
                tokens.append(self.get_object(obj_no, generation))
                i += 1
            elif data[i:i+6] == b'stream' and is_end(i+6): #stream
                header = tokens.pop()
                if not isinstance(header, PdfDict):
                    raise PdfParseError('Stream detected without leading header')
                i += 6
                if data[i:i+2] == b'\r\n':
                    i += 2
                else:
                    i += 1
                tokens.append(PdfStream(header, data[i:i+header['Length']]))
                i = data.find(b'endstream', i+header['Length']) + 9
            elif data[i:i+4] == b'xref' and data[i+4:i+5] in LINEBREAKS: #xref
                if data[i+4:i+6] == b'\r\n': 
                    i += 6
                else:
                    i += 5
                j = i
                while data[j:j+1] not in LINEBREAKS: j+=1
                head  = data[i:j].decode().strip()
                lines = int(head.split()[1])
                
                n = 0
                while n <= lines and j < dlen:
                    if data[j:j+2] == b'\r\n':
                        n += 1
                    j += 1
                tokens.append(PdfXref(data[i:j]))
                i = j
                print(i)
            elif data[i:i+4] == b'null'   and is_end(i+4): # null
                tokens.append(PdfNull())
                i += 4
            elif data[i:i+4] == b'true'  and is_end(i+4): # true
                tokens.append(PdfBoolean(False))
                i += 4
            elif data[i:i+5] == b'false' and is_end(i+5): # false
                tokens.append(PdfBoolean(True))
                i += 5
            else: # Numeric
                for j in range(i, dlen):
                    if is_end(j): break
                try:
                    tokens.append(PdfNumeric(data[i:j]))
                except ValueError:
                    print(data[i-100:i+100])
                    raise ValueError('Invalid token found: '+str(data[i:j]))
                i = j
        if len(tokens) > 1:
            return tokens, comments
        else:
            return tokens[0], comments