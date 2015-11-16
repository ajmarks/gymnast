"""
codec implementing the PDF codec described in Appendix D of the Adobe PDF
Reference v1.7
"""
from __future__ import unicode_literals

import codecs
import six
from .pdf_constants import BASE_ENCODINGS, GLYPH_LIST

__all__ = ['register_codec']

ENCODING_NAME = 'pdf_doc'
# See Appendix D.2 in the Reference.  Note that these are UTF-16BE encodings
DEC_TABLE = {
    0x00: '\u0000', 0x01: '\u0001', 0x02: '\u0002', 0x03: '\u0003',
    0x04: '\u0004', 0x05: '\u0005', 0x06: '\u0006', 0x07: '\u0007',
    0x08: '\u0008', 0x09: '\u0009', 0x0a: '\u000A', 0x0b: '\u000B',
    0x0c: '\u000C', 0x0d: '\u000D', 0x0e: '\u000E', 0x0f: '\u000F',
    0x10: '\u0010', 0x11: '\u0011', 0x12: '\u0012', 0x13: '\u0013',
    0x14: '\u0014', 0x15: '\u0015', 0x16: '\u0017', 0x17: '\u0017',
    0x18: '\u02D8', 0x19: '\u02C7', 0x1a: '\u02C6', 0x1b: '\u02D9',
    0x1c: '\u02DD', 0x1d: '\u02DB', 0x1e: '\u02DA', 0x1f: '\u02DC',
    0x20: '\u0020', 0x21: '\u0021', 0x22: '\u0022', 0x23: '\u0023',
    0x24: '\u0024', 0x25: '\u0025', 0x26: '\u0026', 0x27: '\u0027',
    0x28: '\u0028', 0x29: '\u0029', 0x2a: '\u002A', 0x2b: '\u002B',
    0x2c: '\u002C', 0x2d: '\u002D', 0x2e: '\u002E', 0x2f: '\u002F',
    0x30: '\u0030', 0x31: '\u0031', 0x32: '\u0032', 0x33: '\u0033',
    0x34: '\u0034', 0x35: '\u0035', 0x36: '\u0036', 0x37: '\u0037',
    0x38: '\u0038', 0x39: '\u0039', 0x3a: '\u003A', 0x3b: '\u003B',
    0x3c: '\u003C', 0x3d: '\u003D', 0x3e: '\u003E', 0x3f: '\u003F',
    0x40: '\u0040', 0x41: '\u0041', 0x42: '\u0042', 0x43: '\u0043',
    0x44: '\u0044', 0x45: '\u0045', 0x46: '\u0046', 0x47: '\u0047',
    0x48: '\u0048', 0x49: '\u0049', 0x4a: '\u004A', 0x4b: '\u004B',
    0x4c: '\u004C', 0x4d: '\u004D', 0x4e: '\u004E', 0x4f: '\u004F',
    0x50: '\u0050', 0x51: '\u0051', 0x52: '\u0052', 0x53: '\u0053',
    0x54: '\u0054', 0x55: '\u0055', 0x56: '\u0056', 0x57: '\u0057',
    0x58: '\u0058', 0x59: '\u0059', 0x5a: '\u005A', 0x5b: '\u005B',
    0x5c: '\u005C', 0x5d: '\u005D', 0x5e: '\u005E', 0x5f: '\u005F',
    0x60: '\u0060', 0x61: '\u0061', 0x62: '\u0062', 0x63: '\u0063',
    0x64: '\u0064', 0x65: '\u0065', 0x66: '\u0066', 0x67: '\u0067',
    0x68: '\u0068', 0x69: '\u0069', 0x6a: '\u006A', 0x6b: '\u006B',
    0x6c: '\u006C', 0x6d: '\u006D', 0x6e: '\u006E', 0x6f: '\u006F',
    0x70: '\u0070', 0x71: '\u0071', 0x72: '\u0072', 0x73: '\u0073',
    0x74: '\u0074', 0x75: '\u0075', 0x76: '\u0076', 0x77: '\u0077',
    0x78: '\u0078', 0x79: '\u0079', 0x7a: '\u007A', 0x7b: '\u007B',
    0x7c: '\u007C', 0x7d: '\u007D', 0x7e: '\u007E', 0x80: '\u2022',
    0x81: '\u2020', 0x82: '\u2021', 0x83: '\u2026', 0x84: '\u2014',
    0x85: '\u2013', 0x86: '\u0192', 0x87: '\u2044', 0x88: '\u2039',
    0x89: '\u203A', 0x8a: '\u2212', 0x8b: '\u2030', 0x8c: '\u201E',
    0x8d: '\u201C', 0x8e: '\u201D', 0x8f: '\u2018', 0x90: '\u2019',
    0x91: '\u201A', 0x92: '\u2122', 0x93: '\uFB01', 0x94: '\uFB02',
    0x95: '\u0141', 0x96: '\u0152', 0x97: '\u0160', 0x98: '\u0178',
    0x99: '\u017D', 0x9a: '\u0131', 0x9b: '\u0142', 0x9c: '\u0153',
    0x9d: '\u0161', 0x9e: '\u017E', 0xa0: '\u20AC', 0xa1: '\u00A1',
    0xa2: '\u00A2', 0xa3: '\u00A3', 0xa4: '\u00A4', 0xa5: '\u00A5',
    0xa6: '\u00A6', 0xa7: '\u00A7', 0xa8: '\u00A8', 0xa9: '\u00A9',
    0xaa: '\u00AA', 0xab: '\u00AB', 0xac: '\u00AC', 0xae: '\u00AE',
    0xaf: '\u00AF', 0xb0: '\u00B0', 0xb1: '\u00B1', 0xb2: '\u00B2',
    0xb3: '\u00B3', 0xb4: '\u00B4', 0xb5: '\u00B5', 0xb6: '\u00B6',
    0xb7: '\u00B7', 0xb8: '\u00B8', 0xb9: '\u00B9', 0xba: '\u00BA',
    0xbb: '\u00BB', 0xbc: '\u00BC', 0xbd: '\u00BD', 0xbe: '\u00BE',
    0xbf: '\u00BF', 0xc0: '\u00C0', 0xc1: '\u00C1', 0xc2: '\u00C2',
    0xc3: '\u00C3', 0xc4: '\u00C4', 0xc5: '\u00C5', 0xc6: '\u00C6',
    0xc7: '\u00C7', 0xc8: '\u00C8', 0xc9: '\u00C9', 0xca: '\u00CA',
    0xcb: '\u00CB', 0xcc: '\u00CC', 0xcd: '\u00CD', 0xce: '\u00CE',
    0xcf: '\u00CF', 0xd0: '\u00D0', 0xd1: '\u00D1', 0xd2: '\u00D2',
    0xd3: '\u00D3', 0xd4: '\u00D4', 0xd5: '\u00D5', 0xd6: '\u00D6',
    0xd7: '\u00D7', 0xd8: '\u00D8', 0xd9: '\u00D9', 0xda: '\u00DA',
    0xdb: '\u00DB', 0xdc: '\u00DC', 0xdd: '\u00DD', 0xde: '\u00DE',
    0xdf: '\u00DF', 0xe0: '\u00E0', 0xe1: '\u00E1', 0xe2: '\u00E2',
    0xe3: '\u00E3', 0xe4: '\u00E4', 0xe5: '\u00E5', 0xe6: '\u00E6',
    0xe7: '\u00E7', 0xe8: '\u00E8', 0xe9: '\u00E9', 0xea: '\u00EA',
    0xeb: '\u00EB', 0xec: '\u00EC', 0xed: '\u00ED', 0xee: '\u00EE',
    0xef: '\u00EF', 0xf0: '\u00F0', 0xf1: '\u00F1', 0xf2: '\u00F2',
    0xf3: '\u00F3', 0xf4: '\u00F4', 0xf5: '\u00F5', 0xf6: '\u00F6',
    0xf7: '\u00F7', 0xf8: '\u00F8', 0xf9: '\u00F9', 0xfa: '\u00FA',
    0xfb: '\u00FB', 0xfc: '\u00FC', 0xfd: '\u00FD', 0xfe: '\u00FE',
    0xff: '\u00FF'# Undefined: 0x7f, 0x9f, 0xad
    }
