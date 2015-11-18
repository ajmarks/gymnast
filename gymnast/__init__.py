# -*- coding: utf-8 -*-
"""Gymnast: PDF Parser

Classes:
    PdfDocument - General PDF document class.

.. :copyright: (c) 2015 Andrew Marks.
.. :license: MIT. See LICENSE for details.
"""

__author__    = 'Andrew Marks'
__copyright__ = 'Copyright 2015, Andrew Marks'
__license__   = 'MIT'
__status__    = 'Alpha'

from .pdf_doc    import PdfDocument
from .pdf_parser import PdfParser

from pkg_resources import resource_string
__version__ = resource_string(__name__, 'VERSION').decode('ascii').strip()

__all__ = ['PdfDocument', 'PdfParser']
