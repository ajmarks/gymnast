import sys
sys.path.insert(1, './')

import requests

from gymnast            import PdfDocument
from gymnast            import PdfLineRenderer
from gymnast.pdf_parser import PdfParser

#fname = 'c:/855.pdf'
url = 'http://www.census.gov/retail/mrts/www/data/pdf/ec_current.pdf'
r = requests.get(url)
pdf = PdfDocument(r.content).parse()
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