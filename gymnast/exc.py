"""
Exceptions used by this package
"""

__all__ = ['PdfError', 'PdfParseError', 'PdfOpWarning', 'NotImplementedWarning']

class PdfError(Exception):
    """Generic PDF exception"""
    pass
class PdfParseError(PdfError):
    """Exception parsing PDF file"""
    pass
class PdfWarning(UserWarning):
    """Invalid or non-implemented PDF content operation"""
    pass
class PdfOpWarning(PdfWarning):
    """Invalid or non-implemented PDF content operation"""
    pass
class NotImplementedWarning(PdfWarning):
    """Invalid or non-implemented PDF content operation"""
    pass
