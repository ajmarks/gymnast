"""
More complex page renderer that extracts the text based on the following plan:

1. Each text showing operation is parsed into a TextBlock object:
2. After a TextBlock is created, it is assigned to a TextLine:
   a. TextLines are assigned based on the line matrix and position.
   b. If no line is matched, a new one is created for that text box.
3. After the entire page is parsed, the text is extracted:
   a. The TextBlocks in each line are sorted by left-most edge.
   b. The texts from each of the line's TextBlock are concatenated together
      with spaces added between LeftBlock and RightBlock based on the space
      between the two blocks and the space width in LeftBlock's font.
   c. Lines are sorted vertically based on their midpoints, and concatenated
      together with newlines (TODO: blank lines as appropriate).

Some background on the math.  Transformation matrices are 3x3 invertible
matrices of the form
                                      [ a b 0 ]
        PdfMatrix(a, b, c, d, e, f) = [ c d 0 ].
                                      [ e f 1 ]
Points are represented as element row vectors [x y 1] with matrices acting on
points by right multiplication.  This is equivalent then to treating points as
[x y], and breaking down the matrix into multiplication and addition:
[x' y'] = [x y]*[a b;c d] + [e f].  This also matches what happens with Tm: it
implicitly applies the line matrix transformation and a translation.

Now, the important part:
For the purposes of determining lines, we don't care about scaling factors, so,
ignoring text rotated 90 or -90 degrees, we can uniquely idenitify lines by two
numbers, slope and y intercept, where

Slope = b/a ([1 0]*[a b;c d] = [a b]) and
Intercept = f - b/a*e.

These numbers are then rounded to one decimal place to prevent visually
indistiguishable items from being placed on different lines.  This correction
will probably be made more sophisticated in the future.

TODO: Support vertical writing
"""

import collections
import io
import six

from .base_renderer  import PdfBaseRenderer
from ..pdf_operation import PdfOperation

class TextBlock(object):
    """Represents a block of text in the PDF output"""

    def __init__(self, xmin, space_width, tab_width=None):
        """Initialize a new text box at the specified x coordinate with the
        space character width and tab width (in terms of spaces)"""
        self._xmin        = float(xmin)
        self._space_width = float(space_width)
        self._tab_width   = float(tab_width) if tab_width else None
        self._text        = io.StringIO()
        self._width       = 0

    @property
    def xbounds(self):
        """Horizontal coordinate lower and upper bounds"""
        return (self._xmin, self._xmin+self._width)

    def get_no_spaces(self, width):
        return int(width/self._space_width)

    def write_text(self, text, width, x=None):
        """Add new text to the next box, adjusting the box width and adding
        spacing based on the x coordinate if provided."""
        if x:
            self.fill_spaces(x)
        self._text.write(text)
        self._width += width

    def get_spacing(self, x):
        """Returns an appropriate amount of spacing between the current end of
        the block and the x coordinate."""
        dist = x - self._xmin - self._width
        spaces = dist/self._space_width
        if self._tab_width and spaces >= self._tab_width:
            return '\t'
        else:
            return int(spaces)*' '

    def fill_spaces(self, x):
        """Fill in enough spaces to reach the specified x coordinate"""
        self._text.write(self.get_spacing(x))
        self._width = x - self._xmin

    @property
    def text(self):
        return self._text.getvalue()

class PdfTextRenderer(PdfBaseRenderer):
    """More sophisticated page renderer.  Stores the result of each text
    showing operator in a TextBlock object, which are then assigned to lines
    on the page based on their line matrix and positions.  After the page has
    been processed, it goes over each line determining spacing based on the gap
    between successive TextBlocks in the line and width of the space character
    in the first of the two."""

    def __init__(self, page, fixed_width=True, tab_width=None):
        """Text line extractor.

        Arguments:
            page - The PdfPage to parse
            fw_spaces - Should spaces be approximate as fixed width?
            tab_width - Replaces this many spaces with a tab (default None)"""
        super(PdfTextRenderer, self).__init__(page)
        self._lines       = collections.defaultdict(list)
        self._tab_width   = tab_width
        self._fixed_width = fixed_width

    def _render_text(self, string, new_state):
        """Add the text to the active text block"""
        x0 = self.text_coords[0]
        x1 = new_state.current_coords[0]
        self._text_block.write_text(string, x1-x0, x0)

    def _preop(self, op):
        """If the operation is a text showing one, initialize a new textbox
        with the currently active font and size at the current coordinates."""
        if op.optype == PdfOperation.TEXT_SHOWING:
            if self._fixed_width:
                space_width = self._avg_width
            else:
                space_width = self._space_width
            self._text_block = TextBlock(self.text_coords[0],
                                         space_width,
                                         self._tab_width)

    def _postop(self, op):
        """If we were in a text showing operation, add it to a line"""
        if op.optype == PdfOperation.TEXT_SHOWING:
            self._lines[self._line_id].append(self._text_block)
        self._text_block = None

    def _return(self):
        """Return the extracted text"""
        #IDEA: there's probably a better way to do this
        lines = list(six.iteritems(self._lines))
        return [self._join_blocks(i[1], self._fixed_width)
                for i in sorted(lines, key=lambda l: -l[0][1])]

    @property
    def _line_id(self):
        """Get a unique id for this line.  See module docstring."""
        mat = self.ts.m
        # Sometimes PDF writers will play games with rise instead of moving to
        # a new line, so we need to add a correction
        y_adj = (self.ts.rise <= -self._line_height)*self.ts.rise
        slope = mat.a/mat.b if mat.b else 0
        return (round(slope,1),
                round(mat.f - y_adj + mat.e*slope, 1))

    @property
    def _line_height(self):
        """The text-space y offset between lines"""
        if self.ts.l:
            return self.ts.l
        return self.active_font.FontDescriptor.CapHeight

    @property
    def _space_width(self):
        """The width of a space in the current font, transformed to text space
        and then to user-space"""
        w0 = self._gs_to_ts(self.active_font.space_width, 1)[0]
        return w0 * self.ts.fs * self.ts.h * self.ts.m.a

    @property
    def _avg_width(self):
        """The width of a typical character in the current font, transformed to
        text space and then to user-space"""
        w0 = self._gs_to_ts(self.active_font.avg_width, 1)[0]
        return w0 * self.ts.fs * self.ts.h * self.ts.m.a

    def _join_blocks(self, blocks, fixed_width):
        """Join together a list of text blocks, adding space as needed"""
        blocks.sort(key=lambda b: b.xbounds[0])
        prev_block = blocks[0]
        if fixed_width:
            text = ' '
            for block in blocks:
                width = block.xbounds[0]-self._page.CropBox[0]
                text += ' '*(block.get_no_spaces(width)-len(text)) + block.text
            return text
        else:
            sio = io.StringIO()
            sio.write(blocks[0].text)
            for block in blocks[1:]:
                sio.write(prev_block.get_spacing(block.xbounds[0]))
                sio.write(block.text)
                prev_block = block
            return sio.getvalue()
