from urllib import urlopen
from BeautifulSoup import BeautifulSoup 
import re

#open and read webpage
webpage = urlopen("http://feeds.huffingtonpost.com/huffingtonpost/raw_feed").read()

#determine what to titles / links to grab (2nd through 16th)
listiterator = []
listiterator[:] = range(2,16)

soup = BeautifulSoup(webpage)

titlesoup = soup.findAll("title")
linksoup = soup.findAll("link")

#print results
for i in listiterator:
    print titlesoup[i]
    print linksoup[i]
    print "\n"
from urllib import urlopen
from BeautifulSoup import BeautifulSoup 
import re

#open and read webpage
webpage = urlopen("http://feeds.huffingtonpost.com/huffingtonpost/raw_feed").read()

#determine what to titles / links to grab (2nd through 16th)
listiterator = []
listiterator[:] = range(2,16)

soup = BeautifulSoup(webpage)

titlesoup = soup.findAll("title")
linksoup = soup.findAll("link")

#print results
for i in listiterator:
    print titlesoup[i]
    print linksoup[i]
    print "\n"
