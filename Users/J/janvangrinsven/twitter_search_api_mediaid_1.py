import scraperwiki
import simplejson

# retrieve a page
base_url = 'https://api.twitter.com/1.1/search/tweets.json?q=%'
q = 'offshoreleaks'
options = '&rpp=100&page='
page = 1

while 1:
    try:
        url = base_url + q
        html = scraperwiki.scrape(url)
        #print html
        soup = simplejson.loads(html)
        for result in soup['results']:
            data = {}
            data['id'] = result['id']
            data['text'] = result['text']
            data['from_user'] = result['from_user']
            data['created_at']= result['created_at']   


            # save records to the datastore
            scraperwiki.sqlite.save(["id"], data) 
        page = page + 1
    except:
        print str(page) + ' pages scraped'
        break

import scraperwiki
import simplejson

# retrieve a page
base_url = 'https://api.twitter.com/1.1/search/tweets.json?q=%'
q = 'offshoreleaks'
options = '&rpp=100&page='
page = 1

while 1:
    try:
        url = base_url + q
        html = scraperwiki.scrape(url)
        #print html
        soup = simplejson.loads(html)
        for result in soup['results']:
            data = {}
            data['id'] = result['id']
            data['text'] = result['text']
            data['from_user'] = result['from_user']
            data['created_at']= result['created_at']   


            # save records to the datastore
            scraperwiki.sqlite.save(["id"], data) 
        page = page + 1
    except:
        print str(page) + ' pages scraped'
        break