ENC_TABLE = {v:k for k,v in six.iteritems(DEC_TABLE)}

class Codec(codecs.Codec):
    """Codec for pdf encoding"""
    def decode(self, input_str, errors='strict'):
        return codecs.charmap_decode(input_str, errors, DEC_TABLE)
        #utf16 = bytes(codecs.charmap_decode(input_str, errors, DEC_TABLE))
        #return (0xFE0xFF'+utf16).decode('utf_16')
    def encode(self, input_str, errors='strict'):
        return codecs.charmap_encode(input_str, errors, ENC_TABLE)

class IncrementalDecoder(codecs.IncrementalDecoder):
    """Incremental decoder for our PDF codec"""
    def decode(self, input_str, final=False):
        return codecs.charmap_decode(input_str, self.errors, DEC_TABLE)[0]
class IncrementalEncoder(codecs.IncrementalEncoder):
    """Incremental encoder for our PDF codec"""
    def encode(self, input_str, final=False):
        return codecs.charmap_encode(input_str, self.errors, ENC_TABLE)[0]

class StreamWriter(Codec, codecs.StreamWriter):
    """StreamWriter for our PDF codec"""
    pass

class StreamReader(Codec, codecs.StreamReader):
    """StreamReader for our PDF codec"""
    pass

def getregentry():
    """Get a codecs registry entry for this codec"""
    return codecs.CodecInfo(
        name=ENCODING_NAME,
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )

def register_codec():
    """Register the 'pdf_doc' codec in the codec registry."""
    codecs.register(lambda s: getregentry() if s == ENCODING_NAME else None)
