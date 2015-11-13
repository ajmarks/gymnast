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
    def __init__(self, a, b, c, d, e, f):
        """Create a new PdfMatrix object.  Arguments real numbers and represent
        a matrix as described on p. 208 of the Reference:
                                      [ a b 0 ]
        PdfMatrix(a, b, c, d, e, f) = [ c d 0 ]
                                      [ e f 1 ]
        """
        self._a = float(a)
        self._b = float(b)
        self._c = float(c)
        self._d = float(d)
        self._e = float(e)
        self._f = float(f)
    def transform_coords(self, x, y):
        return (self._a*+self._c*y+self._e, 
                self._b*+self._d*y+self._f)
    def __mul__(self, other):
        """Matrix multiplication.
        Given the type constraint below, this will be self*other"""
        if not isinstance(other, PdfMatrix):
            raise TypeError('Can only multiply PdfMatrices by PdfMatrice')
        return PdfMatrix(self._a*other._a+self._b*other._c,
                         self._a*other._b+self._b*other._d,
                         self._c*other._a+self._d*other._c,
                         self._c*other._b+self._d*other._d,
                         self._e*other._a+self._f*other._c+other._e,
                         self._e*other._b+self._f*other._d+other._f)
    @property
    def current_coords(self):
        """Current x, y offset in whatever space this matrix represents"""
        return self._e, self._f
    def copy(self):
        """Return a copy of this matrix"""
        return PdfMatrix(self._a, self._b,
                         self._c, self._d,
                         self._e, self._f)