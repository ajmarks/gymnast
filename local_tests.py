import sys
sys.path.insert(1, './')
#sys.path.insert(1, './pdf_parser/')

from pdf_parser.pdf_doc  import PdfDocument
from pdf_parser.pdf_page import PdfPage

#fname = 'c:/L549-0113-6.pdf'
fname = 'S:/Research/Leisure/STR RevPar Data/US Weekly PDFs/Lodging Smith Travel Results 15-10-07.pdf'
pdf = PdfDocument(fname)
pdf.parse()
page = PdfPage(pdf._elements[0]['Root'].value['Pages'].value['Kids'][1])
ops = page.Contents.operations
l = [next(ops) for i in  range(100)]