"""
PdfFont class: Switchboard for the actual font classes
"""

from warnings      import warn
from .type1        import Type1Font
from .base_font    import PdfBaseFont
from ..pdf_element import PdfElement
from ...exc        import NotImplementedWarning

class PdfFont(PdfElement):
    """Switchboard class that should probably be a function.
    Returns PDF Font of the appropriate types."""
    def __new__(self, obj, obj_key=None):
        obj = obj.value
        if obj['Type'] != 'Font':
            raise ValueError('Not a font')
        if obj['Subtype'] == 'Type1':
            return Type1Font(obj, obj_key)
        warn('Font subtype "{}" not yet supported'.format(obj['Subtype']),
             NotImplementedWarning)
        return PdfBaseFont(obj, obj_key)
