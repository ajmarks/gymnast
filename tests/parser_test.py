import io
import unittest
from ..ppdf_parser import PdfParser

class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = PdfParser()

    def set_data(self, data):
        self.parser._data = io.BufferedReader(io.BytesIO(data))