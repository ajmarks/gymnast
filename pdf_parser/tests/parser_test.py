import io
import unittest
from ..pdf_parser import PdfParser

class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = PdfParser()

    def set_data(self, data):
        self.parser._data = io.BufferedReader(io.BytesIO(data))