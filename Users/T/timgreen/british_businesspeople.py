# British businesspeople from Wikipedia
import scraperwiki
import lxml.html
import urllib2

categories = ['http://en.wikipedia.org/wiki/Category:British_businesspeople',
              'http://en.wikipedia.org/wiki/Category:English_businesspeople',
              'http://en.wikipedia.org/wiki/Category:Scottish_businesspeople',
              'http://en.wikipedia.org/wiki/Category:Welsh_businesspeople',]

for category_url in categories:
    category_url_next = category_url
    while category_url_next is not None:
        response = urllib2.urlopen(category_url_next)
        tree = lxml.html.parse(response, base_url=category_url_next)
        
        for a in tree.xpath('//td/ul/li/a'):
            scraperwiki.sqlite.save(['url'], {'name': a.text, 'category_url': category_url, 'url': "http://en.wikipedia.org%s" % a.attrib['href']}, table_name='people')
    
        next_a = tree.xpath('//div[@id="mw-pages"]/a[.="next 200"]')
        if next_a:
            print "Continuing on %s" % category_url
            category_url_next = "http://en.wikipedia.org%s" % next_a[0].attrib['href']
        else:
            category_url_next = None
# British businesspeople from Wikipedia
import scraperwiki
import lxml.html
import urllib2

categories = ['http://en.wikipedia.org/wiki/Category:British_businesspeople',
              'http://en.wikipedia.org/wiki/Category:English_businesspeople',
              'http://en.wikipedia.org/wiki/Category:Scottish_businesspeople',
              'http://en.wikipedia.org/wiki/Category:Welsh_businesspeople',]

for category_url in categories:
    category_url_next = category_url
    while category_url_next is not None:
        response = urllib2.urlopen(category_url_next)
        tree = lxml.html.parse(response, base_url=category_url_next)
        
        for a in tree.xpath('//td/ul/li/a'):
            scraperwiki.sqlite.save(['url'], {'name': a.text, 'category_url': category_url, 'url': "http://en.wikipedia.org%s" % a.attrib['href']}, table_name='people')
    
        next_a = tree.xpath('//div[@id="mw-pages"]/a[.="next 200"]')
        if next_a:
            print "Continuing on %s" % category_url
            category_url_next = "http://en.wikipedia.org%s" % next_a[0].attrib['href']
        else:
            category_url_next = None
