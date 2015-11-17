"""
PDF Document elements.  These make up the actual useful parts of the PDF file.
Internally, most are simply dict-like objects, however, we have two modes of
access: dict-like and attribute.

Dict-like access allows one to get to the actual data defined in the object.
Attribute access provides a variety of helpful featues such as deferencing
indirect object references, parsing the data into a useful object, and filling
in default values where applicable.
"""

from .pdf_element    import PdfElement
from .fonts          import PdfBaseFont, FontDescriptor, FontEncoding, PdfFont
from .pdf_page       import PdfPage, PdfPageNode, PdfAbstractPage
from .other_elements import PdfCatalog

__all__ = ['PdfElement', 'PdfFont', 'FontDescriptor', 'FontEncoding',
           'PdfPage', 'PdfPageNode', 'PdfAbstractPage', 'PdfCatalog'
           'PdfBaseFont']
