import sys
sys.path.insert(1, './')

import requests
from gymnast import PdfDocument, PdfTextRenderer

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