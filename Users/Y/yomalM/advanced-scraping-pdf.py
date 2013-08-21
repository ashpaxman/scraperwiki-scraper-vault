###########################################################################################
# We use a ScraperWiki library called pdftoxml to scrape PDFs.
# This is an example of scraping a simple PDF.
###########################################################################################
import scraperwiki
import json
from BeautifulSoup import BeautifulSoup

pdfurl = "http://www.madingley.org/uploaded/Hansard_08.07.2010.pdf"
a = scraperwiki.scrape(pdfurl)
s = BeautifulSoup(scraperwiki.pdftoxml(a))

name = None
all = []
data = {}
state = None
l = []

for t in s.findAll('text'):
    if t.text != " ": 
        print t
        print t.text
    
