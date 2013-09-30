#Scraper for Craigslist for analytics.
import scraperwiki
import lxml.html
crawlpages=20
target = "http://london.craigslist.co.uk/sya/"
page = lxml.html.fromstring(scraperwiki.scrape(target))
#construct an array of placenames
places=[n.text.strip(" ").lstrip("(").rstrip(")").strip(" ") for n in page.cssselect(".itempn>*")]
for ipage in [lxml.html.fromstring(
        scraperwiki.scrape(
            target+"index"+str(n*100)+".html"
        )
    ) for n in range(1,crawlpages+1)]:
    places=places + [n.text.strip(" ").lstrip("(").rstrip(")").strip(" ") for n in ipage.cssselect(".itempn>*")]
for place in places:
    scraperwiki.sqlite.save(unique_keys=['loc'],data={'loc':place})#Scraper for Craigslist for analytics.
import scraperwiki
import lxml.html
crawlpages=20
target = "http://london.craigslist.co.uk/sya/"
page = lxml.html.fromstring(scraperwiki.scrape(target))
#construct an array of placenames
places=[n.text.strip(" ").lstrip("(").rstrip(")").strip(" ") for n in page.cssselect(".itempn>*")]
for ipage in [lxml.html.fromstring(
        scraperwiki.scrape(
            target+"index"+str(n*100)+".html"
        )
    ) for n in range(1,crawlpages+1)]:
    places=places + [n.text.strip(" ").lstrip("(").rstrip(")").strip(" ") for n in ipage.cssselect(".itempn>*")]
for place in places:
    scraperwiki.sqlite.save(unique_keys=['loc'],data={'loc':place})