# pdf_parser TODO

* **PDF basic Parser**
    * Implement indirect objects
    * Implement streams
    * Decide if we're going to keep the PdfNull, PdfBoolean, PdfInt, and PdfReal types
    * Package it up into a nice class
    * See if we can make that main parser function not be so insanely awful

* **Text Parser**
	* Refactor existing code to longer assume PyPDF2 conventions.  This also means nuking all of those ridiculous extra leading /'s in Name objects
	* Finish TextBlock class
	* Impliment simple RTree based line identification heuristic

* **Long-term projects**
	* Encryption and protection
	* Images and such
	* Other graphic objects?