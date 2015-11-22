"""
The various object types represented in PDF files
"""

#These may seem unecessary, but it lets us assume that every pdf element
#has a .value property so we needn't worry about constantly trying to
#deference.  It will also help when we implement a PDF writer, allowing us
#to simply call obj.pdf_encode()

from .compound_types   import PdfArray, PdfDict
from .object_types     import PdfObjectReference, PdfIndirectObject
from .simple_types     import PdfNull, PdfInt, PdfReal, PdfBool
from .string_types     import PdfString, PdfLiteralString, PdfHexString, PdfName, PdfComment
from .streams          import PdfStream
from .structural_types import PdfRaw, PdfHeader, PdfRawData, PdfXref, PdfStreamXref
from .common           import PdfType

__all__ = ['PdfArray', 'PdfDict', 'PdfObjectReference', 'PdfIndirectObject',
           'PdfNull', 'PdfInt', 'PdfReal', 'PdfBool', 'PdfString',
           'PdfLiteralString', 'PdfHexString', 'PdfName', 'PdfComment',
           'PdfStream', 'PdfRaw', 'PdfHeader', 'PdfRawData', 'PdfXref',
           'PdfType', 'PdfStreamXref']
