"""
The main PDF Document class
"""

from .exc           import PdfError, PdfParseError
from .misc          import buffer_data, read_until, force_decode, \
                           consume_whitespace, is_digit, ReCacher, \
                           int_from_bytes
from .pdf_constants import EOLS
from .pdf_parser    import PdfParser
from .pdf_types     import PdfHeader, PdfXref, PdfObjectReference, PdfDict

__all__ = ['PdfDocument']

class PdfDocument(object):
    """The main PDF Document class"""
    _opened_file = False

    def __init__(self, data):
        """Initialize a new PdfDocument based on data.

        Arguments:
            data - Either a binary string or a binary, readable stream
                   (e.g, BytesIO or a binary mode file)"""
        if isinstance(data, str):
            data = open(data, 'rb')
            self._opened_file = True
        self._data = buffer_data(data)
        self._parser = PdfParser(self)
        # These get used in parse()
        self._pages       = None
        self._version     = None
        self._ind_objects = {}
        self._xrefs       = None
        self._page_index  = None

    def parse(self):
        """Parse the data into a workable PDF document"""
        header         = self._get_header(self._data)
        xrefs, trailer = self._get_structure()

        self._version     = header.version
        self._xrefs       = xrefs
        self._build_doc(trailer)
        return self

    def _build_doc(self, trailer):
        """Use the information in trailer to build the document structure"""
        try:
            self._root = trailer['Root'].parsed_object
        except KeyError:
            raise PdfError('PDF file lacks a root element.  Is it protected?')
        self._version = trailer.get('Version', self._version)
        try:
            self._info = trailer['Info'].parsed_object
        except KeyError:
            self._info = None
        self._size = trailer['Size']
        try:
            self._encrypt = trailer['Encrypt'].parsed_object
        except KeyError:
            self._encrypt = None
        try:
            self._id = trailer['ID'].value
        except KeyError:
            self._id = None

    def parse_object(self, offset):
        """Parse the indirecte object located at the specified offset and add
        it to the documents objects dict, returning the stream position to its
        initial location"""
        pos = self._data.tell()
        obj = self._parser.parse_indirect_object(self._data, offset)
        self.indirect_objects[obj.object_key] = obj
        self._data.seek(pos)

    def __del__(self):
        """Cleanup on deletion"""
        if self._opened_file:
            self._data.close()

    def _get_structure(self, startxref=None):
        """Build the basic document structure.  Xrefs and trailers can come in
        two forms: either as literals in the file or as stream objects.  When
        presented as objects, the stream header also acts as the trailer, and
        the stream data is a set of xref records.  As far as I can tell, there
        is no rule against mixing and matching."""

        if not startxref:
            startxref = self._get_startxref(self._data)

        self._data.seek(startxref)
        if self._data.read(1).isdigit():
            xrefs, trailer = self._get_xref_stream(startxref)
        else:
            xrefs   = self._get_xref_table(startxref)
            trailer = self._get_trailer()
        try:
            new_xrefs, new_trailer = self._get_structure(trailer['Prev'])
        except KeyError:
            pass
        else:
            xrefs.update(new_xrefs)
            trailer.update(new_trailer)
        return xrefs, trailer

    @staticmethod
    def _get_header(data):
        """Return a PdfHeader object representing the header data from the PDF
        file in data"""
        data.seek(0)
        if data.read(1) != b'%':
            raise PdfParseError('PDF version header not found')
        hline = read_until(data, EOLS)
        hline = hline.decode()
        rc = ReCacher()
        if   rc.match(r'PDF\-(\d+\.\d+)$', hline):
            header = PdfHeader(rc.group(1))
        elif rc.match(r'\!PS\?Adobe\?(\d+.\d+) PDF\?(\d+\.\d+)$', hline):
            header = PdfHeader(rc.group(2), rc.group(1))
        else:
            raise PdfError('Invalid PDF version header')
        return header

    @staticmethod
    def _get_startxref(data):
        """Gets the final startxref position from the data stream."""
        # This seems like too much, but for some reason Adobe readers allow
        # %%EOF to be anywhere in the last 1024 bytes
        data.seek(-1024, 2)
        chunk = data.read(1024)
        eof = chunk.find(b'%%EOF')
        if eof < 0:
            raise PdfParseError('EOF marker not found')

        #This silliness avoids a weird corner case where there's an incremental
        #update <1KB long, resulting in multiple %%EOF markers in the last KB
        #of the file.  Of course, if Adobe would just stick to their standard
        #and insist that %%EOF be the absolute last thing, we could just grab
        #the final 29 bytes above and skip this.
        eof2 = chunk.find(b'%%EOF', eof+1)
        while eof2 > 0:
            eof  = eof2
            eof2 = chunk.find(b'%%EOF', eof+1)

        # The offset can never be more than 10 digits, so the two startxref
        # lines combined will, at most, be 'startxref\r\n1234567890\r\n', which
        # is 23 characters long
        lines = chunk[eof-23:eof].splitlines()[-2:]
        if lines[0] != b'startxref' or not lines[1].isdigit():
            raise PdfParseError('startxref not found')
        return int(lines[1])

    def _get_xref_table(self, offset):
        """Get the data in an xref table located at the specified offset.
        These have a very specific format described on pp. 93-97 of the
        Adobe PDF Reference. Here's the short version:

        The first line will be just the token 'xref'.
        Following that will be one or more xref subsections consisting first of
        a line with two integers (e.g. "0 35"), which we will term obj_0 and m,
        and m xref lines, of the form oooooooooo ggggg n eol, where o and g are
        digits, n is either 'f' or 'n' and eol is a two character line end
        sequence (though not necessarily \\r\\n; it could be, e.g., ' \\n').
        If the ith xref line (counting from 0) in a subsection is
        0000001000 00007 n\\r\\n, that means that object (obj_0+i, 00007) is
        located at offset 1000 into the file and that it is in use.

        Returns a dict with keys (objno, generation) and PdfXref objects as
        values."""

        data = self._data
        data.seek(offset)
        token = self._data.read(4)
        if token != b'xref':
            msg = "Expected 'xref', found '{}'."
            raise PdfParseError(msg.format(force_decode(token)))
        consume_whitespace(data, EOLS)
        xrefs = {}
        while is_digit(data.peek(1)[0]):
            xrefs.update(self._get_xref_subsection())
        return xrefs

    def _get_xref_stream(self, offset):
        """Extract Xrefs from a cross reference stream located at the specified
        offset.  See pp. 106 - 109."""
        obj = self._parser.parse_indirect_object(self._data, offset)
        return self.parse_xref_obj(obj)

    def parse_xref_obj(self, obj):
        stream = obj.value
        header = stream.header
        if header['Type'] != 'XRef':
            raise PdfError('Type "XRef" expected, got "{}"'.format(header['Type']))
        id0 = header.get('Index', (0,))[0]
        # Field widths.  Because of PDF's affinity for micro-optimation via
        # default values, the first first may be skipped, in which case
        widths = header['W']
        if len(widths) == 2:
            widths.insert(0, 0)
        recsize = sum(widths)
        data = stream.data
        # Divide, parse, and dictify
        recs = [(id0 + i, data[i*recsize:(i+1)*recsize])
                for i in range(header['Size'])]
        xrefs = (self._parse_xrefstrm_rec(r[0], r[1], widths) for r in recs)
        xrefs = {(x['object_id'], x['generation']): x for x in xrefs}
        return xrefs, header

    def _parse_xrefstrm_rec(self, obj_id, data, widths):
        if widths[0] == 0:
            rec_type = 1
        else:
            rec_type = int_from_bytes(data[:widths[0]])
        val_2 = data[widths[0]:widths[1]]
        val_3 = data[widths[1]:] # Type and obj_no are 1 and 2
        if rec_type == 0:
            return PdfXref(self, obj_id, val_2, val_3, False)
        if rec_type == 1:
            return PdfXref(self, obj_id, val_2, val_3 if widths[2] else 0, True)
        if rec_type == 2:
            #TODO
            raise NotImplementedError('Object streams not yet implemented')

    def _get_xref_subsection(self):
        """Exctract an Xref subsection from data.  This method assumes data's
        stream position to already be at the start of the subsection and leaves
        it at the start of the next line. Returns a dict with keys
        (objno, generation) and PdfXref objects as values."""
        header = read_until(self._data, EOLS)
        id0, nlines = map(int, header.split())
        consume_whitespace(self._data, EOLS)
        lines = self._data.read(20*nlines).decode().splitlines()
        consume_whitespace(self._data, EOLS)
        return {x.key: x for x in (PdfXref.from_line(self, id0+i, l)
                                   for i, l in enumerate(lines))}

    def _get_trailer(self):
        """Gets a document trailer located at the current stream position.
        Trailers are described in the reference on pp. 96-98, and consist of
        the keyword "trailer" followed by a dictionary.  We might not have a
        trailer, so then return an empty PdfDict and rewind."""
        data = self._data
        consume_whitespace(data)
        token = self._data.read(7)
        if token != b'trailer':
            data.seek(-len(token), 1)
            return PdfDict()
        return self._parser.parse_simple_object(data)

    @property
    def Root(self):
        """Document's Root element"""
        return self._root
    @property
    def Info(self):
        return self._info
    @property
    def Size(self):
        return self._size
    @property
    def Encrypt(self):
        return self._encrypt
    @property
    def ID(self):
        return self._id

    @property
    def Pages(self):
        """Flattened list of pages"""
        if self._pages is None:
            self._pages = self._build_page_list(self.Root.Pages)
        return self._pages

    def get_page_index(self, page):
        """Retrieve the index into self.Pages for the given page"""
        if self._page_index is None:
            self._page_index = {k:v for v, k in 
                                enumerate(p.unique_id for p in self.Pages)}
        return self._page_index.get(page.unique_id)

    @classmethod
    def _build_page_list(cls, page):
        """Build the list of page objects by recursively descending the page
        node tree"""
        try:
            return sum((cls._build_page_list(p) for p in page.Kids), [])
        except AttributeError:
            return [page]

    @property
    def indirect_objects(self):
        """Dict-like of all of the indirect objects defined in the document"""
        return self._ind_objects
    def get_object(self, object_number, generation):
        """Get the indirect object referenced"""
        try:
            return self._xrefs[(object_number, generation)].value
        except KeyError:
            raise PdfError('No object exists with that number and generation')

class PdfElementList(object):
    """List-like object that auto-deferences its PDF object elements"""
    def __init__(self, *args, **kwargs):
        self._list = list(*args, **kwargs)
    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self._get_value(i) for i in self._list[key]]
        else:
            return self._get_value(self._list[key])
    def __delitem__(self, key):
        self._list.__delitem__(key)
    def __len__(self):
        return self._list.__len__()
    def __str__(self):
        return str(self._list)
    def __repr__(self):
        return repr(self._list)

    @staticmethod
    def _get_value(item):
        if isinstance(item, PdfObjectReference):
            return item.value
        else:
            return item
