"""
Very simple matrix class for PDF transformation matrices.

PDF Transformations are represented as 3x3 real matrices, the last column of
which is always [0, 0, 1]^T.  Besides assignment, they're used in exactly two
ways: either multiplication by another transformation matrix or left
multiplication by a coordinate row vector [x, y, 1], so using (and thus
requiring) numpy for this seemed like massive overkill.

In the interests of compatability, we're not going to rely on Python 3.5's
matrix multiplication operator, though it does support it.
"""

__all__ = ['PdfMatrix']

class PdfMatrix(object):
    """Very limited matrix class representing PDF transformations"""
    def __init__(self, a, b, c, d, e, f):
        """Create a new PdfMatrix object.  Arguments real numbers and represent
        a matrix as described on p. 208 of the Reference:
                                      [ a b 0 ]
        PdfMatrix(a, b, c, d, e, f) = [ c d 0 ]
                                      [ e f 1 ]
        """
        self.a = float(a)
        self.b = float(b)
        self.c = float(c)
        self.d = float(d)
        self.e = float(e)
        self.f = float(f)
    def transform_coords(self, x, y):
        return (self.a*+self.c*y+self.e,
                self.b*+self.d*y+self.f)
    def __mul__(self, other):
        """Matrix multiplication.
        Given the type constraint below, this will be self*other"""
        if not isinstance(other, PdfMatrix):
            raise TypeError('Can only multiply PdfMatrices by PdfMatrice')
        return PdfMatrix(self.a*other.a+self.b*other.c,
                         self.a*other.b+self.b*other.d,
                         self.c*other.a+self.d*other.c,
                         self.c*other.b+self.d*other.d,
                         self.e*other.a+self.f*other.c+other.e,
                         self.e*other.b+self.f*other.d+other.f)
    @property
    def current_coords(self):
        """Current x, y offset in whatever space this matrix represents"""
        return self.e, self.f
    def copy(self):
        """Return a copy of this matrix"""
        return PdfMatrix(self.a, self.b,
                         self.c, self.d,
                         self.e, self.f)
