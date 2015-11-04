from exc                  import *
from opcodes.text_objects     import BT, ET
from opcodes.text_state       import Tc, Tw, Tz, TL, Tf, Tr, Ts
from opcodes.text_positioning import Td, TD, Tm, Tstar
from opcodes.text_showing     import Tj, TJ, Apostrophe, Quote

from pdf_extractor            import TextParser

#PTVS nonsense
from builtins import *

def get_subclasses(cls):
    subs = cls.__subclasses__()
    for s in subs:
        subs += get_subclasses(s)
    return subs

class PdfOper(object):
    """Abstract PDF opcode class.  Specify new opcodes by inheriting from 
    PdfOper and setting opcode to the appropriate pdf opcode."""
    opcode  = None
    is_text = False

    #Type hints
    if False:
        opcodes = OpcodeExecutor()
        parser  = TextParser()

    @classmethod
    def __init__(cls, executor):
        cls.opcodes = executor
        cls.parser  = executor.parser

        assert isinstance(cls.opcodes, OpcodeExecutor)
        assert isinstance(cls.parser,  TextParser)

    @classmethod
    def __call__(cls, args):
        return cls.do_opcode(cls.parser, *args)
    @classmethod
    def do_opcode(cls, *args):
        raise NotImplementedError

class PdfNOP(PdfOper):
    """Dummy opcode that does nothing.  Called when we've not 
    implemented a given opcode"""
    @classmethod
    def do_opcode(cls, *args):
        #Some logging stuff should go here
        pass

class OpcodeExecutor(object):
    """Singleton that maintains the collection of all known opcodes and 
    dispatches them.  Once initiated, opcodes can be called by invoking
    OpcodeExecutor[opcode](*args)"""

    @classmethod
    def __init__(cls, parser):
        cls.parser  = parser
        cls.NOP     = PdfNOP(cls) 
        cls.opcodes = cls._build_opcodes()

    @classmethod
    def __getitem__(cls, opcode):
        """Main dispatch method.  Return the opcode if implemented, otherwise
        returns a NOP."""
        try:
            return cls.opcodes[opcode]
        except KeyError:
            #We should probably add some logging stuff here
            return cls.NOP
    
    @classmethod
    def _build_opcodes(cls):
        """Build the opcodes dict, initializing its elements as we go"""
        opcodes = {o.opcode: o(cls)
                    for o in get_subclasses(PdfOper) 
                         if o.opcode}
        #This way we won't need to worry about bytes vs strs for opcodes
        for k,v in opcodes.items():
            if   isinstance(k, bytes):
                opcodes[k.decode()] = v
            elif isinstance(k, str):
                opcodes[k.encode()] = v