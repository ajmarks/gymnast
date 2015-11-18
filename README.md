# Gymnast: It's not an Acrobat

[![GitHub license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/ajmarks/pdf_parser/blob/master/LICENSE) [![Code Issues](https://www.quantifiedcode.com/api/v1/project/d0106c63f4f8467586aae7498f148e94/badge.svg)](https://www.quantifiedcode.com/app/project/d0106c63f4f8467586aae7498f148e94)

PDF parser written in Python 3 (backport to 2.7 in the works).  This was designed to provide a Pythonic interface to access (and, eventually, write) Adobe PDF files.  Some of attributes have non-Pythonic capitalization, but that is to match the underlying structure of the PDF document (doing otherwise would get very confusing).

##Usage
```python
import io
from gymnast          import PdfDocument
from gymnast.renderer import PdfBaseRenderer

class PdfSimpleRenderer(PdfBaseRenderer):
    """Simple renderer example that just extracts text with no processing"""
    def __init__(self, page):
        super().__init__(page)
        self._text = io.StringIO()
    def _render_text(self, text, new_state):
        self._text.write(self.active_font.decode_string(text))
    def _return(self):
        return self._text.getvalue()

fname = '/path/to/file.pdf'
pdf   = PdfDocument(fname).parse()
text  = SimpleRenderer(pdf.Pages[-3]).render()
```


##TODO (in no particular order)
- **Features and functionality**
  - [x] Rewrite the parser and document class to lazy-load the document based on the xrefs table
  - [x] Complete the base page renderer
  - [ ] Page Rendering
    - [x] Getting the `BaseRenderer` class working
    - [x] Implement a proof of concept extractor that just dumps strings
    - [ ] Get a bit fancier, assigning textblocks to lines and such
  - [ ] Handle page numbering more fully
    - [ ] Add a method to `PdfDocument` to get a page by number
    - [ ] Add propreties to `PdfPage` for the page number (both as an `int` and a formatted `str` according to `PdfDocument.Root.PageLabels['Nums']`)
  - [ ] Backport to Python 2.7 (about 80% done or so)
  - [ ] Font stuff
    - [x] Carve the `PdfFont` class into an abstract `PdfBaseFont` and a `PdfType1Font` implementation
      - [x] `PdfFont.__new__` will pick the correct subclass based on the font's Subtype element
      - [x] PdfBasefFont class will also have an abstract method for the glyph space to text space transformation
    - [ ] Add subcless for Type3 fonts
    - [x] Add subcless for TrueType fonts
    - [ ] Add subcless for composite fonts
    - [x] Add legacy support for the 14 standard fonts
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
    - [x] `XRef`
    - [ ] `Filespec`
    - [ ] `EmbeddedFile`
    - [ ] `CollectionItem` / `CollectionSubitem`
    - [ ] `XObject`
  - [ ] Handle document encryption
  - [ ] Start on graphics stuff (maybe)
  - [ ] Interactive forms (AcroForms)
- **Administrative**
  - [ ] Write tests for existing code
  - [x] Come up with a better name
  - [ ] Document everything much, much better internally
  - [ ] Package it up neatly and pypi it
  - [ ] Write some proper documentation
