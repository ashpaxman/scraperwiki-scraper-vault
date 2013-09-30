###################################################################################
# Twitter API scraper - designed to be forked and used for more interesting things
###################################################################################

import scraperwiki
import simplejson
import urllib2

# Get results from the Twitter API! Change QUERY to your search term of choice. 
# Examples: 'newsnight', 'from:bbcnewsnight', 'to:bbcnewsnight'
QUERY = 'From:TheFunnyTeens'
RESULTS_PER_PAGE = '100'
LANGUAGE = 'en'
NUM_PAGES = 5 

for page in range(1, NUM_PAGES+1):
    base_url = 'http://search.twitter.com/search.json?q=%s&rpp=%s&lang=%s&page=%s' \
         % (urllib2.quote(QUERY), RESULTS_PER_PAGE, LANGUAGE, page)
    try:
        results_json = simplejson.loads(scraperwiki.scrape(base_url))
        for result in results_json['results']:
            data = {}
            data['id'] = result['id']
            data['text'] = result['text']
            #data['from_user'] = result['from_user']
            #print data['from_user'], data['text']
            print data['text']
            scraperwiki.sqlite.save(["id"], data) 
            scraperwiki.sqlite.save(["text"], data) 
    except:
        print 'Oh dear, failed to scrape %s' % base_url###################################################################################
# Twitter API scraper - designed to be forked and used for more interesting things
###################################################################################

import scraperwiki
import simplejson
import urllib2

# Get results from the Twitter API! Change QUERY to your search term of choice. 
# Examples: 'newsnight', 'from:bbcnewsnight', 'to:bbcnewsnight'
QUERY = 'From:TheFunnyTeens'
RESULTS_PER_PAGE = '100'
LANGUAGE = 'en'
NUM_PAGES = 5 

for page in range(1, NUM_PAGES+1):
    base_url = 'http://search.twitter.com/search.json?q=%s&rpp=%s&lang=%s&page=%s' \
         % (urllib2.quote(QUERY), RESULTS_PER_PAGE, LANGUAGE, page)
    try:
        results_json = simplejson.loads(scraperwiki.scrape(base_url))
        for result in results_json['results']:
            data = {}
            data['id'] = result['id']
            data['text'] = result['text']
            #data['from_user'] = result['from_user']
            #print data['from_user'], data['text']
            print data['text']
            scraperwiki.sqlite.save(["id"], data) 
            scraperwiki.sqlite.save(["text"], data) 
    except:
        print 'Oh dear, failed to scrape %s' % base_url