#These may seem unecessary, but it lets us assume that every pdf element
#has a .value property so we needn't worry about constantly trying to 
#deference.  It will also help when we implement a PDF writer, allowing us
#to simply call obj.pdf_encode()

from .compound_types   import *
from .object_types     import *
from .simple_types     import *
from .string_types     import *
from .streams          import *
from .structural_types import *