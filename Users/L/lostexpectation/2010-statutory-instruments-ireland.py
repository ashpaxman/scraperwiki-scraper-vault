import scraperwiki
import re

import BeautifulSoup
from datetime import datetime
from scraperwiki import datastore


# get the index of all from 2010
urlindex = "http://www.irishstatutebook.ie/2010/statutory.html"
htmlindex = scraperwiki.scrape(urlindex)
print htmlindex
sinos = re.findall('<a href="(/2010/en/si/\d+.html)">S.I. No. (\d+)/2010 — (.*?).</a>', htmlindex)

# for lk, no, title in sinos:
for lk, no, title in sinos:
    url = "http://www.irishstatutebook.ie"+lk
    page = scraperwiki.scrape(url)
    #print page 
   

    
    # http://www.irishstatutebook.ie/2010/en/si/0121.html
    #need to find act,ministry,minister|seal of courts etc
    dept = re.findall('(?si)<p style="display:block;">Minister (?:for|of )(.*?)</p>', page) # working cept courts
    #act powers conferred on me by
    #act = re.findall('(?si)powers conferred on (?:me by|them by) (.*?)\(No.', page) # working but with urls
    #def gettext(act):
    #  """Return the text within html, removing any HTML tags it contained."""
    #    cleaned = re.sub('<.*?>', '', act)  # remove tags
    #    cleaned = ' '.join(cleaned.split())  # collapse whitespace
    #    return cleaned
    
    #def dealWithLinks(actlinks):
    #    for link in act:
    #        href = link.get('href')
    #        name = link.text.replace("&nbsp;", "")
    
#def dealWithStructureLinks(structureLinks):
    #if href is not None:
    #        key = href.replace("/structures/data/index.cfm?id=", "")
    #        record = { "key" : key, "name" : name, "link" : base_url + href }
                                 
    #sealbody dept = re.search('(?si)<p style="display:block;">Minister (?:for|of )(.*?)</p>|<p style="display:block;">GIVEN under the seal of the (*.?),</p>', page)
    #dept = re.search('(?si)<p style="display:block;">Minister (?:for|of )(.*?)</p>|<p style="display:block;">GIVEN under the seal of the (*.?),</p>', page)
    #if dept != []: #notnone
    #    return []
    #else:
    #    print "Not a Dept", url
    #    dept = "courts or other"
       
    # if european directive 
    
    mdate = re.search(' of</i> (\d+)<i>.. (\w+)</i>, (2010).</p>', page)
    if mdate:
        date = mdate.group(1)+" "+mdate.group(2)+" 2010"
    else:
        print "No date on", url
        date = None
    msdate = re.search('(?si)<p style="display:block;">Given under (?:my Official Seal|my Hand|the Official Seal of the Government|the Official Seal of,? the Minister for Finance|the Seal of the Courts Service),</p>.*?<p style="display:block;">(\d+) (\w+) (2010)\.?</p>', page) 
    if msdate:
        sealdata = "%s %s %s" % msdate.groups()
    else:
        print "No seal date found", url, page
        sealdata = None  
    mnstr = re.findall('<p style="display:block;">WHEREAS I,|I, (.*?), Minister', page)

    
    data = {'url': url, 'title': title, 'number':no, 'date':date, 'sealdate':sealdata, 'mnstr':mnstr, 'dept':dept }#   'act':cleaned} # , 'sealbody':sealbody} # deptdata } 
    scraperwiki.sqlite.save(['url'], data)   
import scraperwiki
import re

import BeautifulSoup
from datetime import datetime
from scraperwiki import datastore


# get the index of all from 2010
urlindex = "http://www.irishstatutebook.ie/2010/statutory.html"
htmlindex = scraperwiki.scrape(urlindex)
print htmlindex
sinos = re.findall('<a href="(/2010/en/si/\d+.html)">S.I. No. (\d+)/2010 — (.*?).</a>', htmlindex)

# for lk, no, title in sinos:
for lk, no, title in sinos:
    url = "http://www.irishstatutebook.ie"+lk
    page = scraperwiki.scrape(url)
    #print page 
   

    
    # http://www.irishstatutebook.ie/2010/en/si/0121.html
    #need to find act,ministry,minister|seal of courts etc
    dept = re.findall('(?si)<p style="display:block;">Minister (?:for|of )(.*?)</p>', page) # working cept courts
    #act powers conferred on me by
    #act = re.findall('(?si)powers conferred on (?:me by|them by) (.*?)\(No.', page) # working but with urls
    #def gettext(act):
    #  """Return the text within html, removing any HTML tags it contained."""
    #    cleaned = re.sub('<.*?>', '', act)  # remove tags
    #    cleaned = ' '.join(cleaned.split())  # collapse whitespace
    #    return cleaned
    
    #def dealWithLinks(actlinks):
    #    for link in act:
    #        href = link.get('href')
    #        name = link.text.replace("&nbsp;", "")
    
