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
import math
import six

from .base_renderer  import PdfBaseRenderer
from ..pdf_operation import PdfOperation

class TextBlock(object):
    """Represents a block of text in the PDF output"""

    def __init__(self, xmin, space_width, fixed_width):
        """Initialize a new text box at the specified x coordinate with the
        space character width and tab width (in terms of spaces)"""
        self._xmin        = float(xmin)
        self._space_width = float(space_width)
        self._fixed_width = bool(fixed_width)
        self._text        = io.StringIO()
        self._width       = 0.0

    @property
    def xbounds(self):
        """Horizontal coordinate lower and upper bounds"""
        return (self._xmin, self._xmin+self._width)

    @property
    def space_width(self):
        """The width of a space in the current font"""
        return self._space_width

    def write_text(self, text, width, x=None):
        """Add new text to the next box, adjusting the box width and adding
        spacing based on the x coordinate if provided."""
        if x:
            self.fill_spaces(x)
        self._text.write(text)
        self._width += width

    def get_no_spaces(self, width):
        """Get the number of spaces needed to fill the specified width (in text
        space units)."""
        spaces = width/self._space_width
        if self._fixed_width and spaces >= .8:
            text_len = len(self._text.getvalue())
            return round((self._width+width)/self._space_width)-text_len
        elif self._fixed_width:
            return 0
        else:
            return round(width/self._space_width)

    def fill_spaces(self, x):
        """Fill in enough spaces to reach the specified x coordinate"""
        spaces = self.get_no_spaces(x - self._xmin - self._width)
        self._text.write(' '*spaces)
        self._width = x - self._xmin

    @property
    def text(self):
        """The text string in the block"""
        return self._text.getvalue()

class PdfTextRenderer(PdfBaseRenderer):
    """More sophisticated page renderer.  Stores the result of each text
    showing operator in a TextBlock object, which are then assigned to lines
    on the page based on their line matrix and positions.  After the page has
    been processed, it goes over each line determining spacing based on the gap
    between successive TextBlocks in the line and width of the space character
    in the first of the two."""

    def __init__(self, page, fixed_width=True):
        """Text line extractor.

        Arguments:
            page - The PdfPage to parse
            fw_spaces - Adjust spacing to render to preserve format in a fixed
                        width font (default True)"""
        super(PdfTextRenderer, self).__init__(page)
        self._lines       = collections.defaultdict(list)
        self._fixed_width = fixed_width
        self._line_sizes  = collections.defaultdict(int)

    def _render_text(self, string, new_state):
        """Add the text to the active text block, and update the active font's
        glyph count"""
        x0 = self.text_coords[0]
        x1 = new_state.current_coords[0]
        self._text_block.write_text(string, x1-x0, x0)
        cap_height  = self.active_font.FontDescriptor.CapHeight
        cap_height  = self.active_font.text_space_coords(0, cap_height)[1]
        cap_height *= self.ts.fs*self.ts.m.d
        self._line_sizes[round(cap_height,1)] += len(string)

    def _preop(self, op):
        """If the operation is a text showing one, initialize a new textbox
        with the currently active font and size at the current coordinates."""
        if op.optype == PdfOperation.TEXT_SHOWING:
            if self._fixed_width:
                space_width = self._avg_width
            else:
                space_width = self._space_width
            self._text_block = TextBlock(self.text_coords[0], space_width,
                                         self._fixed_width)

    def _postop(self, op):
        """If we were in a text showing operation, add it to a line"""
        if op.optype == PdfOperation.TEXT_SHOWING:
            self._lines[self._line_id].append(self._text_block)
        self._text_block = None

    def _return(self):
        """Return the extracted text"""
        # Median line size
        line_size = max(self._line_sizes, key=self._line_sizes.get)
        lines = sorted(six.iteritems(self._lines), key=lambda l: -l[0][1])
        dist_lines = [lines[0]]
        for l in lines[1:]:
            # Does the top of this line cross the bottom of the one above?
            if l[0][1] + line_size >= dist_lines[-1][0][1]:
                dist_lines[-1][1].extend(l[1])
            else:
                dist_lines.append(l)
        return '\n'.join([self._join_blocks(i[1], self._fixed_width)
                          for i in dist_lines])
        ## IDEA: Add option to include blank lines as below
        #text_lines = [(i[0][1], self._join_blocks(i[1], self._fixed_width))
        #               for i in dist_lines]
        #results = io.StringIO()
        #results.write(text_lines[0][1])
        #for i in range(1, len(text_lines)):
        #    new_lines = round((text_lines[i-1][0]-text_lines[i][0])/line_size)
        #    results.write('\n'*new_lines+text_lines[i][1])
        #return results.getvalue()

    @property
    def _line_id(self):
        """Get a unique id for this line.  See module docstring."""
        mat = self.ts.m
        # Sometimes PDF writers will play games with rise instead of moving to
        # a new line, so we need to add a correction
        y_adj = (self.ts.rise <= -self._line_height)*self.ts.rise
        slope = mat.a/mat.b if mat.b else 0
        return (round(slope),
                mat.f - y_adj + mat.e*slope)

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
        w0 = self.active_font.space_width
        return w0 * self.ts.fs * self.ts.h * self.ts.m.a

    @property
    def _avg_width(self):
        """The width of a typical character in the current font, transformed to
        text space and then to user-space"""
        w0 = self.active_font.avg_width
        return w0 * self.ts.fs * self.ts.h * self.ts.m.a

    def _join_blocks(self, blocks, fixed_width):
        """Join together a list of text blocks, adding space as needed"""
        blocks.sort(key=lambda b: b.xbounds[0])
        sio = io.StringIO()
        if fixed_width:
            spaces = ' '*round( (blocks[0].xbounds[0]-self._page.CropBox[0]) \
                         /blocks[0].space_width)
            sio.write(spaces)
        sio.write(blocks[0].text)
        prev_block = blocks[0]
        for block in blocks[1:]:
            width = block.xbounds[0] - prev_block.xbounds[1]
            sio.write(' '*block.get_no_spaces(width) + block.text)
            prev_block = block
        return sio.getvalue()