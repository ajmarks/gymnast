# Gymnast: It's not Acrobat

[![GitHub license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/ajmarks/pdf_parser/blob/master/LICENSE) [![Code Issues](https://www.quantifiedcode.com/api/v1/project/d0106c63f4f8467586aae7498f148e94/badge.svg)](https://www.quantifiedcode.com/app/project/d0106c63f4f8467586aae7498f148e94) [![PyPI version](https://badge.fury.io/py/gymnast.svg)](https://badge.fury.io/py/gymnast)

PDF parser written in Python 3 (backport to 2.7 in the works).  This was designed to provide a Pythonic interface to access (and, eventually, write) Adobe PDF files.  Some of attributes have non-Pythonic capitalization, but that is to match the underlying structure of the PDF document (doing otherwise would get very confusing).

##Usage (dev branch)
```python
import requests
from gymnast import PdfDocument, PdfTextRenderer

url = 'http://www.census.gov/retail/mrts/www/data/pdf/ec_current.pdf'
r = requests.get(url)
pdf = PdfDocument(r.content).parse()
text = PdfTextRenderer(pdf.Pages[1], fixed_width=True).render()
print(text)
```

####Output:
```
     Table 1.    Estimated Quarterly U.S. Retail Sales: Total and E-commerce1 
      (Estimates are based on data from the Monthly Retail Trade Survey and administrative records.) 
                                    Retail Sales        E-commerce          Percent Change              Percent Change
                                (millions of dollars)    as a Percent      From Prior Quarter            From Same Quarter 
             Quarter                                            of                                         A Year Ago
                               Total      E-commerce          Total       Total      E-commerce       Total     E-commerce 
       Adjusted2
       3rd quarter 2015(p)     1,184,994      87,509         7.4           1.2           4.2           1.6          15.1
       2nd quarter 2015(r)     1,171,458      84,019         7.2           1.6           4.4           1.0          14.3
       1st quarter 2015       1,152,986      80,451         7.0          -1.4          3.7           1.8          14.8
       4th quarter 2014       1,169,143      77,558         6.6           0.3           2.0           3.8          14.0
       3rd quarter 2014(r)     1,165,943      76,041         6.5           0.5           3.5           4.0          15.4
       Not Adjusted
       3rd quarter 2015(p)     1,187,337      81,053         6.8           0.0           2.9           1.6          15.2
       2nd quarter 2015(r)     1,187,208      78,779         6.6          10.2          5.2           0.9          14.4
       1st quarter 2015       1,077,586      74,920         7.0          -12.1         -19.9          1.5          14.4
       4th quarter 2014       1,225,969      93,530         7.6           4.9          32.9          3.9          13.9
       3rd quarter 2014       1,168,187      70,351         6.0          -0.7          2.2           4.2          15.7
         (p) Preliminary estimate.    (r) Revised estimate.  
             1 E-commerce sales are sales of goods and services where  the buyer places an order, or the price and terms  of the sale  are negotiated over an Internet, mobile 
         device (M-commerce), extranet, Electronic Data Interchange (EDI) network, electronic mail, or other comparable online system. Payment may or may not be 
         made online. 
          2
          Estimates are adjusted for seasonal variation, but not for price changes.  Total sales estimates are also adjusted for trading-day differences and moving 
         holidays. 
...
```


##TODO (in no particular order)
- **Features and functionality**
  - [x] Rewrite the parser and document class to lazy-load the document based on the xrefs table
  - [x] Complete the base page renderer
  - [ ] Page Rendering
    - [x] Getting the `BaseRenderer` class working
    - [x] Implement a proof of concept extractor that just dumps strings
    - [x] Get a bit fancier, assigning textblocks to lines and such
  - [ ] Handle page numbering more fully
    - [x] Add a method to `PdfDocument` to get a page by number
    - [ ] Add propreties to `PdfPage` for the page number (both as an `int` and a formatted `str` according to `PdfDocument.Root.PageLabels['Nums']`) (first part done on dev branch)
  - [ ] Backport to Python 2.7 (about 80% done or so)
  - [ ] Font stuff
    - [x] Carve the `PdfFont` class into an abstract `PdfBaseFont` and a `PdfType1Font` implementation
      - [x] `PdfFont.__new__` will pick the correct subclass based on the font's Subtype element
      - [x] `PdfBasefFont` class will also have an abstract method for the glyph space to text space transformation
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
    - [x] `ObjStm` (on dev branch)
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
  - [x] Package it up neatly and pypi it
  - [ ] Write some proper documentation