#def dealWithStructureLinks(structureLinks):
    #if href is not None:
    #        key = href.replace("/structures/data/index.cfm?id=", "")
    #        record = { "key" : key, "name" : name, "link" : base_url + href }
                                 
    #sealbody dept = re.search('(?si)<p style="display:block;">Minister (?:for|of )(.*?)</p>|<p style="display:block;">GIVEN under the seal of the (*.?),</p>', page)
    #dept = re.search('(?si)<p style="display:block;">Minister (?:for|of )(.*?)</p>|<p style="display:block;">GIVEN under the seal of the (*.?),</p>', page)
    #if dept != []: #notnone
    #    return []
    #else:
    #    print "Not a Dept", url
    #    dept = "courts or other"
       
    # if european directive 
    
    mdate = re.search(' of</i> (\d+)<i>.. (\w+)</i>, (2010).</p>', page)
    if mdate:
        date = mdate.group(1)+" "+mdate.group(2)+" 2010"
    else:
        print "No date on", url
        date = None
    msdate = re.search('(?si)<p style="display:block;">Given under (?:my Official Seal|my Hand|the Official Seal of the Government|the Official Seal of,? the Minister for Finance|the Seal of the Courts Service),</p>.*?<p style="display:block;">(\d+) (\w+) (2010)\.?</p>', page) 
    if msdate:
        sealdata = "%s %s %s" % msdate.groups()
    else:
        print "No seal date found", url, page
        sealdata = None  
    mnstr = re.findall('<p style="display:block;">WHEREAS I,|I, (.*?), Minister', page)

    
    data = {'url': url, 'title': title, 'number':no, 'date':date, 'sealdate':sealdata, 'mnstr':mnstr, 'dept':dept }#   'act':cleaned} # , 'sealbody':sealbody} # deptdata } 
    scraperwiki.sqlite.save(['url'], data)   
import scraperwiki
import re

import BeautifulSoup
from datetime import datetime
from scraperwiki import datastore


# get the index of all from 2010
urlindex = "http://www.irishstatutebook.ie/2010/statutory.html"
htmlindex = scraperwiki.scrape(urlindex)
print htmlindex
sinos = re.findall('<a href="(/2010/en/si/\d+.html)">S.I. No. (\d+)/2010 — (.*?).</a>', htmlindex)

# for lk, no, title in sinos:
for lk, no, title in sinos:
    url = "http://www.irishstatutebook.ie"+lk
    page = scraperwiki.scrape(url)
    #print page 
   

    
    # http://www.irishstatutebook.ie/2010/en/si/0121.html
    #need to find act,ministry,minister|seal of courts etc
    dept = re.findall('(?si)<p style="display:block;">Minister (?:for|of )(.*?)</p>', page) # working cept courts
    #act powers conferred on me by
    #act = re.findall('(?si)powers conferred on (?:me by|them by) (.*?)\(No.', page) # working but with urls
    #def gettext(act):
    #  """Return the text within html, removing any HTML tags it contained."""
    #    cleaned = re.sub('<.*?>', '', act)  # remove tags
    #    cleaned = ' '.join(cleaned.split())  # collapse whitespace
    #    return cleaned
    
    #def dealWithLinks(actlinks):
    #    for link in act:
    #        href = link.get('href')
    #        name = link.text.replace("&nbsp;", "")
    
