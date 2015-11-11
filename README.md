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


##TODO (in no particular order)
- **Features and functionality**
  - [ ] Complete the base page renderer
  - [ ] Write a fancypants, rtree-based text extracting renderer based on text-object coordinates
  - [ ] Handle page numbering more fully
    - [ ] Add a method to PdfDocument to get a page by number
    - [ ] Add propreties to PdfPage for the page number (both as an int and a formatted str according to PdfDocument.Root.PageLabels['Nums'])
  - [ ] Implement the remaining StreamFilters (will probably have the image ones return a PIL.Image)
    - [ ] `RunLengthDecode`
    - [ ] `CCITTFaxDecode`
    - [ ] `JBIG2Decode`
    - [ ] `DCTDecode`
    - [ ] `JPXDecode`
    - [ ] `Crypt`
  - [ ] Implement remaining object types
    - [ ] `ObjStm`
    - [ ] `XRef`
    - [ ] `Filespec`
    - [ ] `EmbeddedFile`
    - [ ] `CollectionItem` / `CollectionSubitem`
    - [ ] `XObject`
  - [ ] Font stuff
    - [ ] Add legacy support for the 14 standard fonts
    - [ ] Add support for Type3 fonts
    - [ ] Add support for TrueType fonts
    - [ ] Add support for composite fonts
    - [ ] Font-to-unicode CMAPs
  - [ ] Handle document encryption
  - [ ] Start on graphics stuff (maybe)
  - [ ] Interactive forms (AcroForms)
- **Administrative**
  - [ ] Write tests for existing code
  - [ ] Come up with a better name
  - [ ] Document everything much, much better internally
  - [ ] Package it up neatly and pypi it
  - [ ] Write some proper documentation