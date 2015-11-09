import warnings

from .exc            import *
from .misc           import get_subclasses, classproperty, ensure_str

#PTVS nonsense
from builtins import *

class PdfOperationMeta(type):
    def __getitem__(cls, operator):
        operator = ensure_str(operator)
        try:
            return cls.opcodes[operator]
        except KeyError:
            return type(operator, (PdfNOP,), {})

class PdfOperation(object, metaclass=PdfOperationMeta):
    """PDF content stream operations."""
    opcode = None
    
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

    @staticmethod
    def __init_opcodes():
        from .opcodes.text_objects     import BT, ET
        from .opcodes.text_state       import Tc, Tw, Tz, TL, Tf, Tr, Ts
        from .opcodes.text_positioning import Td, TD, Tm, Tstar
        from .opcodes.text_showing     import Tj, TJ, Apostrophe, Quote
        opcodes = {ensure_str(o.opcode): o
                   for o in get_subclasses(PdfOperation)
                     if o.opcode}
        PdfOperation.__opcodes = opcodes

        

class PdfNOP(PdfOperation):
    """Dummy opcode that does nothing.  Called when we've not 
    implemented a given opcode"""
    def __call__(self, renderer):
        cname = self.__class__.__name__
        warnings.warn("Opcode '%s' not implemented.  NOP." % cname,
                      PdfOpWarning)
        return self.do_opcode(renderer, *self._operands)

    @staticmethod
    def do_opcode(renderer, *args):
        #Some logging stuff should go here
        pass