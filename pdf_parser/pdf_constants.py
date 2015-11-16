"""
Constants needed mostly for PDF character encoding
"""

import binascii
import os
from bidict import bidict

#PTVS nonsense
if False:
    from builtins import *

__all__  = ['EOLS', 'WHITESPACE', 'BASE_ENCODINGS', 'GLYPH_LIST']
DATA_DIR = os.path.dirname(os.path.abspath(__file__))+'/data/'

EOLS       = frozenset((b'\r', b'\n', b'\r\n'))
WHITESPACE = frozenset((b' ', b'\t', b'\r', b'\n', b'\f', b'\x00'))

def get_base_encodings():
    """Load the base PDF encoding schemes and parse it into a nice dict."""
    with open(DATA_DIR+'/pdf_encodings.txt') as f:
        lines = [l.split(';') for l in f.read().splitlines() if l[0] != '#']
    encodings = ('StandardEncoding', 'MacRomanEncoding', 
                 'WinAnsiEncoding', 'PDFDocEncoding')
    to_code = lambda x: int(x, 8) if x else None
    return {l[0]:dict(zip(encodings,map(to_code, l[1:]))) for l in lines}

BASE_ENCODINGS = get_base_encodings()

def get_glyph_list():
    """Load the Adobe Glyph list into a bidict.
    https://partners.adobe.com/public/developer/en/opentype/glyphlist.txt"""

    #For the character codes that appear multiple times, we're going to
    #arbitrarily exclude one of the names.
    #TODO: handle this less dumbly
    dupes = {'Cdotaccent', 'Dcroat', 'Edotaccent', 'Gcommaaccent', 
             'Gdotaccent', 'cdotaccent', 'dcroat', 'edotaccent', 
             'gcommaaccent', 'middot', 'mu1', 'nbspace', 'overscore', 
             'sfthyphen', 'spacehackarabic', 'verticalbar'}
    with open(DATA_DIR+'glyphlist.txt') as f:
        lines = [l.split(';') for l in f.read().splitlines() if l[0] != '#']
    decode = lambda s: b''.join([binascii.unhexlify(i) 
                                 for i in s.split()]).decode('utf-16-be')
    return bidict({l[0]:decode(l[1]) for l in lines if l[0] not in dupes})

GLYPH_LIST = get_glyph_list()
