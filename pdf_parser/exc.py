"""
Exceptions used by this package
"""

class PdfError(Exception):
    """Generic PDF exception"""
    pass
class PdfParseError(PdfError):
    """Exception parsing PDF file"""
    pass
class PdfOpWarning(RuntimeWarning):
    """Invalid or non-implemented PDF content operation"""
    pass
