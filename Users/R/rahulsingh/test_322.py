import scraperwiki

# Blank Python
import urllib2
import re

scraperwiki.sqlite.attach('laptops-ib-pages-results','urls')
list_urls = scraperwiki.sqlite.select('* from urls.swdata')

count = 1
for dict_urls in list_urls:
 url = dict_urls['url']
 #print url
 
 open = urllib2.urlopen(url)
 page = str(open.readlines())
 

 matches = re.findall(r'(href=")(/Laptop/[./?=\w\d-]+)',page)
 for match in matches:
  pagelink = 'http://www.infibeam.com'+match[1]
  print pagelink
  scraperwiki.sqlite.save(['link'],data={'link':pagelink})
  print count
  count = count + 1

print 'total count : '+str(count)
import scraperwiki

# Blank Python
import urllib2
import re

scraperwiki.sqlite.attach('laptops-ib-pages-results','urls')
list_urls = scraperwiki.sqlite.select('* from urls.swdata')

count = 1
for dict_urls in list_urls:
 url = dict_urls['url']
 #print url
 
 open = urllib2.urlopen(url)
 page = str(open.readlines())
 

 matches = re.findall(r'(href=")(/Laptop/[./?=\w\d-]+)',page)
 for match in matches:
  pagelink = 'http://www.infibeam.com'+match[1]
  print pagelink
  scraperwiki.sqlite.save(['link'],data={'link':pagelink})
  print count
  count = count + 1

print 'total count : '+str(count)
