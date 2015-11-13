import sys
sys.path.insert(1, './')
#sys.path.insert(1, './pdf_parser/')

from pdf_parser import PdfDocument, PdfParser
from pdf_parser.renderer import PdfSimpleRenderer, PdfTextRenderer

#fname = 'c:/L549-0113-6.pdf'
fname = 'S:/Research/Leisure/STR RevPar Data/US Weekly PDFs/Lodging Smith Travel Results 15-10-07.pdf'
pdf = PdfDocument(fname)
pdf.parse()
rend = PdfTextRenderer(pdf.Pages[4]).render()

import zlib
s = page.Fonts['T1_0'].ToUnicode
PdfParser().parse(page.Fonts['T1_0'].ToUnicode.data, False, True)