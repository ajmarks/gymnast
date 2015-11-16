import io
import unittest
from ..pdf_parser.pdf_parser import PdfParser

class ParserTestCase(unittest.TestCase):
    """Test the parser"""
    def setUp(self):
        self.parser = PdfParser()
