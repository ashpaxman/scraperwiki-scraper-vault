###################################################################################
# Twitter scraper - designed to be forked and used for more interesting things
###################################################################################

import scraperwiki
import simplejson
import urllib2

# Change QUERY to your search term of choice. 
# Examples: 'newsnight', 'from:bbcnewsnight', 'to:bbcnewsnight'

#This part defines the search
#You can look for hash tags or search terms
QUERY = 'vine.co/v/'
RESULTS_PER_PAGE = '100'
COORDINATES = '39.747322,-104.999496'
RADIUS = '25mi'
RESULT_TYPE = 'mixed'
NUM_PAGES = 100 

for page in range(1, NUM_PAGES+1):
    base_url = 'http://search.twitter.com/search.json?q=%s&rpp=%s&page=%s&geocode=%s,%s&result_type=%s' \
         % (urllib2.quote(QUERY), RESULTS_PER_PAGE, page,COORDINATES,RADIUS,RESULT_TYPE)
#Python is really particular about indentation.
    try:
        results_json = simplejson.loads(scraperwiki.scrape(base_url))
        for result in results_json['results']:
            #print result

#This is the information you're pulling from each Tweet.
            data = {}
            data['id'] = result['id']
            data['text'] = result['text']
            data['from_user'] = result['from_user']
            data['created_at'] = result['created_at']
            data['geo'] = result['geo']
#This prints a selection of the data.
            print data['from_user'], data['text'], data['geo']
            scraperwiki.sqlite.save(["id"], data) 
    except:
        print 'Oh dear, failed to scrape %s' % base_url
        break
###################################################################################
# Twitter scraper - designed to be forked and used for more interesting things
###################################################################################

import scraperwiki
import simplejson
import urllib2

# Change QUERY to your search term of choice. 
# Examples: 'newsnight', 'from:bbcnewsnight', 'to:bbcnewsnight'

#This part defines the search
#You can look for hash tags or search terms
QUERY = 'vine.co/v/'
RESULTS_PER_PAGE = '100'
COORDINATES = '39.747322,-104.999496'
RADIUS = '25mi'
RESULT_TYPE = 'mixed'
NUM_PAGES = 100 

for page in range(1, NUM_PAGES+1):
    base_url = 'http://search.twitter.com/search.json?q=%s&rpp=%s&page=%s&geocode=%s,%s&result_type=%s' \
         % (urllib2.quote(QUERY), RESULTS_PER_PAGE, page,COORDINATES,RADIUS,RESULT_TYPE)
#Python is really particular about indentation.
    try:
        results_json = simplejson.loads(scraperwiki.scrape(base_url))
        for result in results_json['results']:
            #print result

#This is the information you're pulling from each Tweet.
            data = {}
            data['id'] = result['id']
            data['text'] = result['text']
            data['from_user'] = result['from_user']
            data['created_at'] = result['created_at']
            data['geo'] = result['geo']
#This prints a selection of the data.
            print data['from_user'], data['text'], data['geo']
            scraperwiki.sqlite.save(["id"], data) 
    except:
        print 'Oh dear, failed to scrape %s' % base_url
        break
