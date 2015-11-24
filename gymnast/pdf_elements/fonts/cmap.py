"""
CIDMap objects

See Reference pp. 441-452, and 472-475 for an overview. Full treatment at
http://www.adobe.com/content/dam/Adobe/en/devnet/font/pdfs/5014.CIDFont_Spec.pdf
"""

from ...pdf_parser import PdfParser
from ...pdf_types  import PdfRaw
from ...misc       import int_from_bytes, int_to_bytes
from bidict import bidict

RANGE_OPS = {'usematrix', 'codespacerange', 'cmap',
             'bfchar', 'bfrange', 'cidchar','cidrange',
             'notdefchar', 'notdefrange', 'rearrangedfont',''}
OTHER_OPS = {'usecmap', 'usefont',}
PARAMS    = {'CIDSystemInfo', 'CMapName', 'CMapType'}
RANGES = {'begin'+b:'end'+b for b in RANGE_OPS}
RANGES.update({p:'def' for p in PARAMS})

def clean_token(token):
    """Convert PdfRaw tokens to strings"""
    if isinstance(token, PdfRaw):
        return token.decode()
    else:
        return token

def codespace(start, end):
    if len(start) != len(end):
        raise ValueError('start and end must have the same dimesionality')
    if start == b'':
        yield b''
    for i in range(len(start)):
        for val in range(start[i], end[i]+1):
            for rest in codespace(start[i+1:], end[i+1:]):
                yield int_to_bytes(val, 1)+rest

class CMap(object):
    _data = None
    def __init__(self, cmap_data, parse=True):
        """Create a new CMap object from the data (typically the contents)
        of a CMap file or a CMap stream object."""
        if isinstance(cmap_data, str):
            cmap_data = cmap_data.decode()
        self._data = [clean_token(t)
                      for t in PdfParser().iterparse(cmap_data, True)]
        self._maps      = bidict()
        self._basemap   = None
        self._coderange = set()
        self._sys_info  = []
        if parse:
            self.parse()

    @classmethod
    def from_stream(cls, stream):
        """Parse a CMap stream into a CMap object"""
        return cls(stream.data)

    def parse(self, tokens=None, end_token=None):
        """Parse tokens or object's data file"""
        if tokens is None and self._data:
            tokens = deque(self._data)
        if not isinstance(tokens, deque):
            tokens = deque(tokens)
        results = []
        t = ''
        while tokens:
            t = tokens.popleft()
            if t == end_token:
                break
            if isinstance(t, str):
                try:
                    print('RANGES[t]', RANGES[t])
                    args = self.parse(tokens, RANGES[t])
                    print('args: ', args)
                except KeyError:
                    args = []
                    print('No args')
                #TODO: Try-except this
                try:
                    op = self.OPERATIONS[t]
                except TypeError:
                    results.append(t)
                else:
                    print('Doing ',t)
                    op(self, results, deque(args))
        return results

    def codespacerange(self, parsed, args):
        """Set the range of valid character codes"""
        pass#self._codes =

    def bfchar(self, parsed, args):
        """Remap individual character codes"""
        nvals = parsed.pop()
        for i in range(nvals):
            src  = args.popleft()
            dest = args.popleft()
            if isinstance(dest, int):
                self._maps[src] = self._base_map[dest]
            else:
                self._maps[src] = dest

    def bfrange(self, parsed, args):
        """Remap ranges of character codes"""
        nvals = parsed.pop()
        for i in range(nvals):
            low  = args.popleft()
            high = args.popleft()
            dest = args.popleft()
            if isinstance(dest, int):
                self._maps.update({low+j:self._base_map[dest+j]
                                   for j in codespace(low, high)})
            else:
                self._maps.update({j:dest[i]
                                   for i, j in enumerate(codespace(low, high))})

    def set_system_info(self, parsed, args):
        """Set the system info"""
        self._sys_info = args[0]

    # The various operators.  Somehow I like this more than a big
    # series of elifs
    OPERATIONS = {'beginbfchar'  : bfchar,
                  'beginbfrange' : bfrange,
                  'CIDSystemInfo': set_system_info,
                 }