#def dealWithStructureLinks(structureLinks):
    #if href is not None:
    #        key = href.replace("/structures/data/index.cfm?id=", "")
    #        record = { "key" : key, "name" : name, "link" : base_url + href }
                                 
    #sealbody dept = re.search('(?si)<p style="display:block;">Minister (?:for|of )(.*?)</p>|<p style="display:block;">GIVEN under the seal of the (*.?),</p>', page)
    #dept = re.search('(?si)<p style="display:block;">Minister (?:for|of )(.*?)</p>|<p style="display:block;">GIVEN under the seal of the (*.?),</p>', page)
    #if dept != []: #notnone
    #    return []
    #else:
    #    print "Not a Dept", url
    #    dept = "courts or other"
       
    # if european directive 
    
    mdate = re.search(' of</i> (\d+)<i>.. (\w+)</i>, (2010).</p>', page)
    if mdate:
        date = mdate.group(1)+" "+mdate.group(2)+" 2010"
    else:
        print "No date on", url
        date = None
    msdate = re.search('(?si)<p style="display:block;">Given under (?:my Official Seal|my Hand|the Official Seal of the Government|the Official Seal of,? the Minister for Finance|the Seal of the Courts Service),</p>.*?<p style="display:block;">(\d+) (\w+) (2010)\.?</p>', page) 
    if msdate:
        sealdata = "%s %s %s" % msdate.groups()
    else:
        print "No seal date found", url, page
        sealdata = None  
    mnstr = re.findall('<p style="display:block;">WHEREAS I,|I, (.*?), Minister', page)

    
    data = {'url': url, 'title': title, 'number':no, 'date':date, 'sealdate':sealdata, 'mnstr':mnstr, 'dept':dept }#   'act':cleaned} # , 'sealbody':sealbody} # deptdata } 
    scraperwiki.sqlite.save(['url'], data)   
import scraperwiki
import re

import BeautifulSoup
from datetime import datetime
from scraperwiki import datastore


# get the index of all from 2010
urlindex = "http://www.irishstatutebook.ie/2010/statutory.html"
htmlindex = scraperwiki.scrape(urlindex)
print htmlindex
sinos = re.findall('<a href="(/2010/en/si/\d+.html)">S.I. No. (\d+)/2010 — (.*?).</a>', htmlindex)

# for lk, no, title in sinos:
for lk, no, title in sinos:
    url = "http://www.irishstatutebook.ie"+lk
    page = scraperwiki.scrape(url)
    #print page 
   

    
    # http://www.irishstatutebook.ie/2010/en/si/0121.html
    #need to find act,ministry,minister|seal of courts etc
    dept = re.findall('(?si)<p style="display:block;">Minister (?:for|of )(.*?)</p>', page) # working cept courts
    #act powers conferred on me by
    #act = re.findall('(?si)powers conferred on (?:me by|them by) (.*?)\(No.', page) # working but with urls
    #def gettext(act):
    #  """Return the text within html, removing any HTML tags it contained."""
    #    cleaned = re.sub('<.*?>', '', act)  # remove tags
    #    cleaned = ' '.join(cleaned.split())  # collapse whitespace
    #    return cleaned
    
    #def dealWithLinks(actlinks):
    #    for link in act:
    #        href = link.get('href')
    #        name = link.text.replace("&nbsp;", "")
    
#def dealWithStructureLinks(structureLinks):
    #if href is not None:
    #        key = href.replace("/structures/data/index.cfm?id=", "")
    #        record = { "key" : key, "name" : name, "link" : base_url + href }
                                 
    #sealbody dept = re.search('(?si)<p style="display:block;">Minister (?:for|of )(.*?)</p>|<p style="display:block;">GIVEN under the seal of the (*.?),</p>', page)
    #dept = re.search('(?si)<p style="display:block;">Minister (?:for|of )(.*?)</p>|<p style="display:block;">GIVEN under the seal of the (*.?),</p>', page)
    #if dept != []: #notnone
    #    return []
    #else:
    #    print "Not a Dept", url
    #    dept = "courts or other"
       
    # if european directive 
    
    mdate = re.search(' of</i> (\d+)<i>.. (\w+)</i>, (2010).</p>', page)
    if mdate:
        date = mdate.group(1)+" "+mdate.group(2)+" 2010"
    else:
        print "No date on", url
        date = None
    msdate = re.search('(?si)<p style="display:block;">Given under (?:my Official Seal|my Hand|the Official Seal of the Government|the Official Seal of,? the Minister for Finance|the Seal of the Courts Service),</p>.*?<p style="display:block;">(\d+) (\w+) (2010)\.?</p>', page) 
    if msdate:
        sealdata = "%s %s %s" % msdate.groups()
    else:
        print "No seal date found", url, page
        sealdata = None  
    mnstr = re.findall('<p style="display:block;">WHEREAS I,|I, (.*?), Minister', page)

    
    data = {'url': url, 'title': title, 'number':no, 'date':date, 'sealdate':sealdata, 'mnstr':mnstr, 'dept':dept }#   'act':cleaned} # , 'sealbody':sealbody} # deptdata } 
    scraperwiki.sqlite.save(['url'], data)   
