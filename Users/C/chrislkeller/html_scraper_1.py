import scraperwiki           
import requests
from BeautifulSoup import BeautifulSoup
import urllib
import urllib2

#set page user agent
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19'
headers={'User-Agent':user_agent,}

#varible for page content
html = urllib2.urlopen('http://www.publichealthmdc.com/environmental/water/beaches/').read()

#create soup object
soup = BeautifulSoup(html)

#find each beach
beach = {'class': 'outline_box_beaches'}
divs = soup.findAll(attrs = beach)

#loop through beaches, grabbing name and status
for el in divs:
    name = el.h2.text.strip()
    status = el.div.div.span.text.strip()
    print "%s - (%s)" % (name, status)