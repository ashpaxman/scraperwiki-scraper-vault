# Wii Game Scraper
import scraperwiki
import lxml.html
import re

for page in range(0,20):
    url = "http://www.metacritic.com/browse/games/release-date/available/wii/name?view=detailed&page=%s" % page
    html = scraperwiki.scrape(url)
    root = lxml.html.fromstring(html)
    products = root.xpath("//ol[@class='list_products list_product_summaries']/li")
    for product in products:
        data = {}
        data['title'] = str(product.xpath("div/div/div/div/div/h3[@class='product_title']/a/text()")[0])
        data['url'] = str(product.xpath("div/div[2]/a/img/@src")[0])

        product_release = product.xpath("div/div/div/div[@class='more_stats extended_stats']/ul[@class='more_stats']/li[@class='stat release_date']/span[@class='data']/text()")
        if len(product_release) != 1:
            data['release'] = -1
        else:
            data['release'] = str(product_release[0])


        scraperwiki.log(data)
        scraperwiki.sqlite.save(unique_keys=['title','url','release'], data=data)# Wii Game Scraper
import scraperwiki
import lxml.html
import re

for page in range(0,20):
    url = "http://www.metacritic.com/browse/games/release-date/available/wii/name?view=detailed&page=%s" % page
    html = scraperwiki.scrape(url)
    root = lxml.html.fromstring(html)
    products = root.xpath("//ol[@class='list_products list_product_summaries']/li")
    for product in products:
        data = {}
        data['title'] = str(product.xpath("div/div/div/div/div/h3[@class='product_title']/a/text()")[0])
        data['url'] = str(product.xpath("div/div[2]/a/img/@src")[0])

        product_release = product.xpath("div/div/div/div[@class='more_stats extended_stats']/ul[@class='more_stats']/li[@class='stat release_date']/span[@class='data']/text()")
        if len(product_release) != 1:
            data['release'] = -1
        else:
            data['release'] = str(product_release[0])


        scraperwiki.log(data)
        scraperwiki.sqlite.save(unique_keys=['title','url','release'], data=data)