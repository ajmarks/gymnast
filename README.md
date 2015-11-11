# pdf_parser

PDF parser written in Python 3.

##Usage
```python
from pdf_parser import PdfDocument

file = '/path/to/file.pdf'
pdf = PdfDocument(file).parse()
page = pdf.Pages[-3]
fonts = page.Fonts.values()
```
