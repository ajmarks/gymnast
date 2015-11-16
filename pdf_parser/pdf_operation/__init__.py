"""
PDF Content Stream operations.  These represent the bulk of the displayed
content in the document.  They are callables that act on a PdfRenderer object
"""

from .pdf_operation import PdfOperation, PdfNOP

__all__ = ['PdfOperation', 'PdfNOP']
