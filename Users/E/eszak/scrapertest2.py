import scraperwiki
html = scraperwiki.scrape('https://scraperwiki.com/hello_world.html')
print "Click on the ...more link to see the whole page"
print html

import lxml.html
root = lxml.html.fromstring(html) 
tds = root.cssselect('td')
for td in tds:
    print lxml.html.tostring(td)
    print td.text

for td in tds:
    record = { "td" : td.text }
    scraperwiki.sqlite.save(["td"], record)import scraperwiki
html = scraperwiki.scrape('https://scraperwiki.com/hello_world.html')
print "Click on the ...more link to see the whole page"
print html

import lxml.html
root = lxml.html.fromstring(html) 
tds = root.cssselect('td')
for td in tds:
    print lxml.html.tostring(td)
    print td.text

for td in tds:
    record = { "td" : td.text }
    scraperwiki.sqlite.save(["td"], record)