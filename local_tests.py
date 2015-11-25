import sys
sys.path.insert(1, './')

import requests
from gymnast import PdfDocument, PdfTextRenderer
from gymnast.pdf_elements.fonts.cmap import CMap

fname = 'S:/Research/Leisure/STR RevPar Data/US Weekly PDFs/Lodging Smith Travel Results 15-10-07.pdf'
pdf = PdfDocument(fname).parse()
page = pdf.Pages[4]
strm = page.Fonts['T1_1'].ToUnicode
cmap = CMap.from_stream(strm)



#fname = 'c:/855.pdf'
url = 'http://www.census.gov/retail/mrts/www/data/pdf/ec_current.pdf'
r = requests.get(url)
pdf = PdfDocument(r.content).parse()
print(PdfTextRenderer(pdf.Pages[1], fixed_width=True).render())
input()
#fname = 'c:/results.pdf'
#pdf = PdfDocument(fname)
#pdf.parse()
#rend = PdfTextRenderer(pdf.Pages[1]).render()

#import zlib
#s = page.Fonts['T1_0'].ToUnicode
#PdfParser().parse(page.Fonts['T1_0'].ToUnicode.data, False, True)