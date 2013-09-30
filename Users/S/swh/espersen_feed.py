import scraperwiki
from datetime import datetime
import re
import json
import urllib

sourcescraper = 'espersen'

scraperwiki.sqlite.attach(sourcescraper) 

keys =  scraperwiki.sqlite.execute('select * from `espersen`.swdata limit 0')['keys']
data =  scraperwiki.sqlite.select('* from `espersen`.swdata ORDER BY "date" DESC')


#meta
for row in data:
    updated = "%s" % (row.get('date'))
    break

print """<?xml version="1.0" encoding="utf-8"?>

<feed xmlns='http://www.w3.org/2005/Atom'>
    <title type='text'>Espersen DK News</title>
    <updated>%s</updated>
    <id>http://scraperwikiviews.com/run/espersen/?</id> 
    <link rel='self' type='application/atom+xml' href='http://scraperwikiviews.com/run/espersen/?'/>
    <generator uri='http://scraperwikiviews.com/run/espersen/?' version='1.0'></generator>""" % (updated) 

# rows
for row in data:
    title = row.get('title')
    date = row.get('date')
    summary = row.get('title')
    link = row.get('link') 

    updated = "%s" % (row.get('date')[:-9])
    printable = 1
    print """    <entry>
    <title>  %s - %s </title>
    <updated> %s </updated> 
    <summary type='html'>
    <![CDATA[
       <p><a href='%s'>%s</a></p>
    ]]>
    </summary>
    </entry>""" % (date[:-9], title, updated, link, summary)
print '</feed>'






import scraperwiki
from datetime import datetime
import re
import json
import urllib

sourcescraper = 'espersen'

scraperwiki.sqlite.attach(sourcescraper) 

keys =  scraperwiki.sqlite.execute('select * from `espersen`.swdata limit 0')['keys']
data =  scraperwiki.sqlite.select('* from `espersen`.swdata ORDER BY "date" DESC')


#meta
for row in data:
    updated = "%s" % (row.get('date'))
    break

print """<?xml version="1.0" encoding="utf-8"?>

<feed xmlns='http://www.w3.org/2005/Atom'>
    <title type='text'>Espersen DK News</title>
    <updated>%s</updated>
    <id>http://scraperwikiviews.com/run/espersen/?</id> 
    <link rel='self' type='application/atom+xml' href='http://scraperwikiviews.com/run/espersen/?'/>
    <generator uri='http://scraperwikiviews.com/run/espersen/?' version='1.0'></generator>""" % (updated) 

# rows
for row in data:
    title = row.get('title')
    date = row.get('date')
    summary = row.get('title')
    link = row.get('link') 

    updated = "%s" % (row.get('date')[:-9])
    printable = 1
    print """    <entry>
    <title>  %s - %s </title>
    <updated> %s </updated> 
    <summary type='html'>
    <![CDATA[
       <p><a href='%s'>%s</a></p>
    ]]>
    </summary>
    </entry>""" % (date[:-9], title, updated, link, summary)
print '</feed>'






