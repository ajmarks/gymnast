import sys
sys.path.insert(1, './')
#sys.path.insert(1, './pdf_parser/')

from pdf_parser import PdfDocument, PdfParser
from pdf_parser.renderer import PdfSimpleRenderer, PdfTextRenderer
from pdf_parser.pdf_parser import PdfParser
from pdf_parser.misc       import buffer_data

#fname = 'c:/855.pdf'
fname = 'S:/Research/Leisure/STR RevPar Data/US Weekly PDFs/Lodging Smith Travel Results 15-10-07.pdf'
pdf = PdfDocument(fname).parse()
page = pdf.Pages[4]
print(page.Fonts['T1_1'].FontDescriptor.CharSet)
print(PdfSimpleRenderer(page).render())
#fname = 'c:/results.pdf'
##fname = 'S:/Research/Leisure/STR RevPar Data/US Weekly PDFs/Lodging Smith Travel Results 15-10-07.pdf'
#pdf = PdfDocument(fname)
#pdf.parse()
#rend = PdfTextRenderer(pdf.Pages[1]).render()

#import zlib
#s = page.Fonts['T1_0'].ToUnicode
#PdfParser().parse(page.Fonts['T1_0'].ToUnicode.data, False, True)