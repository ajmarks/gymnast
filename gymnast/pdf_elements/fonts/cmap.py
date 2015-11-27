"""
CIDMap objects

See Reference pp. 441-452, and 472-475 for an overview. Full treatment at
http://www.adobe.com/content/dam/Adobe/en/devnet/font/pdfs/5014.CIDFont_Spec.pdf
"""

from bidict      import bidict
from collections import deque

from ...pdf_parser import PdfParser
from ...pdf_types  import PdfRaw, PdfName
from ...misc       import int_from_bytes, int_to_bytes, defaultlist
from copy import copy, deepcopy


RANGE_OPS = {'usematrix', 'codespacerange', 'cmap',
             'bfchar', 'bfrange', 'cidchar','cidrange',
             'notdefchar', 'notdefrange', 'rearrangedfont', ''}
OTHER_OPS = {'usecmap', 'usefont'}
PARAMS    = {'/CIDSystemInfo', '/CMapName', '/CMapType'}
RANGES = {'begin'+b:'end'+b for b in RANGE_OPS}
RANGES.update({p:'def' for p in PARAMS})

class CMap(object):
    _data = None
    def __init__(self, cmap_data, parse=True):
        """Create a new CMap object from the data (typically the contents)
        of a CMap file or a CMap stream object."""
        if isinstance(cmap_data, str):
            cmap_data = cmap_data.decode()
        self._data = [clean_token(t)
                      for t in PdfParser().iterparse(cmap_data, True)]
        self._maps       = bidict()
        self._basemap    = None
        self._coderanges = defaultlist(set)
        self._sys_info   = []
        if parse:
            self._results = self.parse()
        input()

    @classmethod
    def from_stream(cls, stream):
        """Parse a CMap stream into a CMap object"""
        return cls(stream.data)

    def in_code_range(self, byte_code):
        """Returns True if byte_code is in the CMaps' code range"""
        for i in range(1, len(self._coderanges)):
            if byte_code[:i] in self._coderanges[i]:
                return True
        return False

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
            try:
                new_end = RANGES[t]
            except (KeyError, TypeError):
                args = []
            else:
                args = self.parse(tokens, new_end)

            try:
                op = self.OPERATIONS[t]
            except (KeyError, TypeError):
                results.append(t)
                if args:
                    results.append(args)

            else:
                result = op(self, results, deque(args))
                if result:
                    results.append(result)
        return results

    def codespacerange(self, parsed, args):
        """Set the range of valid character codes"""
        nvals = parsed.pop()
        for i in range(nvals):
            low  = args.popleft()
            high = args.popleft()
            self._coderanges[len(low)] |= {c for c in codespace(low, high)}
        if self._basemap is None:
            self._basemap = {b:b for cr in self._coderanges for b in cr}

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
            elif isinstance(dest, bytes):
                dims = coderange_dims(low, high)
                self._maps.update({i:self._base_map[j]
                                   for i, j in zip(codespace(low,  dimensions=dims),
                                                   codespace(dest, dimensions=dims))})
            else:
                self._maps.update({j:dest[i]
                                   for i, j in enumerate(codespace(low, high))})

    def set_system_info(self, parsed, args):
        """Set the system info"""
        self._sys_info = args[0]

    # The various operators.  Somehow I like this more than a big
    # series of elifs
    OPERATIONS = {'beginbfchar'        : bfchar,
                  'beginbfrange'       : bfrange,
                  'begincodespacerange': codespacerange,
                  '/CIDSystemInfo'     : set_system_info,
                 }

def clean_token(token):
    """Convert PdfRaw tokens to strings"""
    if isinstance(token, PdfRaw):
        return token.decode()
    elif isinstance(token, PdfName):
        #TODO: do something better than this gross hack
        return PdfName('/'+token)
    else:
        return token

def coderange_dims(start, end):
    """Code range dimensions between bytecodes"""
    if len(start) != len(end):
        raise ValueError('start and end must have the same dimesionality')
    dims = [e-s for s, e in zip(start, end)]
    if any(d < 0 for d in dims):
        raise ValueError('Invalid range')
    return dims

def codespace(start, end=None, dimensions=None):
    """Build a range of values representing a code range"""
    if not(bool(end) ^ (dimensions is not None)):
        raise ValueError('An end or dimensions must be provided')
    if end:
        dimensions = coderange_dims(start, end)
    dim = len(dimensions)
    if dim > len(start):
        raise ValueError('Too many dimensions')
    if not start:
        yield b''
        raise StopIteration
    for val in range(start[-dim], dimensions[0] + 1):
        for rest in codespace(start[-dim:][1:],
                              dimensions=dimensions[1:]):
            yield int_to_bytes(val, 1)+rest