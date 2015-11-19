import sys
sys.path.insert(1, './')

from gymnast            import PdfDocument
from gymnast            import PdfLineRenderer
from gymnast.pdf_parser import PdfParser

#fname = 'c:/855.pdf'
fname = 'S:/Research/Leisure/STR RevPar Data/US Weekly PDFs/Lodging Smith Travel Results 15-10-07.pdf'
pdf = PdfDocument(fname).parse()
page = pdf.Pages[4]
print(page.Fonts['T1_1'].FontDescriptor.CharSet)
text = PdfLineRenderer(page, True, None).render()
print(text)
#fname = 'c:/results.pdf'
#pdf = PdfDocument(fname)
#pdf.parse()
#rend = PdfTextRenderer(pdf.Pages[1]).render()

#import zlib
#s = page.Fonts['T1_0'].ToUnicode
#PdfParser().parse(page.Fonts['T1_0'].ToUnicode.data, False, True)