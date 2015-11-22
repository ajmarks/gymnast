import sys
sys.path.insert(1, './')

import requests

from gymnast            import PdfDocument
from gymnast            import PdfTextRenderer
from gymnast.pdf_parser import PdfParser

#fname = 'c:/855.pdf'
url = 'http://www.census.gov/retail/mrts/www/data/pdf/ec_current.pdf'
r = requests.get(url)
pdf = PdfDocument(r.content).parse()
page = pdf.Pages[1]
#ops = [str(o) for o in page.Contents.operations]
text = PdfTextRenderer(page, True, None).render()
print(text)
input()
#fname = 'c:/results.pdf'
#pdf = PdfDocument(fname)
#pdf.parse()
#rend = PdfTextRenderer(pdf.Pages[1]).render()

#import zlib
#s = page.Fonts['T1_0'].ToUnicode
#PdfParser().parse(page.Fonts['T1_0'].ToUnicode.data, False, True)