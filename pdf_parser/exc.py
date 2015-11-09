class PdfError(Exception):
    pass
class PdfParseError(PdfError):
    pass
class PdfOpWarning(RuntimeWarning):
    pass