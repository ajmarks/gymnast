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
numbers, slope and y intercept.

Slope = b/a ([1 0]*[a b;c d] = [a b])
Intercept = f - b/a*e

TODO: Support vertical writing
"""

import collections
import io
import six
from intervaltree import IntervalTree

from .base_renderer  import PdfBaseRenderer
from ..pdf_operation import PdfOperation

class TextBlock(object):
    """Represents a block of text in the PDF output"""

    def __init__(self, space_width, cap_height, xmin, ymin,
                 text=None, xmax=None):
        self._space_width = space_width
        self._height      = cap_height
        self._text        = io.StringIO(text)
        self._ymin        = float(ymin)
        self._xmin        = float(xmin)
        self._xmax        = xmax if xmax else self._xmin

    def write_text(self, text, x, width):
        """Add new text to the next box, adding spacing based on the x
        coordinate."""
        self._text.write(text)
        self._xmax += width

    def get_spacing(self, width):
        """Returns an appropriate amount of spacing for a rightward shift of
        width based upon the current font.

        TODO: Tabs and such"""
        return round(width/self._space_width)*' '
    def fill_spaces(self, x_max):
        width = x_max - self._xmax
        self.write_text(self.get_spacing(width), 0, width)

    @property
    def font_height(self):
        """The height of a capital letter in the current font"""
        return self._height
    @property
    def text(self):
        return self._text.getvalue()

class PdfLineRenderer(PdfBaseRenderer):
    """More sophisticated page renderer.  Stores the result of each text
    showing operator in a TextBlock object, which are then assigned to lines
    on the page based on their line matrix and positions.  After the page has
    been processed, it goes over each line determining spacing based on the gap
    between successive TextBlocks in the line and width of the space character
    in the first of the two."""

    def _pre_render(self):
        """Prepare for rendering by initializing our lines aparatus"""
        self._lines = collections.defaultdict(list)

    def _render_text(self, string, new_state):
        x0, y0 = self.text_coords
        x1, y1 = new_state.current_coords
        self._text_block.write_text(string, x0, x1-x0)

    def _preop(self, op):
        """Initialize a new textbox with the currently active font and size
        at the current coordinates."""
        assert isinstance(op, PdfOperation)
        if op.optype == PdfOperation.TEXT_SHOWING:
            #self._last_coords = self.text_coords
            self._text_block = TextBlock(self._space_width,
                                         self._cap_height,
                                         self.text_coords[0],
                                         self.text_coords[1])
    def _move_text_cursor(self, T_m):
        x1, y1 = self._compute_T_rm(T_m=T_m).current_coords
        self._text_block.fill_spaces(x1)

    def _postop(self, op):
        if op.optype == PdfOperation.TEXT_SHOWING:
            self._lines[self._line_id].append(self._text_block)
        self._text_block = None

    def _return(self):
        #TODO: there's probably a better way to do this
        lines = list(six.iteritems(self._lines))
        return [i[1] for i in sorted(lines, key=lambda l: l[0][1])]

    @property
    def _line_id(self):
        """Get a unique id for this line.  See module docstring."""
        mat = self.ts.T_m
        slope = mat.a/mat.b
        return (slope, mat.f - mat.e*slope)

    @property
    def _space_width(self):
        """The width of a space in the current font"""
        # TODO: Use active_font.FontMatrix instead of division by 1000
        w0 = self.active_font.space_width/1000.0
        return (w0*self.ts.T_fs+self.ts.T_c+self.ts.T_w) * self._T_h

    @property
    def _cap_height(self):
        """The height of a capital letter in the current font"""
        # TODO: Use active_font.FontMatrix instead of division by 1000
        return self.active_font.FontDescriptor.CapHeight/1000.0*self.ts.T_fs
