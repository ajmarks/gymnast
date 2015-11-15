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
  - [x] Rewrite the parser and document class to lazy-load the document based on the xrefs table
  - [ ] Add support for linearized PDF files
  - [x] Complete the base page renderer
  - [ ] Page Rendering
    - [x] Getting the `BaseRenderer` class working
    - [x] Implement a proof of concept extractor that just dumps strings
    - [ ] Get a bit fancier, assigning textblocks to lines and such
  - [ ] Handle page numbering more fully
    - [ ] Add a method to `PdfDocument` to get a page by number
    - [ ] Add propreties to `PdfPage` for the page number (both as an `int` and a formatted `str` according to `PdfDocument.Root.PageLabels['Nums']`)
  - [ ] Backport to Python 2.7 (should be pretty simple; I think it's just turning `yield from` into loops)
  - [ ] Font stuff
    - [ ] Carve the `PdfFont` class into an abstract `PdfBaseFont` and a `PdfType1Font` implementation
      - [ ] `PdfFont.__new__` will pick the correct subclass based on the font's Subtype element
      - [ ] PdfBasefFont class will also have an abstract method for the glyph space to text space transformation
    - [ ] Add subcless for Type3 fonts
    - [ ] Add subcless for TrueType fonts
    - [ ] Add subcless for composite fonts
    - [ ] Add legacy support for the 14 standard fonts
    - [ ] Font-to-unicode CMAPs
  - [ ] Implement the remaining `StreamFilter`s (will probably have the image ones return a `PIL.Image`)
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
  - [ ] Handle document encryption
  - [ ] Start on graphics stuff (maybe)
  - [ ] Interactive forms (AcroForms)
- **Administrative**
  - [ ] Write tests for existing code
  - [ ] Come up with a better name
  - [ ] Document everything much, much better internally
  - [ ] Package it up neatly and pypi it
  - [ ] Write some proper documentation
