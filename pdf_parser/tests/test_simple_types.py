from .parser_test import ParserTestCase
from ..exc        import *

class TestSimpleTypes(ParserTestCase):
    def setUp(self):
        super().__init__()
        self.func = self.parser._parse_literal

    def test_int(self):
        self.assertEqual(self.func(b'-10'), -10)
        self.assertEqual(self.func(b'10'), 10)
    
    def test_real(self):
        self.assertAlmostEqual(self.func(b'-10.123'), -10.123)
        self.assertAlmostEqual(self.func(b'10.123'), 10.123)
    def test_bool(self):
        self.assertIs(self.func(b'true'),  True)
        self.assertIs(self.func(b'false'), False)
    def test_real(self):
        self.assertIsNone(self.func(b'null'))
    def test_invalid(self):
        bad_vals = [b'slfkj', b'none', b'True', b'False', b'12..54', 
                    b'-123.55', b'123,456', b'(string)', b'<</Name1 1>>',
                    b'[1 2 3]',b'%comment', b'\x250\x249']
        for val in bad_vals:
            self.assertRaises(PdfParseError, self.func, val)