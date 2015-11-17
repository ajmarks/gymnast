"""
More complex page renderer that extracts the text based on the following plan:

1. Each text showing operation is parsed into a TextBlock object:
   a. This is done glyph-by-glyph
   b. Spaces are inserted between glyphs based on the distance from the end
      of the previous glyph, the start of the new one, and width of the space
      in the current font.
   c. The height of the TextBlock is that of the font's capital letters.
2. After a TextBlock is created, it is assigned to a TextLine:
   a. TextLines are assigned based on simple geometric intersection.
   b. If no line is matched, a new one is created for that text box and is
      assigned the middle third of that TextBlock's vertical span.
   c. TODO: If multiple lines are matched, take the one with the largest overlap
3. After the entire page is parsed, the text is extracted:
   a. The TextBlocks in each line are sorted by left-most edge.
   b. The texts from each of the line's TextBlock are concatenated together
      with spaces added between LeftBlock and RightBlock based on the space
      between the two blocks and the space width in LeftBlock's font.
   c. Lines are sorted vertically based on their midpoints, and concatenated
      together with newlines (TODO: blank lines as appropriate).
"""
import io
import six
from intervaltree import IntervalTree

from .base_renderer  import PdfBaseRenderer
from ..pdf_operation import PdfOperation


class TextLine(object):
    """Class representing a unique line of text on the page"""
    def __init__(self, ymin, ymax):
        self._texts     = []
        self._interval = slice(ymin, ymax)

    def extract_text(self):
        self._texts.sort(key=lambda t: t._xmin)
        text  = io.StringIO()
        prev = self._texts[0]
        for t in self._texts:
            text.write(prev.spaces_to(t)) #TODO: tabs
            text.write(t.text)
        return text.getvalue()
    def add_text(self, text_block):
        self._texts.append(text_block)
    @property
    def interval(self):
        return (self._interval.start, self._interval.stop)

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
    @property
    def interval(self):
        return slice(self._ymin, self._ymin+self._height)
    def space_to(self, next_block):
        """Convenience method to get spacing to the next block."""
        return self.get_spacing(next_block._xmin-self._xmax)


class PdfTextRenderer(PdfBaseRenderer):
    """More sophisticated page renderer.  Stores the result of each text
    showing operator in a TextBlock object, which are then assigned to lines
    on the page based on their vertical coordinates.  After the page has been
    processed, it goes over each line determining spacing based on the gap
    between successive TextBlocks in the line and width of the space character
    in the first of the two.

    TODO: Add support for vertical text direction and RTL languages"""

    def _pre_render(self):
        """Prepare for rendering by initializing our lines aparatus"""
        self._tree = IntervalTree()

    def _render_text(self, string, new_state):
        x0, _ = self.text_coords
        x1, _ = new_state.current_coords
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
        x1, _ = self._compute_T_rm(T_m=T_m).current_coords
        self._text_block.fill_spaces(x1)
    def _postop(self, op):
        if op.optype == PdfOperation.TEXT_SHOWING:
            self._block_to_line()
        self._text_block = None
    def _return(self):
        lines = [i[-1] for i in self._tree.all_intervals]
        lines.sort(key=lambda l: l.interval[1], reverse=True)
        return lines

    def _new_line(self, ymin, ymax):
        line = TextLine(ymin, ymax)
        self._tree[line.interval] = line
        return line

    def _block_to_line(self):
        block = self._text_block
        lines = self._tree[block.interval]
        if not lines:
            # TODO: customize this interval
            low  = block.interval.start
            high = block.interval.stop
            line = self._new_line((2*low+high)/3.0, (2*high+low)/3.0)
        else:
            #TODO: Pick the line more intelligently when there are multiple
            #matches
            line = six.next(iter(lines)).data
        line.add_text(block)

    @property
    def _space_width(self):
        """The width of a space in the current font"""
        # TODO: Use active_font.FontMatrix instead of division by 1000
        w0 = self.active_font.space_width/1000.0
        return (w0*self.ts.T_fs+self.ts.T_c+self.ts.T_w) * self.ts.T_h

    @property
    def _cap_height(self):
        """The height of a capital letter in the current font"""
        # TODO: Use active_font.FontMatrix instead of division by 1000
        return self.active_font.FontDescriptor.CapHeight/1000.0*self.ts.T_fs
