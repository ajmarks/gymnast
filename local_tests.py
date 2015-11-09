import sys
sys.path.insert(1, './')
#sys.path.insert(1, './pdf_parser/')

from pdf_parser.pdf_parser import PdfParser

fname = 'c:/L549-0113-6.pdf'
parser = PdfParser()
pdf = parser.parse(fname)

print(pdf)