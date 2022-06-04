# acl-crawler

This script extracts each paper info listed in the specified URL of ACL Anthology sites.  The info includes 
paper title, authors, abstract, PDF url, Bib url, Software zip url, and code site url.

## Usage

- `./ac.py URL` extracts info from the URL and output a CSV table to standard output.
- `./ac.py -s FILE URL` extracts info as above, and also writes the HTML into the FILE.
- `./ac.py -f PATH` reads a HTML file and extracts info from it.
