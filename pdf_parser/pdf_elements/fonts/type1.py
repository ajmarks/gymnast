"""
Type1 Fonts
"""
import os

from .base_font       import PdfBaseFont
from ...pdf_constants import DATA_DIR
from ...pdf_types     import PdfName, PdfDict

AFM_DIR   = DATA_DIR + '/afm/'
STD_FONTS = {j[:-4] for j in os.listdir(AFM_DIR) if j[-4:] == '.afm'}

class Type1Font(PdfBaseFont):
    """Base PDF Font.  Right now this is exclusively Type 1."""

    def __init__(self, obj, obj_key=None):
        """If the font has a name in the Standard 14, load defaults from there
        and then apply the settings from the definition here."""
        obj = obj.value
        if obj['BaseFont'] in STD_FONTS:
            std_font = get_std_font_dict(obj['BaseFont'])
            obj = std_font.update(obj)
        super(Type1Font, self).__init__(obj, obj_key)

    def text_space_coords(self, x, y):
        """Type1 fonts just scale by 1/1000 to convert from glyph space"""
        return x/1000., y/1000.

    @classmethod
    def load_standard_font(cls, font_name):
        """Super, super crude method to parse a afm font file into a Type1
        PdfFont object"""

def get_std_font_dict(font_name):
    """Load a standard font and parse it into a PdfDict similar to how it would
    be stored in a PDF file"""
    FILE_PAT = AFM_DIR + '/{}.afm'

    typify = lambda a: None if not a else (a[0] if len(a) == 1 else a)
    parsed = load_afm_file(FILE_PAT.format(font_name))
    charmets = [{i.split()[0]:typify(i.split()[1:])
                 for i in l.split(';') if i.strip()}
                for l in parsed['CharMetrics']]
    first_char = min(int(i['C']) for i in charmets if i['C'] != '-1')
    last_char  = min(int(i['C']) for i in charmets)
    widths     = [i['WX']
                  for i in sorted(charmets, key=lambda x: int(x['C']))
                  if i['C'] != '-1']
    charset    = [PdfName(i['N'])  for i in charmets if i['C'] != '-1']
    intprop = lambda x: None if x not in parsed else int(parsed[x])

    flags =   1*int(parsed.get('IsFixedPitch') == 'true')\
            +   8*(parsed['CharacterSet'] == 'Special')    \
            +  64*(parsed['CharacterSet'] != 'Special')    \
            + 128*(parsed['ItalicAngle']  != '0')
    fdesc = {PdfName('Type')       : 'FontDescriptor',
             PdfName('FontName')   : parsed['FontName'],
             PdfName('FontFamily') : parsed['FamilyName'],
             PdfName('FontWeight') : parsed['Weight'],
             PdfName('Flags')      : flags,
             PdfName('FontBBox')   : [int(i) for i in parsed['FontBBox']],
             PdfName('ItalicAngle'): intprop('ItalicAngle'),
             PdfName('Ascent')     : intprop('Ascender'),
             PdfName('Descent')    : intprop('Descender'),
             PdfName('CapHeight')  : intprop('CapHeight'),
             PdfName('XHeight')    : intprop('XHeight'),
             PdfName('StemV')      : intprop('StdHW'),
             PdfName('StemH')      : intprop('StdVW'),
             PdfName('Charset')    : charset,
            }
    font  = {PdfName('Type')          : 'Font',
             PdfName('Subtype')       : 'Type1',
             PdfName('BaseFont')      : parsed['FontName'],
             PdfName('FirstChar')     : first_char,
             PdfName('LastChar')      : last_char,
             PdfName('Widths')        : widths,
             PdfName('FontDescriptor'): PdfDict(fdesc),
            }
    return PdfDict(font)

def load_afm_file(fname):
    """Load an Adobe Font Metrics file.  This is somewhat crude, but sufficient
    for these purposes"""
    DO_NOTHINGS =  {'EndFontMetrics', 'StartFontMetrics',
                    'EndKernData', 'StartKernData'}
    SECTIONS = {'StartCharMetrics', 'StartKernPairs', 'StartTrackKern'}
    with open(fname) as f:
        lines =  [l for l in f.read().splitlines() if l[:8]!='Comment '][::-1]
    data = {}
    delist = lambda x: x[0] if len(x) == 1 else x
    while lines:
        line = lines.pop().split()
        if   line[0] in DO_NOTHINGS:
            continue
        elif line[0] in SECTIONS:
            data[line[0][5:]] = lines[-int(line[1]):][::-1]
            del lines[-int(line[1])-1:]
        else:
            data[line[0]] = delist(line[1:])
    return data

