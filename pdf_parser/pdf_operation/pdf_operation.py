import warnings

from ..exc  import *
from ..misc import get_subclasses, classproperty, ensure_str, MetaGettable




__all__ =['PdfOperation']

class PdfOperation(object, metaclass=MetaGettable):
    """PDF content stream operations."""
    opcode = None
    optype = None

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

    @staticmethod
    def do_opcode(renderer, *operands):
        raise NotImplementedError

    # Don't worry about anythign down here.  Just fill in the opcode, implement
    # do_opcode(), have a beer, and relax.
    __opcodes = None
    @classproperty
    def opcodes(cls):
        if PdfOperation.__opcodes is None:
            PdfOperation.__init_opcodes()
        return PdfOperation.__opcodes

    def __init__(self, *operands):
        self._operands = operands

    def __call__(self, renderer):
        return self.do_opcode(renderer, *self._operands)

    @classmethod
    def __getitem__(cls, operator):
        operator = ensure_str(operator)
        try:
            return cls.opcodes[operator]
        except KeyError:
            return type(operator, (PdfNOP,), {'_opcode':operator})

    @staticmethod
    def __init_opcodes():
        from . import operations
        opcodes = {ensure_str(o.opcode): o
                   for o in get_subclasses(PdfOperation)
                     if o.opcode}
        PdfOperation.__opcodes = opcodes
    def __str__(self):
        op = self.opcode if self.opcode else self._opcode
        return '{}({})'.format(op, ', '.join(str(i) for i in self._operands))

class PdfNOP(PdfOperation):
    """Dummy opcode that does nothing.  Called when we've not
    implemented a given opcode"""

    optype = PdfOperation.NOP
    def __call__(self, renderer):
        cname = self.__class__.__name__
        warnings.warn("Opcode '%s' not implemented.  NOP." % cname,
                      PdfOpWarning)
        return self.do_opcode(renderer, *self._operands)

    @staticmethod
    def do_opcode(renderer, *args):
        #Some logging stuff should go here
        pass