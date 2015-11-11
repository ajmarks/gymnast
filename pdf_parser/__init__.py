# -*- coding: utf-8 -*-
"""PDF Parser

Classes:
    PdfDocument - General PDF document class.

.. :copyright: (c) 2015 Andrew Marks.
.. :license: MIT. See LICENSE for details.
"""

__author__    = 'Andrew Marks'
__copyright__ = 'Copyright 2015, Andrew Marks'
__license__   = 'MIT'
__status__    = 'Alpha'

from .pdf_doc import PdfDocument

try:
    from pkg_resources import resource_string
    __version__ = resource_string(__name__, 'VERSION').decode('ascii').strip()
except Exception as e:
    from warnings import warn
    warn('Failed to read/set version: %r' % e)

__all__ = ['PdfDocument']