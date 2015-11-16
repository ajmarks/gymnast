from .parser_test import ParserTestCase

class TestStringTypes(ParserTestCase):
    def test_literal_string(self):
        func = self.parser._parse_literal_string
        self.set_data(b'simple string)')
        self.assertEqual(func(None)._parsed_bytes, b'simple string')
        self.set_data(b'simple (string))')
        self.assertEqual(func(None)._parsed_bytes, b'simple (string)')
        self.set_data(b'simple \\((string))')
        self.assertEqual(func(None)._parsed_bytes, b'simple ((string)')
        self.set_data(b'simple (string\\)))')
        self.assertEqual(func(None)._parsed_bytes, b'simple (string))')

    def test_hex_string(self):
        func = self.parser._parse_hex_string
        self.set_data(b'deadbeef>')
        self.assertEqual(func(None)._parsed_bytes, b'\xde\xad\xbe\xef')

    def test_name(self):
        self.set_data(b'Bob#20Smith')
        val = self.parser._parse_name
        self.assertTrue(isinstance(val, PdfName))
        self.assertTrue(isinstance(val, str))
        self.assertEqual(val, 'Bob Smith')
