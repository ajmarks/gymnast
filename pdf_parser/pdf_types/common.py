"""
Base PDFType class from which all of the other data types inherit
"""

class PdfType(object):
    """Abstract base class for PDF objects"""
    def pdf_encode(self):
        """Translate the object into bytes in PDF format"""
        raise NotImplementedError
    @property
    def value(self):
        """Objects, references, and such will override this in clever
        ways."""
        return self
    @property
    def parsed_object(self):
        """Objects, references, and such will override this in clever
        ways."""
        return self
