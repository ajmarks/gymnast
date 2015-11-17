"""
PDF Operations base class
"""

import inspect
import six
import warnings
from ..exc  import PdfOpWarning
from ..misc import ensure_str, MetaGettable

__all__ =['PdfOperation']


@six.add_metaclass(MetaGettable)
class PdfOperation(object):
    """PDF content stream operations dispatcher.  Content stream operations are
    registered by calling PdfOperation.register(), passing the opcode, the type
    of operation, and the function that does it."""
    # Operation type constants (see Reference p. 196)
    # These mostly exist to make things easier in PdfRenderer methods
    NOP                    =     0
    GENERAL_GRAPHICS_STATE =     1
    SPECIAL_GRAPHICS_STATE =     2
    PATH_CONSTRUCTION      =     4
    PATH_PAINTING          =     8
    CLIPPING_PATHS         =    16
    TEXT_OBJECTS           =    32
    TEXT_STATE             =    64
    TEXT_POSITIONING       =   128
    TEXT_SHOWING           =   256
    TYPE_3_FONTS           =   512
    COLOR                  =  1024
    SHADING_PATTERNS       =  2048
    INLINE_IMAGES          =  4096
    XOBJECTS               =  8192
    MARKED_CONTENT         = 16384
    COMPATIBILITY          = 32768

    _opcodes = {}
    _nops    = {} # As we spawn new NOP classes, we'll cache them here
    @classmethod
    def register(cls, opcode, optype, opfunc):
        """Register a new PDF operation.  Arguments are the opcode, the type of
        operation, and the function that actually does the operation."""
        opcode = ensure_str(opcode)
        if not callable(opfunc):
            raise TypeError('opfunc must be callable')
        args = inspect.getfullargspec(opfunc)
        if not (args.varargs or args.args):
            raise ValueError('opfunc must take at least one positional argument')
        opcode = ensure_str(opcode)
        cls._opcodes[opcode] = new_opcode(opcode, optype, opfunc)

    @classmethod
    def __getitem__(cls, operator):
        operator = ensure_str(operator)
        try:
            return cls._opcodes[operator]
        except KeyError:
            return cls._nop(operator)
    @classmethod
    def _nop(cls, operator):
        """Get the corresponding NOP operation, creating it if necessary."""
        warnings.warn("Opcode '{}' not implemented. NOP".format(operator),
                      PdfOpWarning)
        try:
            return cls._nops[operator]
        except KeyError:
            tpe = new_opcode(operator, 0, lambda *x: None)
            cls._nops[operator] = tpe
            return tpe

class PdfBaseOp(object):
    """Base class for all pdf operations"""
    opcode = None
    optype = None
    opfunc = lambda x: None
    def __init__(self, *operands):
        self._operands = operands
    def __call__(self, renderer):
        return (self.opfunc.__func__)(renderer, *self._operands)
    def __str__(self):
        op = self.opcode if self.opcode else self._opcode
        return '{}({})'.format(op, ', '.join(str(i) for i in self._operands))

def new_opcode(opcode, optype, opfunc):
    """Create a new PDF operation based on the arguments"""
    class_data = {'opcode': opcode, 'optype':optype, 'opfunc':opfunc}
    return type(opcode, (PdfBaseOp, ), class_data)
