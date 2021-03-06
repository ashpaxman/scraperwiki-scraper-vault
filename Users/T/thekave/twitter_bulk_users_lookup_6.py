import scraperwiki
import simplejson
import urllib2
from time import sleep

query_sets = []


def chunks(l, n):
    ''' 
    http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    '''
    return [l[i:i+n] for i in range(0, len(l), n)]


def bigquerysearch(queries = []):
    query_sets = chunks(queries, 200)
    for q in query_sets:
        sleep(1.05)
        search(q)


def search(queries = []):
    '''
    Get results from the Twitter Users/Lookup API! Change QUERY to IDs (user_id=%s) or usernames(screen_names=%s) of choice
    DOCS: https://dev.twitter.com/docs/api/1/get/users/lookup
    '''

    base_url = 'https://api.twitter.com/1/users/lookup.json?user_id=%s&include_entities=true' \
            % (urllib2.quote(','.join(queries)))
    try:
        results_json = simplejson.loads(scraperwiki.scrape(base_url))
        for result in results_json:
            data = {}
            data['id'] = result['id']
            
            data['screenname'] = result['screen_name']
            
            print data['id'], data['screenname']
            scraperwiki.sqlite.save(["id"], data) 
    except:
        print 'Oh dear, failed to scrape %s' % base_url
        raise

def bulklookup(queries = []):
    if len(queries) > 14999:
        print "Script did not run. Running script on more than 15,000 users in an hour could incur Twitter rate limiting."

    elif len(queries) > 400:
        print "That's a lot of users! Please be patient."
        bigquerysearch(queries)

    else:
        search(queries)
import scraperwiki
import simplejson
import urllib2
from time import sleep

query_sets = []


def chunks(l, n):
    ''' 
    http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    '''
    return [l[i:i+n] for i in range(0, len(l), n)]


def bigquerysearch(queries = []):
    query_sets = chunks(queries, 200)
    for q in query_sets:
        sleep(1.05)
        search(q)


def search(queries = []):
    '''
    Get results from the Twitter Users/Lookup API! Change QUERY to IDs (user_id=%s) or usernames(screen_names=%s) of choice
    DOCS: https://dev.twitter.com/docs/api/1/get/users/lookup
    '''

    base_url = 'https://api.twitter.com/1/users/lookup.json?user_id=%s&include_entities=true' \
            % (urllib2.quote(','.join(queries)))
    try:
        results_json = simplejson.loads(scraperwiki.scrape(base_url))
        for result in results_json:
            data = {}
            data['id'] = result['id']
            
            data['screenname'] = result['screen_name']
            
            print data['id'], data['screenname']
            scraperwiki.sqlite.save(["id"], data) 
    except:
        print 'Oh dear, failed to scrape %s' % base_url
        raise

def bulklookup(queries = []):
    if len(queries) > 14999:
        print "Script did not run. Running script on more than 15,000 users in an hour could incur Twitter rate limiting."

    elif len(queries) > 400:
        print "That's a lot of users! Please be patient."
        bigquerysearch(queries)

    else:
        search(queries)
