from pdf_parser.pdf_parser import PdfParser

fname = 'S:/Research/Leisure/STR RevPar Data/US Weekly PDFs/Lodging Smith Travel Results 15-10-07.pdf'
parser = PdfParser()
pdf = parser.parse(fname)
pass