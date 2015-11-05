# pdf_parser TODO

* **PDF basic Parser**
    * Decide if indirect they should be decoded in-place or left as a PdfIndirectObject type
	* Implement streams
    * Implement xrefs
	* Implement trailers
	* PDF Headers
	* %%EOF
    * Package it up into a nice class


* **Text Parser**
	* Refactor existing code to longer assume PyPDF2 conventions.  This also means nuking all of those ridiculous extra leading /'s in Name objects
	* Finish TextBlock class
	* Impliment simple RTree based line identification heuristic

* **Long-term projects**
	* Encryption and protection
	* Images and such
	* Other graphic objects?