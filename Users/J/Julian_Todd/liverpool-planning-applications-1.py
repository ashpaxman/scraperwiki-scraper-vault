import scraperwiki
import mechanize
import datetime
import re
import urllib2
import cookielib
import os

# http://hpzworkstations.com/
# Very involved Liverpool planning scraper attempting to get all fields out of their database, which goes back to 1996
# Searches for all applications on a single day, and handles the pagination of the list of applications which requires cookies to execute
# mechanize is unable to follow the links itself because the href values are stuffed with linefeeds, &#0D strings and control characters (see CleanCrapFromLink())

liverpoolplanningurl = "http://northgate.liverpool.gov.uk/planningexploreraa/"

# types of fields that have dates in them
decisionlist = ["Refuse", "Withdrawn", "Approve with Conditions", "Approve without Conditions", "Allowed", "Dismissed", "Prior Approval Given",
                "Split Decision", "Certificate of Lawfulness - Granted", 
                "Final Decision - Dismissed", "Final Decision - Withdrawn", "Conditions Discharged", "No Objections"]
datetypes = ["Date %s" % d  for d in decisionlist ]
datetypes.extend(["Date Registered", "Comments Until", "Appeal Lodged", "Application Registered", "Date Decision"])


cj = cookielib.CookieJar()  # also used by the mechanize.Browser
urllibopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllibopener.addheaders.append (('x-runid', os.environ['RUNID']))

def scrape(url, refererurl):
    try:
        fin = urllibopener.open(url)
        text = fin.read()
        fin.close()
    except:
        log("gone bad " + url)
        return ""
    return text

    #req = urllib2.Request(data["url"])
    #req.add_header('Referer', refererurl)
    #rr = urllib2.urlopen(req)


import time
def log(s):
    time.sleep(0.15)
    print str(s)
    time.sleep(0.2)

def CleanupData(data):
    # convert the location
    if 'Location Co ordinates' in data:
        mcoords = re.match('Easting(\d*)Northing(\d*)$', data['Location Co ordinates'])
        if mcoords.group(1) and mcoords.group(2):  # missing coordinates leave the numbers blank
            seasting = mcoords.group(1)
            snorthing = mcoords.group(2)
            if len(seasting) == 6:
                seasting += "0"
            if len(snorthing) == 6:
                snorthing += "0"
            easting = int(seasting) / 10.0
            northing = int(snorthing) / 10.0
            data["latlng"] = scraperwiki.geo.os_easting_northing_to_latlng(easting, northing)
            data["location"] = "OSEastingNorthing(%f, %f)" % (easting, northing)
        del data['Location Co ordinates']

    # markup dates
    for k in data:
        if k in datetypes:
            mdate = re.match("\s*(\d\d)-(\d\d)-(\d\d\d\d)$", data[k])
            if mdate:
                data[k] = datetime.date(int(mdate.group(3)), int(mdate.group(2)), int(mdate.group(1)))
            else:
                log("Bad date %s %s" % (k, data[k]))

    # separate telephone numbers from case officer
    if "Case Officer / Tel" in data:
        mcaseofficertel = re.match("(.*?)\s*(\d+)$", data["Case Officer / Tel"])
        if mcaseofficertel:
            caseofficer = mcaseofficertel.group(1)
            data["telephone"] = mcaseofficertel.group(2)
        else:
            caseofficer = data["Case Officer / Tel"]
        if caseofficer != data["Planning Officer"]:
            log("Planning/Case %s %s" % (data["Planning Officer"], caseofficer))
        del data["Case Officer / Tel"]
    
    if "Applicant" in data:
        data["Applicant"] = re.sub("&amp;", "&", data["Applicant"])
    if "Agent" in data:
        data["Agent"] = re.sub("&amp;", "&", data["Agent"])

    data["date"] = data["Date Registered"]

    
            
# there are multiple ul lists containing duplicate entries on the
def ParsePlanningDetails(data, text):
    dets = re.search("(?i)<h1>Details Page for Planning Application\xc2\xa0-\xc2\xa0(.*)</h1>", text)
    if not dets:
        log("failed: " + text)
        return
    if data["Application Number"] != dets.group(1):
        log("Application num failure %s %s" % (data["Application Number"], dets.group(1)))
    
    # all relevant lists
    ulists = re.findall("(?si)<ul class=\"list\">(.*?)</ul>", text)
    for ul in ulists[:-1]: # the last list leads to more links

        # all rows in relevant lists
        kv = re.findall("(?s)<li>\s*<div>\s*<span>\s*(.*?)\s*</span>\s*(.*?)\s*</div>\s*</li>", ul)
        #log("= " + str(kv))
        for k, v in kv:
            lv = re.sub("&#xD;|&#xA;|\xc2|\xa0|\r", "", v).strip()
            lv = re.sub("é", "e", lv)
            lv = re.sub("\xbd|\xbf", "?", lv)
            #log("kv %s,%s" % (k, lv))
            lv = unicode(lv, errors="replace")
            
            if k not in data:
                if lv:  # only include if there is an entry here
                    data[k] = lv
            elif data[k] != lv:
                dv = data[k]
                if k in ["Decision", "Appeal Decision"] and data[k] in decisionlist:
                    if len(lv) < len(dv):
                        dv, lv = lv, dv  # sometimes the date is in the index
                    if lv[:len(dv)] == dv:
                        data["Date " + k] = lv[len(data[k])+1:]
                    else:
                        log("FDetails don't match: %s %s %s" % (k, data[k], lv))
                elif re.sub("\s", "", dv) != re.sub("\s", "", lv):
                    log("Details don't match: :%s: :%s: :%s:" % (k, data[k], lv))
            


def CleanCrapFromLink(surl, clen):
    clen = re.sub("&#xD;|&#xA;|\t", "", clen)
    clen = re.sub(" ", "%20", clen)
    clen = re.sub("&amp;", "&", clen)
    return surl + clen

                            
def ParseSearchResultTableRow(surl, headers, cols):
    assert len(headers) == len(cols), cols
    data = dict(zip(headers, cols))
    
    # separate link and application number
    mappl = re.search('(?si)\s*<a class="data_text" href="(StdDetails.aspx?[^\"]*)">([^<]*)</a>', data["Application Number"])
    data["Application Number"] = mappl.group(2)
    data["url"] = CleanCrapFromLink(surl, mappl.group(1))
    
    return data


def ParseSearchResultTable(surl, text):

    # table with results
    mtable = re.search('(?s)<table[^>]*? summary=\"Results of the Search\"[^>]*?(.*?)</table>', text)
    if not mtable:
        if not re.search('No Records Found.', text):
            log("missing No records: " + re.sub("<", "&lt;", text))
        return [ ]

    # rows
    rows = re.findall("(?si)<tr[^>]*>(.*?)</tr>", mtable.group(1))
    headers = re.findall("<th class=\"data_header\">(.*?)</th>", rows[0])
     
    # process each application in table
    results = [ ]
    for row in rows[1:]:
        cols = re.findall("(?si)<td.*?>(.*?)</td>", row)                          
        aproc = ParseSearchResultTableRow(surl, headers, cols)
        results.append(aproc)
    return results
    
                                          
def ScrapePlanningApplications(lastday, daysback):
    firstday = lastday - datetime.timedelta(days=daysback)
    #log("Doing " + str(firstday))
    
    cj.clear()
    br = mechanize.Browser()
    br.addheaders = [ [ 'x-runid', os.environ['RUNID'] ] ]
    
    
    br.set_cookiejar(cj)
    br.open(liverpoolplanningurl)
            
    br.select_form(name="M3Form")

    br["dateStart"] = firstday.strftime("%d/%m/%Y")    
    br["dateEnd"] = lastday.strftime("%d/%m/%Y")
    br["rbGroup"] = ["rbRange"]
    g = br.submit()
    tabletext = g.read()
                  
    surl = re.sub("(?s)StdResults.*$", "", br.geturl())
        
    npages, nrecords = 0, 0
    refererurl = br.geturl()
    
    while True:
        rows = ParseSearchResultTable(surl, tabletext)
        for data in rows:
            #log(nrecords)
            ParsePlanningDetails(data, scrape(data["url"], refererurl))
            CleanupData(data)
            #log("-  " + str(data))
            scraperwiki.datastore.save(unique_keys=["Application Number"], data=data)
            nrecords += 1
        
        mnextlink = re.search('(?s)<a class="noborder" href="(StdResults.aspx[^"]*?)"><img src="/PlanningExplorerAA/SiteFiles/Skins/Default_AA/Images/arrowr.gif" alt="Go to next page "', tabletext)
        if not mnextlink:
            break
        
        nexturl = CleanCrapFromLink(surl, mnextlink.group(1))            
        npages += 1
        log("Page %d %s" % (npages, nexturl))
        
        tabletext = scrape(nexturl, refererurl)
        #log(re.sub("<", "&lt;", tabletext))
        refererurl = nexturl
        #break
    return nrecords, npages



# iterate through day by day
day = datetime.date.today()
# all of 2008-2006 done 
# 
#day = datetime.date(2005, 7, 6)  # run back to 7/17
for i in range(30):
    sday = day.strftime("%d/%m/%Y")
    pday = None # scraperwiki.page_cache.getpagebyname(sday)
    if not pday:
        nrecords, npages = ScrapePlanningApplications(day, 0)
        pday =  "%d %d" % (nrecords, npages)
        log("Scraped %d from %s" % (nrecords, sday))
        #scraperwiki.page_cache.savepage("dayrec", sday, pday)
    else:
        log("skipping %s %s" % (sday, pday))
    day = day - datetime.timedelta(days=1)

        



import scraperwiki
import mechanize
import datetime
import re
import urllib2
import cookielib
import os

# http://hpzworkstations.com/
# Very involved Liverpool planning scraper attempting to get all fields out of their database, which goes back to 1996
# Searches for all applications on a single day, and handles the pagination of the list of applications which requires cookies to execute
# mechanize is unable to follow the links itself because the href values are stuffed with linefeeds, &#0D strings and control characters (see CleanCrapFromLink())

liverpoolplanningurl = "http://northgate.liverpool.gov.uk/planningexploreraa/"

# types of fields that have dates in them
decisionlist = ["Refuse", "Withdrawn", "Approve with Conditions", "Approve without Conditions", "Allowed", "Dismissed", "Prior Approval Given",
                "Split Decision", "Certificate of Lawfulness - Granted", 
                "Final Decision - Dismissed", "Final Decision - Withdrawn", "Conditions Discharged", "No Objections"]
datetypes = ["Date %s" % d  for d in decisionlist ]
datetypes.extend(["Date Registered", "Comments Until", "Appeal Lodged", "Application Registered", "Date Decision"])


cj = cookielib.CookieJar()  # also used by the mechanize.Browser
urllibopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllibopener.addheaders.append (('x-runid', os.environ['RUNID']))

def scrape(url, refererurl):
    try:
        fin = urllibopener.open(url)
        text = fin.read()
        fin.close()
    except:
        log("gone bad " + url)
        return ""
    return text

    #req = urllib2.Request(data["url"])
    #req.add_header('Referer', refererurl)
    #rr = urllib2.urlopen(req)


import time
def log(s):
    time.sleep(0.15)
    print str(s)
    time.sleep(0.2)

def CleanupData(data):
    # convert the location
    if 'Location Co ordinates' in data:
        mcoords = re.match('Easting(\d*)Northing(\d*)$', data['Location Co ordinates'])
        if mcoords.group(1) and mcoords.group(2):  # missing coordinates leave the numbers blank
            seasting = mcoords.group(1)
            snorthing = mcoords.group(2)
            if len(seasting) == 6:
                seasting += "0"
            if len(snorthing) == 6:
                snorthing += "0"
            easting = int(seasting) / 10.0
            northing = int(snorthing) / 10.0
            data["latlng"] = scraperwiki.geo.os_easting_northing_to_latlng(easting, northing)
            data["location"] = "OSEastingNorthing(%f, %f)" % (easting, northing)
        del data['Location Co ordinates']

    # markup dates
    for k in data:
        if k in datetypes:
            mdate = re.match("\s*(\d\d)-(\d\d)-(\d\d\d\d)$", data[k])
            if mdate:
                data[k] = datetime.date(int(mdate.group(3)), int(mdate.group(2)), int(mdate.group(1)))
            else:
                log("Bad date %s %s" % (k, data[k]))

    # separate telephone numbers from case officer
    if "Case Officer / Tel" in data:
        mcaseofficertel = re.match("(.*?)\s*(\d+)$", data["Case Officer / Tel"])
        if mcaseofficertel:
            caseofficer = mcaseofficertel.group(1)
            data["telephone"] = mcaseofficertel.group(2)
        else:
            caseofficer = data["Case Officer / Tel"]
        if caseofficer != data["Planning Officer"]:
            log("Planning/Case %s %s" % (data["Planning Officer"], caseofficer))
        del data["Case Officer / Tel"]
    
    if "Applicant" in data:
        data["Applicant"] = re.sub("&amp;", "&", data["Applicant"])
    if "Agent" in data:
        data["Agent"] = re.sub("&amp;", "&", data["Agent"])

    data["date"] = data["Date Registered"]

    
            
# there are multiple ul lists containing duplicate entries on the
def ParsePlanningDetails(data, text):
    dets = re.search("(?i)<h1>Details Page for Planning Application\xc2\xa0-\xc2\xa0(.*)</h1>", text)
    if not dets:
        log("failed: " + text)
        return
    if data["Application Number"] != dets.group(1):
        log("Application num failure %s %s" % (data["Application Number"], dets.group(1)))
    
    # all relevant lists
    ulists = re.findall("(?si)<ul class=\"list\">(.*?)</ul>", text)
    for ul in ulists[:-1]: # the last list leads to more links

        # all rows in relevant lists
        kv = re.findall("(?s)<li>\s*<div>\s*<span>\s*(.*?)\s*</span>\s*(.*?)\s*</div>\s*</li>", ul)
        #log("= " + str(kv))
        for k, v in kv:
            lv = re.sub("&#xD;|&#xA;|\xc2|\xa0|\r", "", v).strip()
            lv = re.sub("é", "e", lv)
            lv = re.sub("\xbd|\xbf", "?", lv)
            #log("kv %s,%s" % (k, lv))
            lv = unicode(lv, errors="replace")
            
            if k not in data:
                if lv:  # only include if there is an entry here
                    data[k] = lv
            elif data[k] != lv:
                dv = data[k]
                if k in ["Decision", "Appeal Decision"] and data[k] in decisionlist:
                    if len(lv) < len(dv):
                        dv, lv = lv, dv  # sometimes the date is in the index
                    if lv[:len(dv)] == dv:
                        data["Date " + k] = lv[len(data[k])+1:]
                    else:
                        log("FDetails don't match: %s %s %s" % (k, data[k], lv))
                elif re.sub("\s", "", dv) != re.sub("\s", "", lv):
                    log("Details don't match: :%s: :%s: :%s:" % (k, data[k], lv))
            


def CleanCrapFromLink(surl, clen):
    clen = re.sub("&#xD;|&#xA;|\t", "", clen)
    clen = re.sub(" ", "%20", clen)
    clen = re.sub("&amp;", "&", clen)
    return surl + clen

                            
def ParseSearchResultTableRow(surl, headers, cols):
    assert len(headers) == len(cols), cols
    data = dict(zip(headers, cols))
    
    # separate link and application number
    mappl = re.search('(?si)\s*<a class="data_text" href="(StdDetails.aspx?[^\"]*)">([^<]*)</a>', data["Application Number"])
    data["Application Number"] = mappl.group(2)
    data["url"] = CleanCrapFromLink(surl, mappl.group(1))
    
    return data


def ParseSearchResultTable(surl, text):

    # table with results
    mtable = re.search('(?s)<table[^>]*? summary=\"Results of the Search\"[^>]*?(.*?)</table>', text)
    if not mtable:
        if not re.search('No Records Found.', text):
            log("missing No records: " + re.sub("<", "&lt;", text))
        return [ ]

    # rows
    rows = re.findall("(?si)<tr[^>]*>(.*?)</tr>", mtable.group(1))
    headers = re.findall("<th class=\"data_header\">(.*?)</th>", rows[0])
     
    # process each application in table
    results = [ ]
    for row in rows[1:]:
        cols = re.findall("(?si)<td.*?>(.*?)</td>", row)                          
        aproc = ParseSearchResultTableRow(surl, headers, cols)
        results.append(aproc)
    return results
    
                                          
def ScrapePlanningApplications(lastday, daysback):
    firstday = lastday - datetime.timedelta(days=daysback)
    #log("Doing " + str(firstday))
    
    cj.clear()
    br = mechanize.Browser()
    br.addheaders = [ [ 'x-runid', os.environ['RUNID'] ] ]
    
    
    br.set_cookiejar(cj)
    br.open(liverpoolplanningurl)
            
    br.select_form(name="M3Form")

    br["dateStart"] = firstday.strftime("%d/%m/%Y")    
    br["dateEnd"] = lastday.strftime("%d/%m/%Y")
    br["rbGroup"] = ["rbRange"]
    g = br.submit()
    tabletext = g.read()
                  
    surl = re.sub("(?s)StdResults.*$", "", br.geturl())
        
    npages, nrecords = 0, 0
    refererurl = br.geturl()
    
    while True:
        rows = ParseSearchResultTable(surl, tabletext)
        for data in rows:
            #log(nrecords)
            ParsePlanningDetails(data, scrape(data["url"], refererurl))
            CleanupData(data)
            #log("-  " + str(data))
            scraperwiki.datastore.save(unique_keys=["Application Number"], data=data)
            nrecords += 1
        
        mnextlink = re.search('(?s)<a class="noborder" href="(StdResults.aspx[^"]*?)"><img src="/PlanningExplorerAA/SiteFiles/Skins/Default_AA/Images/arrowr.gif" alt="Go to next page "', tabletext)
        if not mnextlink:
            break
        
        nexturl = CleanCrapFromLink(surl, mnextlink.group(1))            
        npages += 1
        log("Page %d %s" % (npages, nexturl))
        
        tabletext = scrape(nexturl, refererurl)
        #log(re.sub("<", "&lt;", tabletext))
        refererurl = nexturl
        #break
    return nrecords, npages



# iterate through day by day
day = datetime.date.today()
# all of 2008-2006 done 
# 
#day = datetime.date(2005, 7, 6)  # run back to 7/17
for i in range(30):
    sday = day.strftime("%d/%m/%Y")
    pday = None # scraperwiki.page_cache.getpagebyname(sday)
    if not pday:
        nrecords, npages = ScrapePlanningApplications(day, 0)
        pday =  "%d %d" % (nrecords, npages)
        log("Scraped %d from %s" % (nrecords, sday))
        #scraperwiki.page_cache.savepage("dayrec", sday, pday)
    else:
        log("skipping %s %s" % (sday, pday))
    day = day - datetime.timedelta(days=1)

        



import scraperwiki
import mechanize
import datetime
import re
import urllib2
import cookielib
import os

# http://hpzworkstations.com/
# Very involved Liverpool planning scraper attempting to get all fields out of their database, which goes back to 1996
# Searches for all applications on a single day, and handles the pagination of the list of applications which requires cookies to execute
# mechanize is unable to follow the links itself because the href values are stuffed with linefeeds, &#0D strings and control characters (see CleanCrapFromLink())

liverpoolplanningurl = "http://northgate.liverpool.gov.uk/planningexploreraa/"

# types of fields that have dates in them
decisionlist = ["Refuse", "Withdrawn", "Approve with Conditions", "Approve without Conditions", "Allowed", "Dismissed", "Prior Approval Given",
                "Split Decision", "Certificate of Lawfulness - Granted", 
                "Final Decision - Dismissed", "Final Decision - Withdrawn", "Conditions Discharged", "No Objections"]
datetypes = ["Date %s" % d  for d in decisionlist ]
datetypes.extend(["Date Registered", "Comments Until", "Appeal Lodged", "Application Registered", "Date Decision"])


cj = cookielib.CookieJar()  # also used by the mechanize.Browser
urllibopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllibopener.addheaders.append (('x-runid', os.environ['RUNID']))

def scrape(url, refererurl):
    try:
        fin = urllibopener.open(url)
        text = fin.read()
        fin.close()
    except:
        log("gone bad " + url)
        return ""
    return text

    #req = urllib2.Request(data["url"])
    #req.add_header('Referer', refererurl)
    #rr = urllib2.urlopen(req)


import time
def log(s):
    time.sleep(0.15)
    print str(s)
    time.sleep(0.2)

def CleanupData(data):
    # convert the location
    if 'Location Co ordinates' in data:
        mcoords = re.match('Easting(\d*)Northing(\d*)$', data['Location Co ordinates'])
        if mcoords.group(1) and mcoords.group(2):  # missing coordinates leave the numbers blank
            seasting = mcoords.group(1)
            snorthing = mcoords.group(2)
            if len(seasting) == 6:
                seasting += "0"
            if len(snorthing) == 6:
                snorthing += "0"
            easting = int(seasting) / 10.0
            northing = int(snorthing) / 10.0
            data["latlng"] = scraperwiki.geo.os_easting_northing_to_latlng(easting, northing)
            data["location"] = "OSEastingNorthing(%f, %f)" % (easting, northing)
        del data['Location Co ordinates']

    # markup dates
    for k in data:
        if k in datetypes:
            mdate = re.match("\s*(\d\d)-(\d\d)-(\d\d\d\d)$", data[k])
            if mdate:
                data[k] = datetime.date(int(mdate.group(3)), int(mdate.group(2)), int(mdate.group(1)))
            else:
                log("Bad date %s %s" % (k, data[k]))

    # separate telephone numbers from case officer
    if "Case Officer / Tel" in data:
        mcaseofficertel = re.match("(.*?)\s*(\d+)$", data["Case Officer / Tel"])
        if mcaseofficertel:
            caseofficer = mcaseofficertel.group(1)
            data["telephone"] = mcaseofficertel.group(2)
        else:
            caseofficer = data["Case Officer / Tel"]
        if caseofficer != data["Planning Officer"]:
            log("Planning/Case %s %s" % (data["Planning Officer"], caseofficer))
        del data["Case Officer / Tel"]
    
    if "Applicant" in data:
        data["Applicant"] = re.sub("&amp;", "&", data["Applicant"])
    if "Agent" in data:
        data["Agent"] = re.sub("&amp;", "&", data["Agent"])

    data["date"] = data["Date Registered"]

    
            
# there are multiple ul lists containing duplicate entries on the
def ParsePlanningDetails(data, text):
    dets = re.search("(?i)<h1>Details Page for Planning Application\xc2\xa0-\xc2\xa0(.*)</h1>", text)
    if not dets:
        log("failed: " + text)
        return
    if data["Application Number"] != dets.group(1):
        log("Application num failure %s %s" % (data["Application Number"], dets.group(1)))
    
    # all relevant lists
    ulists = re.findall("(?si)<ul class=\"list\">(.*?)</ul>", text)
    for ul in ulists[:-1]: # the last list leads to more links

        # all rows in relevant lists
        kv = re.findall("(?s)<li>\s*<div>\s*<span>\s*(.*?)\s*</span>\s*(.*?)\s*</div>\s*</li>", ul)
        #log("= " + str(kv))
        for k, v in kv:
            lv = re.sub("&#xD;|&#xA;|\xc2|\xa0|\r", "", v).strip()
            lv = re.sub("é", "e", lv)
            lv = re.sub("\xbd|\xbf", "?", lv)
            #log("kv %s,%s" % (k, lv))
            lv = unicode(lv, errors="replace")
            
            if k not in data:
                if lv:  # only include if there is an entry here
                    data[k] = lv
            elif data[k] != lv:
                dv = data[k]
                if k in ["Decision", "Appeal Decision"] and data[k] in decisionlist:
                    if len(lv) < len(dv):
                        dv, lv = lv, dv  # sometimes the date is in the index
                    if lv[:len(dv)] == dv:
                        data["Date " + k] = lv[len(data[k])+1:]
                    else:
                        log("FDetails don't match: %s %s %s" % (k, data[k], lv))
                elif re.sub("\s", "", dv) != re.sub("\s", "", lv):
                    log("Details don't match: :%s: :%s: :%s:" % (k, data[k], lv))
            


def CleanCrapFromLink(surl, clen):
    clen = re.sub("&#xD;|&#xA;|\t", "", clen)
    clen = re.sub(" ", "%20", clen)
    clen = re.sub("&amp;", "&", clen)
    return surl + clen

                            
def ParseSearchResultTableRow(surl, headers, cols):
    assert len(headers) == len(cols), cols
    data = dict(zip(headers, cols))
    
    # separate link and application number
    mappl = re.search('(?si)\s*<a class="data_text" href="(StdDetails.aspx?[^\"]*)">([^<]*)</a>', data["Application Number"])
    data["Application Number"] = mappl.group(2)
    data["url"] = CleanCrapFromLink(surl, mappl.group(1))
    
    return data


def ParseSearchResultTable(surl, text):

    # table with results
    mtable = re.search('(?s)<table[^>]*? summary=\"Results of the Search\"[^>]*?(.*?)</table>', text)
    if not mtable:
        if not re.search('No Records Found.', text):
            log("missing No records: " + re.sub("<", "&lt;", text))
        return [ ]

    # rows
    rows = re.findall("(?si)<tr[^>]*>(.*?)</tr>", mtable.group(1))
    headers = re.findall("<th class=\"data_header\">(.*?)</th>", rows[0])
     
    # process each application in table
    results = [ ]
    for row in rows[1:]:
        cols = re.findall("(?si)<td.*?>(.*?)</td>", row)                          
        aproc = ParseSearchResultTableRow(surl, headers, cols)
        results.append(aproc)
    return results
    
                                          
def ScrapePlanningApplications(lastday, daysback):
    firstday = lastday - datetime.timedelta(days=daysback)
    #log("Doing " + str(firstday))
    
    cj.clear()
    br = mechanize.Browser()
    br.addheaders = [ [ 'x-runid', os.environ['RUNID'] ] ]
    
    
    br.set_cookiejar(cj)
    br.open(liverpoolplanningurl)
            
    br.select_form(name="M3Form")

    br["dateStart"] = firstday.strftime("%d/%m/%Y")    
    br["dateEnd"] = lastday.strftime("%d/%m/%Y")
    br["rbGroup"] = ["rbRange"]
    g = br.submit()
    tabletext = g.read()
                  
    surl = re.sub("(?s)StdResults.*$", "", br.geturl())
        
    npages, nrecords = 0, 0
    refererurl = br.geturl()
    
    while True:
        rows = ParseSearchResultTable(surl, tabletext)
        for data in rows:
            #log(nrecords)
            ParsePlanningDetails(data, scrape(data["url"], refererurl))
            CleanupData(data)
            #log("-  " + str(data))
            scraperwiki.datastore.save(unique_keys=["Application Number"], data=data)
            nrecords += 1
        
        mnextlink = re.search('(?s)<a class="noborder" href="(StdResults.aspx[^"]*?)"><img src="/PlanningExplorerAA/SiteFiles/Skins/Default_AA/Images/arrowr.gif" alt="Go to next page "', tabletext)
        if not mnextlink:
            break
        
        nexturl = CleanCrapFromLink(surl, mnextlink.group(1))            
        npages += 1
        log("Page %d %s" % (npages, nexturl))
        
        tabletext = scrape(nexturl, refererurl)
        #log(re.sub("<", "&lt;", tabletext))
        refererurl = nexturl
        #break
    return nrecords, npages



# iterate through day by day
day = datetime.date.today()
# all of 2008-2006 done 
# 
#day = datetime.date(2005, 7, 6)  # run back to 7/17
for i in range(30):
    sday = day.strftime("%d/%m/%Y")
    pday = None # scraperwiki.page_cache.getpagebyname(sday)
    if not pday:
        nrecords, npages = ScrapePlanningApplications(day, 0)
        pday =  "%d %d" % (nrecords, npages)
        log("Scraped %d from %s" % (nrecords, sday))
        #scraperwiki.page_cache.savepage("dayrec", sday, pday)
    else:
        log("skipping %s %s" % (sday, pday))
    day = day - datetime.timedelta(days=1)

        



import scraperwiki
import mechanize
import datetime
import re
import urllib2
import cookielib
import os

# http://hpzworkstations.com/
# Very involved Liverpool planning scraper attempting to get all fields out of their database, which goes back to 1996
# Searches for all applications on a single day, and handles the pagination of the list of applications which requires cookies to execute
# mechanize is unable to follow the links itself because the href values are stuffed with linefeeds, &#0D strings and control characters (see CleanCrapFromLink())

liverpoolplanningurl = "http://northgate.liverpool.gov.uk/planningexploreraa/"

# types of fields that have dates in them
decisionlist = ["Refuse", "Withdrawn", "Approve with Conditions", "Approve without Conditions", "Allowed", "Dismissed", "Prior Approval Given",
                "Split Decision", "Certificate of Lawfulness - Granted", 
                "Final Decision - Dismissed", "Final Decision - Withdrawn", "Conditions Discharged", "No Objections"]
datetypes = ["Date %s" % d  for d in decisionlist ]
datetypes.extend(["Date Registered", "Comments Until", "Appeal Lodged", "Application Registered", "Date Decision"])


cj = cookielib.CookieJar()  # also used by the mechanize.Browser
urllibopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllibopener.addheaders.append (('x-runid', os.environ['RUNID']))

def scrape(url, refererurl):
    try:
        fin = urllibopener.open(url)
        text = fin.read()
        fin.close()
    except:
        log("gone bad " + url)
        return ""
    return text

    #req = urllib2.Request(data["url"])
    #req.add_header('Referer', refererurl)
    #rr = urllib2.urlopen(req)


import time
def log(s):
    time.sleep(0.15)
    print str(s)
    time.sleep(0.2)

def CleanupData(data):
    # convert the location
    if 'Location Co ordinates' in data:
        mcoords = re.match('Easting(\d*)Northing(\d*)$', data['Location Co ordinates'])
        if mcoords.group(1) and mcoords.group(2):  # missing coordinates leave the numbers blank
            seasting = mcoords.group(1)
            snorthing = mcoords.group(2)
            if len(seasting) == 6:
                seasting += "0"
            if len(snorthing) == 6:
                snorthing += "0"
            easting = int(seasting) / 10.0
            northing = int(snorthing) / 10.0
            data["latlng"] = scraperwiki.geo.os_easting_northing_to_latlng(easting, northing)
            data["location"] = "OSEastingNorthing(%f, %f)" % (easting, northing)
        del data['Location Co ordinates']

    # markup dates
    for k in data:
        if k in datetypes:
            mdate = re.match("\s*(\d\d)-(\d\d)-(\d\d\d\d)$", data[k])
            if mdate:
                data[k] = datetime.date(int(mdate.group(3)), int(mdate.group(2)), int(mdate.group(1)))
            else:
                log("Bad date %s %s" % (k, data[k]))

    # separate telephone numbers from case officer
    if "Case Officer / Tel" in data:
        mcaseofficertel = re.match("(.*?)\s*(\d+)$", data["Case Officer / Tel"])
        if mcaseofficertel:
            caseofficer = mcaseofficertel.group(1)
            data["telephone"] = mcaseofficertel.group(2)
        else:
            caseofficer = data["Case Officer / Tel"]
        if caseofficer != data["Planning Officer"]:
            log("Planning/Case %s %s" % (data["Planning Officer"], caseofficer))
        del data["Case Officer / Tel"]
    
    if "Applicant" in data:
        data["Applicant"] = re.sub("&amp;", "&", data["Applicant"])
    if "Agent" in data:
        data["Agent"] = re.sub("&amp;", "&", data["Agent"])

    data["date"] = data["Date Registered"]

    
            
# there are multiple ul lists containing duplicate entries on the
def ParsePlanningDetails(data, text):
    dets = re.search("(?i)<h1>Details Page for Planning Application\xc2\xa0-\xc2\xa0(.*)</h1>", text)
    if not dets:
        log("failed: " + text)
        return
    if data["Application Number"] != dets.group(1):
        log("Application num failure %s %s" % (data["Application Number"], dets.group(1)))
    
    # all relevant lists
    ulists = re.findall("(?si)<ul class=\"list\">(.*?)</ul>", text)
    for ul in ulists[:-1]: # the last list leads to more links

        # all rows in relevant lists
        kv = re.findall("(?s)<li>\s*<div>\s*<span>\s*(.*?)\s*</span>\s*(.*?)\s*</div>\s*</li>", ul)
        #log("= " + str(kv))
        for k, v in kv:
            lv = re.sub("&#xD;|&#xA;|\xc2|\xa0|\r", "", v).strip()
            lv = re.sub("é", "e", lv)
            lv = re.sub("\xbd|\xbf", "?", lv)
            #log("kv %s,%s" % (k, lv))
            lv = unicode(lv, errors="replace")
            
            if k not in data:
                if lv:  # only include if there is an entry here
                    data[k] = lv
            elif data[k] != lv:
                dv = data[k]
                if k in ["Decision", "Appeal Decision"] and data[k] in decisionlist:
                    if len(lv) < len(dv):
                        dv, lv = lv, dv  # sometimes the date is in the index
                    if lv[:len(dv)] == dv:
                        data["Date " + k] = lv[len(data[k])+1:]
                    else:
                        log("FDetails don't match: %s %s %s" % (k, data[k], lv))
                elif re.sub("\s", "", dv) != re.sub("\s", "", lv):
                    log("Details don't match: :%s: :%s: :%s:" % (k, data[k], lv))
            


def CleanCrapFromLink(surl, clen):
    clen = re.sub("&#xD;|&#xA;|\t", "", clen)
    clen = re.sub(" ", "%20", clen)
    clen = re.sub("&amp;", "&", clen)
    return surl + clen

                            
def ParseSearchResultTableRow(surl, headers, cols):
    assert len(headers) == len(cols), cols
    data = dict(zip(headers, cols))
    
    # separate link and application number
    mappl = re.search('(?si)\s*<a class="data_text" href="(StdDetails.aspx?[^\"]*)">([^<]*)</a>', data["Application Number"])
    data["Application Number"] = mappl.group(2)
    data["url"] = CleanCrapFromLink(surl, mappl.group(1))
    
    return data


def ParseSearchResultTable(surl, text):

    # table with results
    mtable = re.search('(?s)<table[^>]*? summary=\"Results of the Search\"[^>]*?(.*?)</table>', text)
    if not mtable:
        if not re.search('No Records Found.', text):
            log("missing No records: " + re.sub("<", "&lt;", text))
        return [ ]

    # rows
    rows = re.findall("(?si)<tr[^>]*>(.*?)</tr>", mtable.group(1))
    headers = re.findall("<th class=\"data_header\">(.*?)</th>", rows[0])
     
    # process each application in table
    results = [ ]
    for row in rows[1:]:
        cols = re.findall("(?si)<td.*?>(.*?)</td>", row)                          
        aproc = ParseSearchResultTableRow(surl, headers, cols)
        results.append(aproc)
    return results
    
                                          
def ScrapePlanningApplications(lastday, daysback):
    firstday = lastday - datetime.timedelta(days=daysback)
    #log("Doing " + str(firstday))
    
    cj.clear()
    br = mechanize.Browser()
    br.addheaders = [ [ 'x-runid', os.environ['RUNID'] ] ]
    
    
    br.set_cookiejar(cj)
    br.open(liverpoolplanningurl)
            
    br.select_form(name="M3Form")

    br["dateStart"] = firstday.strftime("%d/%m/%Y")    
    br["dateEnd"] = lastday.strftime("%d/%m/%Y")
    br["rbGroup"] = ["rbRange"]
    g = br.submit()
    tabletext = g.read()
                  
    surl = re.sub("(?s)StdResults.*$", "", br.geturl())
        
    npages, nrecords = 0, 0
    refererurl = br.geturl()
    
    while True:
        rows = ParseSearchResultTable(surl, tabletext)
        for data in rows:
            #log(nrecords)
            ParsePlanningDetails(data, scrape(data["url"], refererurl))
            CleanupData(data)
            #log("-  " + str(data))
            scraperwiki.datastore.save(unique_keys=["Application Number"], data=data)
            nrecords += 1
        
        mnextlink = re.search('(?s)<a class="noborder" href="(StdResults.aspx[^"]*?)"><img src="/PlanningExplorerAA/SiteFiles/Skins/Default_AA/Images/arrowr.gif" alt="Go to next page "', tabletext)
        if not mnextlink:
            break
        
        nexturl = CleanCrapFromLink(surl, mnextlink.group(1))            
        npages += 1
        log("Page %d %s" % (npages, nexturl))
        
        tabletext = scrape(nexturl, refererurl)
        #log(re.sub("<", "&lt;", tabletext))
        refererurl = nexturl
        #break
    return nrecords, npages



# iterate through day by day
day = datetime.date.today()
# all of 2008-2006 done 
# 
#day = datetime.date(2005, 7, 6)  # run back to 7/17
for i in range(30):
    sday = day.strftime("%d/%m/%Y")
    pday = None # scraperwiki.page_cache.getpagebyname(sday)
    if not pday:
        nrecords, npages = ScrapePlanningApplications(day, 0)
        pday =  "%d %d" % (nrecords, npages)
        log("Scraped %d from %s" % (nrecords, sday))
        #scraperwiki.page_cache.savepage("dayrec", sday, pday)
    else:
        log("skipping %s %s" % (sday, pday))
    day = day - datetime.timedelta(days=1)

        



import scraperwiki
import mechanize
import datetime
import re
import urllib2
import cookielib
import os

# http://hpzworkstations.com/
# Very involved Liverpool planning scraper attempting to get all fields out of their database, which goes back to 1996
# Searches for all applications on a single day, and handles the pagination of the list of applications which requires cookies to execute
# mechanize is unable to follow the links itself because the href values are stuffed with linefeeds, &#0D strings and control characters (see CleanCrapFromLink())

liverpoolplanningurl = "http://northgate.liverpool.gov.uk/planningexploreraa/"

# types of fields that have dates in them
decisionlist = ["Refuse", "Withdrawn", "Approve with Conditions", "Approve without Conditions", "Allowed", "Dismissed", "Prior Approval Given",
                "Split Decision", "Certificate of Lawfulness - Granted", 
                "Final Decision - Dismissed", "Final Decision - Withdrawn", "Conditions Discharged", "No Objections"]
datetypes = ["Date %s" % d  for d in decisionlist ]
datetypes.extend(["Date Registered", "Comments Until", "Appeal Lodged", "Application Registered", "Date Decision"])


cj = cookielib.CookieJar()  # also used by the mechanize.Browser
urllibopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllibopener.addheaders.append (('x-runid', os.environ['RUNID']))

def scrape(url, refererurl):
    try:
        fin = urllibopener.open(url)
        text = fin.read()
        fin.close()
    except:
        log("gone bad " + url)
        return ""
    return text

    #req = urllib2.Request(data["url"])
    #req.add_header('Referer', refererurl)
    #rr = urllib2.urlopen(req)


import time
def log(s):
    time.sleep(0.15)
    print str(s)
    time.sleep(0.2)

def CleanupData(data):
    # convert the location
    if 'Location Co ordinates' in data:
        mcoords = re.match('Easting(\d*)Northing(\d*)$', data['Location Co ordinates'])
        if mcoords.group(1) and mcoords.group(2):  # missing coordinates leave the numbers blank
            seasting = mcoords.group(1)
            snorthing = mcoords.group(2)
            if len(seasting) == 6:
                seasting += "0"
            if len(snorthing) == 6:
                snorthing += "0"
            easting = int(seasting) / 10.0
            northing = int(snorthing) / 10.0
            data["latlng"] = scraperwiki.geo.os_easting_northing_to_latlng(easting, northing)
            data["location"] = "OSEastingNorthing(%f, %f)" % (easting, northing)
        del data['Location Co ordinates']

    # markup dates
    for k in data:
        if k in datetypes:
            mdate = re.match("\s*(\d\d)-(\d\d)-(\d\d\d\d)$", data[k])
            if mdate:
                data[k] = datetime.date(int(mdate.group(3)), int(mdate.group(2)), int(mdate.group(1)))
            else:
                log("Bad date %s %s" % (k, data[k]))

    # separate telephone numbers from case officer
    if "Case Officer / Tel" in data:
        mcaseofficertel = re.match("(.*?)\s*(\d+)$", data["Case Officer / Tel"])
        if mcaseofficertel:
            caseofficer = mcaseofficertel.group(1)
            data["telephone"] = mcaseofficertel.group(2)
        else:
            caseofficer = data["Case Officer / Tel"]
        if caseofficer != data["Planning Officer"]:
            log("Planning/Case %s %s" % (data["Planning Officer"], caseofficer))
        del data["Case Officer / Tel"]
    
    if "Applicant" in data:
        data["Applicant"] = re.sub("&amp;", "&", data["Applicant"])
    if "Agent" in data:
        data["Agent"] = re.sub("&amp;", "&", data["Agent"])

    data["date"] = data["Date Registered"]

    
            
# there are multiple ul lists containing duplicate entries on the
def ParsePlanningDetails(data, text):
    dets = re.search("(?i)<h1>Details Page for Planning Application\xc2\xa0-\xc2\xa0(.*)</h1>", text)
    if not dets:
        log("failed: " + text)
        return
    if data["Application Number"] != dets.group(1):
        log("Application num failure %s %s" % (data["Application Number"], dets.group(1)))
    
    # all relevant lists
    ulists = re.findall("(?si)<ul class=\"list\">(.*?)</ul>", text)
    for ul in ulists[:-1]: # the last list leads to more links

        # all rows in relevant lists
        kv = re.findall("(?s)<li>\s*<div>\s*<span>\s*(.*?)\s*</span>\s*(.*?)\s*</div>\s*</li>", ul)
        #log("= " + str(kv))
        for k, v in kv:
            lv = re.sub("&#xD;|&#xA;|\xc2|\xa0|\r", "", v).strip()
            lv = re.sub("é", "e", lv)
            lv = re.sub("\xbd|\xbf", "?", lv)
            #log("kv %s,%s" % (k, lv))
            lv = unicode(lv, errors="replace")
            
            if k not in data:
                if lv:  # only include if there is an entry here
                    data[k] = lv
            elif data[k] != lv:
                dv = data[k]
                if k in ["Decision", "Appeal Decision"] and data[k] in decisionlist:
                    if len(lv) < len(dv):
                        dv, lv = lv, dv  # sometimes the date is in the index
                    if lv[:len(dv)] == dv:
                        data["Date " + k] = lv[len(data[k])+1:]
                    else:
                        log("FDetails don't match: %s %s %s" % (k, data[k], lv))
                elif re.sub("\s", "", dv) != re.sub("\s", "", lv):
                    log("Details don't match: :%s: :%s: :%s:" % (k, data[k], lv))
            


def CleanCrapFromLink(surl, clen):
    clen = re.sub("&#xD;|&#xA;|\t", "", clen)
    clen = re.sub(" ", "%20", clen)
    clen = re.sub("&amp;", "&", clen)
    return surl + clen

                            
def ParseSearchResultTableRow(surl, headers, cols):
    assert len(headers) == len(cols), cols
    data = dict(zip(headers, cols))
    
    # separate link and application number
    mappl = re.search('(?si)\s*<a class="data_text" href="(StdDetails.aspx?[^\"]*)">([^<]*)</a>', data["Application Number"])
    data["Application Number"] = mappl.group(2)
    data["url"] = CleanCrapFromLink(surl, mappl.group(1))
    
    return data


def ParseSearchResultTable(surl, text):

    # table with results
    mtable = re.search('(?s)<table[^>]*? summary=\"Results of the Search\"[^>]*?(.*?)</table>', text)
    if not mtable:
        if not re.search('No Records Found.', text):
            log("missing No records: " + re.sub("<", "&lt;", text))
        return [ ]

    # rows
    rows = re.findall("(?si)<tr[^>]*>(.*?)</tr>", mtable.group(1))
    headers = re.findall("<th class=\"data_header\">(.*?)</th>", rows[0])
     
    # process each application in table
    results = [ ]
    for row in rows[1:]:
        cols = re.findall("(?si)<td.*?>(.*?)</td>", row)                          
        aproc = ParseSearchResultTableRow(surl, headers, cols)
        results.append(aproc)
    return results
    
                                          
def ScrapePlanningApplications(lastday, daysback):
    firstday = lastday - datetime.timedelta(days=daysback)
    #log("Doing " + str(firstday))
    
    cj.clear()
    br = mechanize.Browser()
    br.addheaders = [ [ 'x-runid', os.environ['RUNID'] ] ]
    
    
    br.set_cookiejar(cj)
    br.open(liverpoolplanningurl)
            
    br.select_form(name="M3Form")

    br["dateStart"] = firstday.strftime("%d/%m/%Y")    
    br["dateEnd"] = lastday.strftime("%d/%m/%Y")
    br["rbGroup"] = ["rbRange"]
    g = br.submit()
    tabletext = g.read()
                  
    surl = re.sub("(?s)StdResults.*$", "", br.geturl())
        
    npages, nrecords = 0, 0
    refererurl = br.geturl()
    
    while True:
        rows = ParseSearchResultTable(surl, tabletext)
        for data in rows:
            #log(nrecords)
            ParsePlanningDetails(data, scrape(data["url"], refererurl))
            CleanupData(data)
            #log("-  " + str(data))
            scraperwiki.datastore.save(unique_keys=["Application Number"], data=data)
            nrecords += 1
        
        mnextlink = re.search('(?s)<a class="noborder" href="(StdResults.aspx[^"]*?)"><img src="/PlanningExplorerAA/SiteFiles/Skins/Default_AA/Images/arrowr.gif" alt="Go to next page "', tabletext)
        if not mnextlink:
            break
        
        nexturl = CleanCrapFromLink(surl, mnextlink.group(1))            
        npages += 1
        log("Page %d %s" % (npages, nexturl))
        
        tabletext = scrape(nexturl, refererurl)
        #log(re.sub("<", "&lt;", tabletext))
        refererurl = nexturl
        #break
    return nrecords, npages



# iterate through day by day
day = datetime.date.today()
# all of 2008-2006 done 
# 
#day = datetime.date(2005, 7, 6)  # run back to 7/17
for i in range(30):
    sday = day.strftime("%d/%m/%Y")
    pday = None # scraperwiki.page_cache.getpagebyname(sday)
    if not pday:
        nrecords, npages = ScrapePlanningApplications(day, 0)
        pday =  "%d %d" % (nrecords, npages)
        log("Scraped %d from %s" % (nrecords, sday))
        #scraperwiki.page_cache.savepage("dayrec", sday, pday)
    else:
        log("skipping %s %s" % (sday, pday))
    day = day - datetime.timedelta(days=1)

        



import scraperwiki
import mechanize
import datetime
import re
import urllib2
import cookielib
import os

# http://hpzworkstations.com/
# Very involved Liverpool planning scraper attempting to get all fields out of their database, which goes back to 1996
# Searches for all applications on a single day, and handles the pagination of the list of applications which requires cookies to execute
# mechanize is unable to follow the links itself because the href values are stuffed with linefeeds, &#0D strings and control characters (see CleanCrapFromLink())

liverpoolplanningurl = "http://northgate.liverpool.gov.uk/planningexploreraa/"

# types of fields that have dates in them
decisionlist = ["Refuse", "Withdrawn", "Approve with Conditions", "Approve without Conditions", "Allowed", "Dismissed", "Prior Approval Given",
                "Split Decision", "Certificate of Lawfulness - Granted", 
                "Final Decision - Dismissed", "Final Decision - Withdrawn", "Conditions Discharged", "No Objections"]
datetypes = ["Date %s" % d  for d in decisionlist ]
datetypes.extend(["Date Registered", "Comments Until", "Appeal Lodged", "Application Registered", "Date Decision"])


cj = cookielib.CookieJar()  # also used by the mechanize.Browser
urllibopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllibopener.addheaders.append (('x-runid', os.environ['RUNID']))

def scrape(url, refererurl):
    try:
        fin = urllibopener.open(url)
        text = fin.read()
        fin.close()
    except:
        log("gone bad " + url)
        return ""
    return text

    #req = urllib2.Request(data["url"])
    #req.add_header('Referer', refererurl)
    #rr = urllib2.urlopen(req)


import time
def log(s):
    time.sleep(0.15)
    print str(s)
    time.sleep(0.2)

def CleanupData(data):
    # convert the location
    if 'Location Co ordinates' in data:
        mcoords = re.match('Easting(\d*)Northing(\d*)$', data['Location Co ordinates'])
        if mcoords.group(1) and mcoords.group(2):  # missing coordinates leave the numbers blank
            seasting = mcoords.group(1)
            snorthing = mcoords.group(2)
            if len(seasting) == 6:
                seasting += "0"
            if len(snorthing) == 6:
                snorthing += "0"
            easting = int(seasting) / 10.0
            northing = int(snorthing) / 10.0
            data["latlng"] = scraperwiki.geo.os_easting_northing_to_latlng(easting, northing)
            data["location"] = "OSEastingNorthing(%f, %f)" % (easting, northing)
        del data['Location Co ordinates']

    # markup dates
    for k in data:
        if k in datetypes:
            mdate = re.match("\s*(\d\d)-(\d\d)-(\d\d\d\d)$", data[k])
            if mdate:
                data[k] = datetime.date(int(mdate.group(3)), int(mdate.group(2)), int(mdate.group(1)))
            else:
                log("Bad date %s %s" % (k, data[k]))

    # separate telephone numbers from case officer
    if "Case Officer / Tel" in data:
        mcaseofficertel = re.match("(.*?)\s*(\d+)$", data["Case Officer / Tel"])
        if mcaseofficertel:
            caseofficer = mcaseofficertel.group(1)
            data["telephone"] = mcaseofficertel.group(2)
        else:
            caseofficer = data["Case Officer / Tel"]
        if caseofficer != data["Planning Officer"]:
            log("Planning/Case %s %s" % (data["Planning Officer"], caseofficer))
        del data["Case Officer / Tel"]
    
    if "Applicant" in data:
        data["Applicant"] = re.sub("&amp;", "&", data["Applicant"])
    if "Agent" in data:
        data["Agent"] = re.sub("&amp;", "&", data["Agent"])

    data["date"] = data["Date Registered"]

    
            
# there are multiple ul lists containing duplicate entries on the
def ParsePlanningDetails(data, text):
    dets = re.search("(?i)<h1>Details Page for Planning Application\xc2\xa0-\xc2\xa0(.*)</h1>", text)
    if not dets:
        log("failed: " + text)
        return
    if data["Application Number"] != dets.group(1):
        log("Application num failure %s %s" % (data["Application Number"], dets.group(1)))
    
    # all relevant lists
    ulists = re.findall("(?si)<ul class=\"list\">(.*?)</ul>", text)
    for ul in ulists[:-1]: # the last list leads to more links

        # all rows in relevant lists
        kv = re.findall("(?s)<li>\s*<div>\s*<span>\s*(.*?)\s*</span>\s*(.*?)\s*</div>\s*</li>", ul)
        #log("= " + str(kv))
        for k, v in kv:
            lv = re.sub("&#xD;|&#xA;|\xc2|\xa0|\r", "", v).strip()
            lv = re.sub("é", "e", lv)
            lv = re.sub("\xbd|\xbf", "?", lv)
            #log("kv %s,%s" % (k, lv))
            lv = unicode(lv, errors="replace")
            
            if k not in data:
                if lv:  # only include if there is an entry here
                    data[k] = lv
            elif data[k] != lv:
                dv = data[k]
                if k in ["Decision", "Appeal Decision"] and data[k] in decisionlist:
                    if len(lv) < len(dv):
                        dv, lv = lv, dv  # sometimes the date is in the index
                    if lv[:len(dv)] == dv:
                        data["Date " + k] = lv[len(data[k])+1:]
                    else:
                        log("FDetails don't match: %s %s %s" % (k, data[k], lv))
                elif re.sub("\s", "", dv) != re.sub("\s", "", lv):
                    log("Details don't match: :%s: :%s: :%s:" % (k, data[k], lv))
            


def CleanCrapFromLink(surl, clen):
    clen = re.sub("&#xD;|&#xA;|\t", "", clen)
    clen = re.sub(" ", "%20", clen)
    clen = re.sub("&amp;", "&", clen)
    return surl + clen

                            
def ParseSearchResultTableRow(surl, headers, cols):
    assert len(headers) == len(cols), cols
    data = dict(zip(headers, cols))
    
    # separate link and application number
    mappl = re.search('(?si)\s*<a class="data_text" href="(StdDetails.aspx?[^\"]*)">([^<]*)</a>', data["Application Number"])
    data["Application Number"] = mappl.group(2)
    data["url"] = CleanCrapFromLink(surl, mappl.group(1))
    
    return data


def ParseSearchResultTable(surl, text):

    # table with results
    mtable = re.search('(?s)<table[^>]*? summary=\"Results of the Search\"[^>]*?(.*?)</table>', text)
    if not mtable:
        if not re.search('No Records Found.', text):
            log("missing No records: " + re.sub("<", "&lt;", text))
        return [ ]

    # rows
    rows = re.findall("(?si)<tr[^>]*>(.*?)</tr>", mtable.group(1))
    headers = re.findall("<th class=\"data_header\">(.*?)</th>", rows[0])
     
    # process each application in table
    results = [ ]
    for row in rows[1:]:
        cols = re.findall("(?si)<td.*?>(.*?)</td>", row)                          
        aproc = ParseSearchResultTableRow(surl, headers, cols)
        results.append(aproc)
    return results
    
                                          
def ScrapePlanningApplications(lastday, daysback):
    firstday = lastday - datetime.timedelta(days=daysback)
    #log("Doing " + str(firstday))
    
    cj.clear()
    br = mechanize.Browser()
    br.addheaders = [ [ 'x-runid', os.environ['RUNID'] ] ]
    
    
    br.set_cookiejar(cj)
    br.open(liverpoolplanningurl)
            
    br.select_form(name="M3Form")

    br["dateStart"] = firstday.strftime("%d/%m/%Y")    
    br["dateEnd"] = lastday.strftime("%d/%m/%Y")
    br["rbGroup"] = ["rbRange"]
    g = br.submit()
    tabletext = g.read()
                  
    surl = re.sub("(?s)StdResults.*$", "", br.geturl())
        
    npages, nrecords = 0, 0
    refererurl = br.geturl()
    
    while True:
        rows = ParseSearchResultTable(surl, tabletext)
        for data in rows:
            #log(nrecords)
            ParsePlanningDetails(data, scrape(data["url"], refererurl))
            CleanupData(data)
            #log("-  " + str(data))
            scraperwiki.datastore.save(unique_keys=["Application Number"], data=data)
            nrecords += 1
        
        mnextlink = re.search('(?s)<a class="noborder" href="(StdResults.aspx[^"]*?)"><img src="/PlanningExplorerAA/SiteFiles/Skins/Default_AA/Images/arrowr.gif" alt="Go to next page "', tabletext)
        if not mnextlink:
            break
        
        nexturl = CleanCrapFromLink(surl, mnextlink.group(1))            
        npages += 1
        log("Page %d %s" % (npages, nexturl))
        
        tabletext = scrape(nexturl, refererurl)
        #log(re.sub("<", "&lt;", tabletext))
        refererurl = nexturl
        #break
    return nrecords, npages



# iterate through day by day
day = datetime.date.today()
# all of 2008-2006 done 
# 
#day = datetime.date(2005, 7, 6)  # run back to 7/17
for i in range(30):
    sday = day.strftime("%d/%m/%Y")
    pday = None # scraperwiki.page_cache.getpagebyname(sday)
    if not pday:
        nrecords, npages = ScrapePlanningApplications(day, 0)
        pday =  "%d %d" % (nrecords, npages)
        log("Scraped %d from %s" % (nrecords, sday))
        #scraperwiki.page_cache.savepage("dayrec", sday, pday)
    else:
        log("skipping %s %s" % (sday, pday))
    day = day - datetime.timedelta(days=1)

        



import scraperwiki
import mechanize
import datetime
import re
import urllib2
import cookielib
import os

# http://hpzworkstations.com/
# Very involved Liverpool planning scraper attempting to get all fields out of their database, which goes back to 1996
# Searches for all applications on a single day, and handles the pagination of the list of applications which requires cookies to execute
# mechanize is unable to follow the links itself because the href values are stuffed with linefeeds, &#0D strings and control characters (see CleanCrapFromLink())

liverpoolplanningurl = "http://northgate.liverpool.gov.uk/planningexploreraa/"

# types of fields that have dates in them
decisionlist = ["Refuse", "Withdrawn", "Approve with Conditions", "Approve without Conditions", "Allowed", "Dismissed", "Prior Approval Given",
                "Split Decision", "Certificate of Lawfulness - Granted", 
                "Final Decision - Dismissed", "Final Decision - Withdrawn", "Conditions Discharged", "No Objections"]
datetypes = ["Date %s" % d  for d in decisionlist ]
datetypes.extend(["Date Registered", "Comments Until", "Appeal Lodged", "Application Registered", "Date Decision"])


cj = cookielib.CookieJar()  # also used by the mechanize.Browser
urllibopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllibopener.addheaders.append (('x-runid', os.environ['RUNID']))

def scrape(url, refererurl):
    try:
        fin = urllibopener.open(url)
        text = fin.read()
        fin.close()
    except:
        log("gone bad " + url)
        return ""
    return text

    #req = urllib2.Request(data["url"])
    #req.add_header('Referer', refererurl)
    #rr = urllib2.urlopen(req)


import time
def log(s):
    time.sleep(0.15)
    print str(s)
    time.sleep(0.2)

def CleanupData(data):
    # convert the location
    if 'Location Co ordinates' in data:
        mcoords = re.match('Easting(\d*)Northing(\d*)$', data['Location Co ordinates'])
        if mcoords.group(1) and mcoords.group(2):  # missing coordinates leave the numbers blank
            seasting = mcoords.group(1)
            snorthing = mcoords.group(2)
            if len(seasting) == 6:
                seasting += "0"
            if len(snorthing) == 6:
                snorthing += "0"
            easting = int(seasting) / 10.0
            northing = int(snorthing) / 10.0
            data["latlng"] = scraperwiki.geo.os_easting_northing_to_latlng(easting, northing)
            data["location"] = "OSEastingNorthing(%f, %f)" % (easting, northing)
        del data['Location Co ordinates']

    # markup dates
    for k in data:
        if k in datetypes:
            mdate = re.match("\s*(\d\d)-(\d\d)-(\d\d\d\d)$", data[k])
            if mdate:
                data[k] = datetime.date(int(mdate.group(3)), int(mdate.group(2)), int(mdate.group(1)))
            else:
                log("Bad date %s %s" % (k, data[k]))

    # separate telephone numbers from case officer
    if "Case Officer / Tel" in data:
        mcaseofficertel = re.match("(.*?)\s*(\d+)$", data["Case Officer / Tel"])
        if mcaseofficertel:
            caseofficer = mcaseofficertel.group(1)
            data["telephone"] = mcaseofficertel.group(2)
        else:
            caseofficer = data["Case Officer / Tel"]
        if caseofficer != data["Planning Officer"]:
            log("Planning/Case %s %s" % (data["Planning Officer"], caseofficer))
        del data["Case Officer / Tel"]
    
    if "Applicant" in data:
        data["Applicant"] = re.sub("&amp;", "&", data["Applicant"])
    if "Agent" in data:
        data["Agent"] = re.sub("&amp;", "&", data["Agent"])

    data["date"] = data["Date Registered"]

    
            
# there are multiple ul lists containing duplicate entries on the
def ParsePlanningDetails(data, text):
    dets = re.search("(?i)<h1>Details Page for Planning Application\xc2\xa0-\xc2\xa0(.*)</h1>", text)
    if not dets:
        log("failed: " + text)
        return
    if data["Application Number"] != dets.group(1):
        log("Application num failure %s %s" % (data["Application Number"], dets.group(1)))
    
    # all relevant lists
    ulists = re.findall("(?si)<ul class=\"list\">(.*?)</ul>", text)
    for ul in ulists[:-1]: # the last list leads to more links

        # all rows in relevant lists
        kv = re.findall("(?s)<li>\s*<div>\s*<span>\s*(.*?)\s*</span>\s*(.*?)\s*</div>\s*</li>", ul)
        #log("= " + str(kv))
        for k, v in kv:
            lv = re.sub("&#xD;|&#xA;|\xc2|\xa0|\r", "", v).strip()
            lv = re.sub("é", "e", lv)
            lv = re.sub("\xbd|\xbf", "?", lv)
            #log("kv %s,%s" % (k, lv))
            lv = unicode(lv, errors="replace")
            
            if k not in data:
                if lv:  # only include if there is an entry here
                    data[k] = lv
            elif data[k] != lv:
                dv = data[k]
                if k in ["Decision", "Appeal Decision"] and data[k] in decisionlist:
                    if len(lv) < len(dv):
                        dv, lv = lv, dv  # sometimes the date is in the index
                    if lv[:len(dv)] == dv:
                        data["Date " + k] = lv[len(data[k])+1:]
                    else:
                        log("FDetails don't match: %s %s %s" % (k, data[k], lv))
                elif re.sub("\s", "", dv) != re.sub("\s", "", lv):
                    log("Details don't match: :%s: :%s: :%s:" % (k, data[k], lv))
            


def CleanCrapFromLink(surl, clen):
    clen = re.sub("&#xD;|&#xA;|\t", "", clen)
    clen = re.sub(" ", "%20", clen)
    clen = re.sub("&amp;", "&", clen)
    return surl + clen

                            
def ParseSearchResultTableRow(surl, headers, cols):
    assert len(headers) == len(cols), cols
    data = dict(zip(headers, cols))
    
    # separate link and application number
    mappl = re.search('(?si)\s*<a class="data_text" href="(StdDetails.aspx?[^\"]*)">([^<]*)</a>', data["Application Number"])
    data["Application Number"] = mappl.group(2)
    data["url"] = CleanCrapFromLink(surl, mappl.group(1))
    
    return data


def ParseSearchResultTable(surl, text):

    # table with results
    mtable = re.search('(?s)<table[^>]*? summary=\"Results of the Search\"[^>]*?(.*?)</table>', text)
    if not mtable:
        if not re.search('No Records Found.', text):
            log("missing No records: " + re.sub("<", "&lt;", text))
        return [ ]

    # rows
    rows = re.findall("(?si)<tr[^>]*>(.*?)</tr>", mtable.group(1))
    headers = re.findall("<th class=\"data_header\">(.*?)</th>", rows[0])
     
    # process each application in table
    results = [ ]
    for row in rows[1:]:
        cols = re.findall("(?si)<td.*?>(.*?)</td>", row)                          
        aproc = ParseSearchResultTableRow(surl, headers, cols)
        results.append(aproc)
    return results
    
                                          
def ScrapePlanningApplications(lastday, daysback):
    firstday = lastday - datetime.timedelta(days=daysback)
    #log("Doing " + str(firstday))
    
    cj.clear()
    br = mechanize.Browser()
    br.addheaders = [ [ 'x-runid', os.environ['RUNID'] ] ]
    
    
    br.set_cookiejar(cj)
    br.open(liverpoolplanningurl)
            
    br.select_form(name="M3Form")

    br["dateStart"] = firstday.strftime("%d/%m/%Y")    
    br["dateEnd"] = lastday.strftime("%d/%m/%Y")
    br["rbGroup"] = ["rbRange"]
    g = br.submit()
    tabletext = g.read()
                  
    surl = re.sub("(?s)StdResults.*$", "", br.geturl())
        
    npages, nrecords = 0, 0
    refererurl = br.geturl()
    
    while True:
        rows = ParseSearchResultTable(surl, tabletext)
        for data in rows:
            #log(nrecords)
            ParsePlanningDetails(data, scrape(data["url"], refererurl))
            CleanupData(data)
            #log("-  " + str(data))
            scraperwiki.datastore.save(unique_keys=["Application Number"], data=data)
            nrecords += 1
        
        mnextlink = re.search('(?s)<a class="noborder" href="(StdResults.aspx[^"]*?)"><img src="/PlanningExplorerAA/SiteFiles/Skins/Default_AA/Images/arrowr.gif" alt="Go to next page "', tabletext)
        if not mnextlink:
            break
        
        nexturl = CleanCrapFromLink(surl, mnextlink.group(1))            
        npages += 1
        log("Page %d %s" % (npages, nexturl))
        
        tabletext = scrape(nexturl, refererurl)
        #log(re.sub("<", "&lt;", tabletext))
        refererurl = nexturl
        #break
    return nrecords, npages



# iterate through day by day
day = datetime.date.today()
# all of 2008-2006 done 
# 
#day = datetime.date(2005, 7, 6)  # run back to 7/17
for i in range(30):
    sday = day.strftime("%d/%m/%Y")
    pday = None # scraperwiki.page_cache.getpagebyname(sday)
    if not pday:
        nrecords, npages = ScrapePlanningApplications(day, 0)
        pday =  "%d %d" % (nrecords, npages)
        log("Scraped %d from %s" % (nrecords, sday))
        #scraperwiki.page_cache.savepage("dayrec", sday, pday)
    else:
        log("skipping %s %s" % (sday, pday))
    day = day - datetime.timedelta(days=1)

        



import scraperwiki
import mechanize
import datetime
import re
import urllib2
import cookielib
import os

# http://hpzworkstations.com/
# Very involved Liverpool planning scraper attempting to get all fields out of their database, which goes back to 1996
# Searches for all applications on a single day, and handles the pagination of the list of applications which requires cookies to execute
# mechanize is unable to follow the links itself because the href values are stuffed with linefeeds, &#0D strings and control characters (see CleanCrapFromLink())

liverpoolplanningurl = "http://northgate.liverpool.gov.uk/planningexploreraa/"

# types of fields that have dates in them
decisionlist = ["Refuse", "Withdrawn", "Approve with Conditions", "Approve without Conditions", "Allowed", "Dismissed", "Prior Approval Given",
                "Split Decision", "Certificate of Lawfulness - Granted", 
                "Final Decision - Dismissed", "Final Decision - Withdrawn", "Conditions Discharged", "No Objections"]
datetypes = ["Date %s" % d  for d in decisionlist ]
datetypes.extend(["Date Registered", "Comments Until", "Appeal Lodged", "Application Registered", "Date Decision"])


cj = cookielib.CookieJar()  # also used by the mechanize.Browser
urllibopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllibopener.addheaders.append (('x-runid', os.environ['RUNID']))

def scrape(url, refererurl):
    try:
        fin = urllibopener.open(url)
        text = fin.read()
        fin.close()
    except:
        log("gone bad " + url)
        return ""
    return text

    #req = urllib2.Request(data["url"])
    #req.add_header('Referer', refererurl)
    #rr = urllib2.urlopen(req)


import time
def log(s):
    time.sleep(0.15)
    print str(s)
    time.sleep(0.2)

def CleanupData(data):
    # convert the location
    if 'Location Co ordinates' in data:
        mcoords = re.match('Easting(\d*)Northing(\d*)$', data['Location Co ordinates'])
        if mcoords.group(1) and mcoords.group(2):  # missing coordinates leave the numbers blank
            seasting = mcoords.group(1)
            snorthing = mcoords.group(2)
            if len(seasting) == 6:
                seasting += "0"
            if len(snorthing) == 6:
                snorthing += "0"
            easting = int(seasting) / 10.0
            northing = int(snorthing) / 10.0
            data["latlng"] = scraperwiki.geo.os_easting_northing_to_latlng(easting, northing)
            data["location"] = "OSEastingNorthing(%f, %f)" % (easting, northing)
        del data['Location Co ordinates']

    # markup dates
    for k in data:
        if k in datetypes:
            mdate = re.match("\s*(\d\d)-(\d\d)-(\d\d\d\d)$", data[k])
            if mdate:
                data[k] = datetime.date(int(mdate.group(3)), int(mdate.group(2)), int(mdate.group(1)))
            else:
                log("Bad date %s %s" % (k, data[k]))

    # separate telephone numbers from case officer
    if "Case Officer / Tel" in data:
        mcaseofficertel = re.match("(.*?)\s*(\d+)$", data["Case Officer / Tel"])
        if mcaseofficertel:
            caseofficer = mcaseofficertel.group(1)
            data["telephone"] = mcaseofficertel.group(2)
        else:
            caseofficer = data["Case Officer / Tel"]
        if caseofficer != data["Planning Officer"]:
            log("Planning/Case %s %s" % (data["Planning Officer"], caseofficer))
        del data["Case Officer / Tel"]
    
    if "Applicant" in data:
        data["Applicant"] = re.sub("&amp;", "&", data["Applicant"])
    if "Agent" in data:
        data["Agent"] = re.sub("&amp;", "&", data["Agent"])

    data["date"] = data["Date Registered"]

    
            
# there are multiple ul lists containing duplicate entries on the
def ParsePlanningDetails(data, text):
    dets = re.search("(?i)<h1>Details Page for Planning Application\xc2\xa0-\xc2\xa0(.*)</h1>", text)
    if not dets:
        log("failed: " + text)
        return
    if data["Application Number"] != dets.group(1):
        log("Application num failure %s %s" % (data["Application Number"], dets.group(1)))
    
    # all relevant lists
    ulists = re.findall("(?si)<ul class=\"list\">(.*?)</ul>", text)
    for ul in ulists[:-1]: # the last list leads to more links

        # all rows in relevant lists
        kv = re.findall("(?s)<li>\s*<div>\s*<span>\s*(.*?)\s*</span>\s*(.*?)\s*</div>\s*</li>", ul)
        #log("= " + str(kv))
        for k, v in kv:
            lv = re.sub("&#xD;|&#xA;|\xc2|\xa0|\r", "", v).strip()
            lv = re.sub("é", "e", lv)
            lv = re.sub("\xbd|\xbf", "?", lv)
            #log("kv %s,%s" % (k, lv))
            lv = unicode(lv, errors="replace")
            
            if k not in data:
                if lv:  # only include if there is an entry here
                    data[k] = lv
            elif data[k] != lv:
                dv = data[k]
                if k in ["Decision", "Appeal Decision"] and data[k] in decisionlist:
                    if len(lv) < len(dv):
                        dv, lv = lv, dv  # sometimes the date is in the index
                    if lv[:len(dv)] == dv:
                        data["Date " + k] = lv[len(data[k])+1:]
                    else:
                        log("FDetails don't match: %s %s %s" % (k, data[k], lv))
                elif re.sub("\s", "", dv) != re.sub("\s", "", lv):
                    log("Details don't match: :%s: :%s: :%s:" % (k, data[k], lv))
            


def CleanCrapFromLink(surl, clen):
    clen = re.sub("&#xD;|&#xA;|\t", "", clen)
    clen = re.sub(" ", "%20", clen)
    clen = re.sub("&amp;", "&", clen)
    return surl + clen

                            
def ParseSearchResultTableRow(surl, headers, cols):
    assert len(headers) == len(cols), cols
    data = dict(zip(headers, cols))
    
    # separate link and application number
    mappl = re.search('(?si)\s*<a class="data_text" href="(StdDetails.aspx?[^\"]*)">([^<]*)</a>', data["Application Number"])
    data["Application Number"] = mappl.group(2)
    data["url"] = CleanCrapFromLink(surl, mappl.group(1))
    
    return data


def ParseSearchResultTable(surl, text):

    # table with results
    mtable = re.search('(?s)<table[^>]*? summary=\"Results of the Search\"[^>]*?(.*?)</table>', text)
    if not mtable:
        if not re.search('No Records Found.', text):
            log("missing No records: " + re.sub("<", "&lt;", text))
        return [ ]

    # rows
    rows = re.findall("(?si)<tr[^>]*>(.*?)</tr>", mtable.group(1))
    headers = re.findall("<th class=\"data_header\">(.*?)</th>", rows[0])
     
    # process each application in table
    results = [ ]
    for row in rows[1:]:
        cols = re.findall("(?si)<td.*?>(.*?)</td>", row)                          
        aproc = ParseSearchResultTableRow(surl, headers, cols)
        results.append(aproc)
    return results
    
                                          
def ScrapePlanningApplications(lastday, daysback):
    firstday = lastday - datetime.timedelta(days=daysback)
    #log("Doing " + str(firstday))
    
    cj.clear()
    br = mechanize.Browser()
    br.addheaders = [ [ 'x-runid', os.environ['RUNID'] ] ]
    
    
    br.set_cookiejar(cj)
    br.open(liverpoolplanningurl)
            
    br.select_form(name="M3Form")

    br["dateStart"] = firstday.strftime("%d/%m/%Y")    
    br["dateEnd"] = lastday.strftime("%d/%m/%Y")
    br["rbGroup"] = ["rbRange"]
    g = br.submit()
    tabletext = g.read()
                  
    surl = re.sub("(?s)StdResults.*$", "", br.geturl())
        
    npages, nrecords = 0, 0
    refererurl = br.geturl()
    
    while True:
        rows = ParseSearchResultTable(surl, tabletext)
        for data in rows:
            #log(nrecords)
            ParsePlanningDetails(data, scrape(data["url"], refererurl))
            CleanupData(data)
            #log("-  " + str(data))
            scraperwiki.datastore.save(unique_keys=["Application Number"], data=data)
            nrecords += 1
        
        mnextlink = re.search('(?s)<a class="noborder" href="(StdResults.aspx[^"]*?)"><img src="/PlanningExplorerAA/SiteFiles/Skins/Default_AA/Images/arrowr.gif" alt="Go to next page "', tabletext)
        if not mnextlink:
            break
        
        nexturl = CleanCrapFromLink(surl, mnextlink.group(1))            
        npages += 1
        log("Page %d %s" % (npages, nexturl))
        
        tabletext = scrape(nexturl, refererurl)
        #log(re.sub("<", "&lt;", tabletext))
        refererurl = nexturl
        #break
    return nrecords, npages



# iterate through day by day
day = datetime.date.today()
# all of 2008-2006 done 
# 
#day = datetime.date(2005, 7, 6)  # run back to 7/17
for i in range(30):
    sday = day.strftime("%d/%m/%Y")
    pday = None # scraperwiki.page_cache.getpagebyname(sday)
    if not pday:
        nrecords, npages = ScrapePlanningApplications(day, 0)
        pday =  "%d %d" % (nrecords, npages)
        log("Scraped %d from %s" % (nrecords, sday))
        #scraperwiki.page_cache.savepage("dayrec", sday, pday)
    else:
        log("skipping %s %s" % (sday, pday))
    day = day - datetime.timedelta(days=1)

        



import scraperwiki
import mechanize
import datetime
import re
import urllib2
import cookielib
import os

# http://hpzworkstations.com/
# Very involved Liverpool planning scraper attempting to get all fields out of their database, which goes back to 1996
# Searches for all applications on a single day, and handles the pagination of the list of applications which requires cookies to execute
# mechanize is unable to follow the links itself because the href values are stuffed with linefeeds, &#0D strings and control characters (see CleanCrapFromLink())

liverpoolplanningurl = "http://northgate.liverpool.gov.uk/planningexploreraa/"

# types of fields that have dates in them
decisionlist = ["Refuse", "Withdrawn", "Approve with Conditions", "Approve without Conditions", "Allowed", "Dismissed", "Prior Approval Given",
                "Split Decision", "Certificate of Lawfulness - Granted", 
                "Final Decision - Dismissed", "Final Decision - Withdrawn", "Conditions Discharged", "No Objections"]
datetypes = ["Date %s" % d  for d in decisionlist ]
datetypes.extend(["Date Registered", "Comments Until", "Appeal Lodged", "Application Registered", "Date Decision"])


cj = cookielib.CookieJar()  # also used by the mechanize.Browser
urllibopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllibopener.addheaders.append (('x-runid', os.environ['RUNID']))

def scrape(url, refererurl):
    try:
        fin = urllibopener.open(url)
        text = fin.read()
        fin.close()
    except:
        log("gone bad " + url)
        return ""
    return text

    #req = urllib2.Request(data["url"])
    #req.add_header('Referer', refererurl)
    #rr = urllib2.urlopen(req)


import time
def log(s):
    time.sleep(0.15)
    print str(s)
    time.sleep(0.2)

def CleanupData(data):
    # convert the location
    if 'Location Co ordinates' in data:
        mcoords = re.match('Easting(\d*)Northing(\d*)$', data['Location Co ordinates'])
        if mcoords.group(1) and mcoords.group(2):  # missing coordinates leave the numbers blank
            seasting = mcoords.group(1)
            snorthing = mcoords.group(2)
            if len(seasting) == 6:
                seasting += "0"
            if len(snorthing) == 6:
                snorthing += "0"
            easting = int(seasting) / 10.0
            northing = int(snorthing) / 10.0
            data["latlng"] = scraperwiki.geo.os_easting_northing_to_latlng(easting, northing)
            data["location"] = "OSEastingNorthing(%f, %f)" % (easting, northing)
        del data['Location Co ordinates']

    # markup dates
    for k in data:
        if k in datetypes:
            mdate = re.match("\s*(\d\d)-(\d\d)-(\d\d\d\d)$", data[k])
            if mdate:
                data[k] = datetime.date(int(mdate.group(3)), int(mdate.group(2)), int(mdate.group(1)))
            else:
                log("Bad date %s %s" % (k, data[k]))

    # separate telephone numbers from case officer
    if "Case Officer / Tel" in data:
        mcaseofficertel = re.match("(.*?)\s*(\d+)$", data["Case Officer / Tel"])
        if mcaseofficertel:
            caseofficer = mcaseofficertel.group(1)
            data["telephone"] = mcaseofficertel.group(2)
        else:
            caseofficer = data["Case Officer / Tel"]
        if caseofficer != data["Planning Officer"]:
            log("Planning/Case %s %s" % (data["Planning Officer"], caseofficer))
        del data["Case Officer / Tel"]
    
    if "Applicant" in data:
        data["Applicant"] = re.sub("&amp;", "&", data["Applicant"])
    if "Agent" in data:
        data["Agent"] = re.sub("&amp;", "&", data["Agent"])

    data["date"] = data["Date Registered"]

    
            
# there are multiple ul lists containing duplicate entries on the
def ParsePlanningDetails(data, text):
    dets = re.search("(?i)<h1>Details Page for Planning Application\xc2\xa0-\xc2\xa0(.*)</h1>", text)
    if not dets:
        log("failed: " + text)
        return
    if data["Application Number"] != dets.group(1):
        log("Application num failure %s %s" % (data["Application Number"], dets.group(1)))
    
    # all relevant lists
    ulists = re.findall("(?si)<ul class=\"list\">(.*?)</ul>", text)
    for ul in ulists[:-1]: # the last list leads to more links

        # all rows in relevant lists
        kv = re.findall("(?s)<li>\s*<div>\s*<span>\s*(.*?)\s*</span>\s*(.*?)\s*</div>\s*</li>", ul)
        #log("= " + str(kv))
        for k, v in kv:
            lv = re.sub("&#xD;|&#xA;|\xc2|\xa0|\r", "", v).strip()
            lv = re.sub("é", "e", lv)
            lv = re.sub("\xbd|\xbf", "?", lv)
            #log("kv %s,%s" % (k, lv))
            lv = unicode(lv, errors="replace")
            
            if k not in data:
                if lv:  # only include if there is an entry here
                    data[k] = lv
            elif data[k] != lv:
                dv = data[k]
                if k in ["Decision", "Appeal Decision"] and data[k] in decisionlist:
                    if len(lv) < len(dv):
                        dv, lv = lv, dv  # sometimes the date is in the index
                    if lv[:len(dv)] == dv:
                        data["Date " + k] = lv[len(data[k])+1:]
                    else:
                        log("FDetails don't match: %s %s %s" % (k, data[k], lv))
                elif re.sub("\s", "", dv) != re.sub("\s", "", lv):
                    log("Details don't match: :%s: :%s: :%s:" % (k, data[k], lv))
            


def CleanCrapFromLink(surl, clen):
    clen = re.sub("&#xD;|&#xA;|\t", "", clen)
    clen = re.sub(" ", "%20", clen)
    clen = re.sub("&amp;", "&", clen)
    return surl + clen

                            
def ParseSearchResultTableRow(surl, headers, cols):
    assert len(headers) == len(cols), cols
    data = dict(zip(headers, cols))
    
    # separate link and application number
    mappl = re.search('(?si)\s*<a class="data_text" href="(StdDetails.aspx?[^\"]*)">([^<]*)</a>', data["Application Number"])
    data["Application Number"] = mappl.group(2)
    data["url"] = CleanCrapFromLink(surl, mappl.group(1))
    
    return data


def ParseSearchResultTable(surl, text):

    # table with results
    mtable = re.search('(?s)<table[^>]*? summary=\"Results of the Search\"[^>]*?(.*?)</table>', text)
    if not mtable:
        if not re.search('No Records Found.', text):
            log("missing No records: " + re.sub("<", "&lt;", text))
        return [ ]

    # rows
    rows = re.findall("(?si)<tr[^>]*>(.*?)</tr>", mtable.group(1))
    headers = re.findall("<th class=\"data_header\">(.*?)</th>", rows[0])
     
    # process each application in table
    results = [ ]
    for row in rows[1:]:
        cols = re.findall("(?si)<td.*?>(.*?)</td>", row)                          
        aproc = ParseSearchResultTableRow(surl, headers, cols)
        results.append(aproc)
    return results
    
                                          
def ScrapePlanningApplications(lastday, daysback):
    firstday = lastday - datetime.timedelta(days=daysback)
    #log("Doing " + str(firstday))
    
    cj.clear()
    br = mechanize.Browser()
    br.addheaders = [ [ 'x-runid', os.environ['RUNID'] ] ]
    
    
    br.set_cookiejar(cj)
    br.open(liverpoolplanningurl)
            
    br.select_form(name="M3Form")

    br["dateStart"] = firstday.strftime("%d/%m/%Y")    
    br["dateEnd"] = lastday.strftime("%d/%m/%Y")
    br["rbGroup"] = ["rbRange"]
    g = br.submit()
    tabletext = g.read()
                  
    surl = re.sub("(?s)StdResults.*$", "", br.geturl())
        
    npages, nrecords = 0, 0
    refererurl = br.geturl()
    
    while True:
        rows = ParseSearchResultTable(surl, tabletext)
        for data in rows:
            #log(nrecords)
            ParsePlanningDetails(data, scrape(data["url"], refererurl))
            CleanupData(data)
            #log("-  " + str(data))
            scraperwiki.datastore.save(unique_keys=["Application Number"], data=data)
            nrecords += 1
        
        mnextlink = re.search('(?s)<a class="noborder" href="(StdResults.aspx[^"]*?)"><img src="/PlanningExplorerAA/SiteFiles/Skins/Default_AA/Images/arrowr.gif" alt="Go to next page "', tabletext)
        if not mnextlink:
            break
        
        nexturl = CleanCrapFromLink(surl, mnextlink.group(1))            
        npages += 1
        log("Page %d %s" % (npages, nexturl))
        
        tabletext = scrape(nexturl, refererurl)
        #log(re.sub("<", "&lt;", tabletext))
        refererurl = nexturl
        #break
    return nrecords, npages



# iterate through day by day
day = datetime.date.today()
# all of 2008-2006 done 
# 
#day = datetime.date(2005, 7, 6)  # run back to 7/17
for i in range(30):
    sday = day.strftime("%d/%m/%Y")
    pday = None # scraperwiki.page_cache.getpagebyname(sday)
    if not pday:
        nrecords, npages = ScrapePlanningApplications(day, 0)
        pday =  "%d %d" % (nrecords, npages)
        log("Scraped %d from %s" % (nrecords, sday))
        #scraperwiki.page_cache.savepage("dayrec", sday, pday)
    else:
        log("skipping %s %s" % (sday, pday))
    day = day - datetime.timedelta(days=1)

        



import scraperwiki
import mechanize
import datetime
import re
import urllib2
import cookielib
import os

# http://hpzworkstations.com/
# Very involved Liverpool planning scraper attempting to get all fields out of their database, which goes back to 1996
# Searches for all applications on a single day, and handles the pagination of the list of applications which requires cookies to execute
# mechanize is unable to follow the links itself because the href values are stuffed with linefeeds, &#0D strings and control characters (see CleanCrapFromLink())

liverpoolplanningurl = "http://northgate.liverpool.gov.uk/planningexploreraa/"

# types of fields that have dates in them
decisionlist = ["Refuse", "Withdrawn", "Approve with Conditions", "Approve without Conditions", "Allowed", "Dismissed", "Prior Approval Given",
                "Split Decision", "Certificate of Lawfulness - Granted", 
                "Final Decision - Dismissed", "Final Decision - Withdrawn", "Conditions Discharged", "No Objections"]
datetypes = ["Date %s" % d  for d in decisionlist ]
datetypes.extend(["Date Registered", "Comments Until", "Appeal Lodged", "Application Registered", "Date Decision"])


cj = cookielib.CookieJar()  # also used by the mechanize.Browser
urllibopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllibopener.addheaders.append (('x-runid', os.environ['RUNID']))

def scrape(url, refererurl):
    try:
        fin = urllibopener.open(url)
        text = fin.read()
        fin.close()
    except:
        log("gone bad " + url)
        return ""
    return text

    #req = urllib2.Request(data["url"])
    #req.add_header('Referer', refererurl)
    #rr = urllib2.urlopen(req)


import time
def log(s):
    time.sleep(0.15)
    print str(s)
    time.sleep(0.2)

def CleanupData(data):
    # convert the location
    if 'Location Co ordinates' in data:
        mcoords = re.match('Easting(\d*)Northing(\d*)$', data['Location Co ordinates'])
        if mcoords.group(1) and mcoords.group(2):  # missing coordinates leave the numbers blank
            seasting = mcoords.group(1)
            snorthing = mcoords.group(2)
            if len(seasting) == 6:
                seasting += "0"
            if len(snorthing) == 6:
                snorthing += "0"
            easting = int(seasting) / 10.0
            northing = int(snorthing) / 10.0
            data["latlng"] = scraperwiki.geo.os_easting_northing_to_latlng(easting, northing)
            data["location"] = "OSEastingNorthing(%f, %f)" % (easting, northing)
        del data['Location Co ordinates']

    # markup dates
    for k in data:
        if k in datetypes:
            mdate = re.match("\s*(\d\d)-(\d\d)-(\d\d\d\d)$", data[k])
            if mdate:
                data[k] = datetime.date(int(mdate.group(3)), int(mdate.group(2)), int(mdate.group(1)))
            else:
                log("Bad date %s %s" % (k, data[k]))

    # separate telephone numbers from case officer
    if "Case Officer / Tel" in data:
        mcaseofficertel = re.match("(.*?)\s*(\d+)$", data["Case Officer / Tel"])
        if mcaseofficertel:
            caseofficer = mcaseofficertel.group(1)
            data["telephone"] = mcaseofficertel.group(2)
        else:
            caseofficer = data["Case Officer / Tel"]
        if caseofficer != data["Planning Officer"]:
            log("Planning/Case %s %s" % (data["Planning Officer"], caseofficer))
        del data["Case Officer / Tel"]
    
    if "Applicant" in data:
        data["Applicant"] = re.sub("&amp;", "&", data["Applicant"])
    if "Agent" in data:
        data["Agent"] = re.sub("&amp;", "&", data["Agent"])

    data["date"] = data["Date Registered"]

    
            
# there are multiple ul lists containing duplicate entries on the
def ParsePlanningDetails(data, text):
    dets = re.search("(?i)<h1>Details Page for Planning Application\xc2\xa0-\xc2\xa0(.*)</h1>", text)
    if not dets:
        log("failed: " + text)
        return
    if data["Application Number"] != dets.group(1):
        log("Application num failure %s %s" % (data["Application Number"], dets.group(1)))
    
    # all relevant lists
    ulists = re.findall("(?si)<ul class=\"list\">(.*?)</ul>", text)
    for ul in ulists[:-1]: # the last list leads to more links

        # all rows in relevant lists
        kv = re.findall("(?s)<li>\s*<div>\s*<span>\s*(.*?)\s*</span>\s*(.*?)\s*</div>\s*</li>", ul)
        #log("= " + str(kv))
        for k, v in kv:
            lv = re.sub("&#xD;|&#xA;|\xc2|\xa0|\r", "", v).strip()
            lv = re.sub("é", "e", lv)
            lv = re.sub("\xbd|\xbf", "?", lv)
            #log("kv %s,%s" % (k, lv))
            lv = unicode(lv, errors="replace")
            
            if k not in data:
                if lv:  # only include if there is an entry here
                    data[k] = lv
            elif data[k] != lv:
                dv = data[k]
                if k in ["Decision", "Appeal Decision"] and data[k] in decisionlist:
                    if len(lv) < len(dv):
                        dv, lv = lv, dv  # sometimes the date is in the index
                    if lv[:len(dv)] == dv:
                        data["Date " + k] = lv[len(data[k])+1:]
                    else:
                        log("FDetails don't match: %s %s %s" % (k, data[k], lv))
                elif re.sub("\s", "", dv) != re.sub("\s", "", lv):
                    log("Details don't match: :%s: :%s: :%s:" % (k, data[k], lv))
            


def CleanCrapFromLink(surl, clen):
    clen = re.sub("&#xD;|&#xA;|\t", "", clen)
    clen = re.sub(" ", "%20", clen)
    clen = re.sub("&amp;", "&", clen)
    return surl + clen

                            
def ParseSearchResultTableRow(surl, headers, cols):
    assert len(headers) == len(cols), cols
    data = dict(zip(headers, cols))
    
    # separate link and application number
    mappl = re.search('(?si)\s*<a class="data_text" href="(StdDetails.aspx?[^\"]*)">([^<]*)</a>', data["Application Number"])
    data["Application Number"] = mappl.group(2)
    data["url"] = CleanCrapFromLink(surl, mappl.group(1))
    
    return data


def ParseSearchResultTable(surl, text):

    # table with results
    mtable = re.search('(?s)<table[^>]*? summary=\"Results of the Search\"[^>]*?(.*?)</table>', text)
    if not mtable:
        if not re.search('No Records Found.', text):
            log("missing No records: " + re.sub("<", "&lt;", text))
        return [ ]

    # rows
    rows = re.findall("(?si)<tr[^>]*>(.*?)</tr>", mtable.group(1))
    headers = re.findall("<th class=\"data_header\">(.*?)</th>", rows[0])
     
    # process each application in table
    results = [ ]
    for row in rows[1:]:
        cols = re.findall("(?si)<td.*?>(.*?)</td>", row)                          
        aproc = ParseSearchResultTableRow(surl, headers, cols)
        results.append(aproc)
    return results
    
                                          
def ScrapePlanningApplications(lastday, daysback):
    firstday = lastday - datetime.timedelta(days=daysback)
    #log("Doing " + str(firstday))
    
    cj.clear()
    br = mechanize.Browser()
    br.addheaders = [ [ 'x-runid', os.environ['RUNID'] ] ]
    
    
    br.set_cookiejar(cj)
    br.open(liverpoolplanningurl)
            
    br.select_form(name="M3Form")

    br["dateStart"] = firstday.strftime("%d/%m/%Y")    
    br["dateEnd"] = lastday.strftime("%d/%m/%Y")
    br["rbGroup"] = ["rbRange"]
    g = br.submit()
    tabletext = g.read()
                  
    surl = re.sub("(?s)StdResults.*$", "", br.geturl())
        
    npages, nrecords = 0, 0
    refererurl = br.geturl()
    
    while True:
        rows = ParseSearchResultTable(surl, tabletext)
        for data in rows:
            #log(nrecords)
            ParsePlanningDetails(data, scrape(data["url"], refererurl))
            CleanupData(data)
            #log("-  " + str(data))
            scraperwiki.datastore.save(unique_keys=["Application Number"], data=data)
            nrecords += 1
        
        mnextlink = re.search('(?s)<a class="noborder" href="(StdResults.aspx[^"]*?)"><img src="/PlanningExplorerAA/SiteFiles/Skins/Default_AA/Images/arrowr.gif" alt="Go to next page "', tabletext)
        if not mnextlink:
            break
        
        nexturl = CleanCrapFromLink(surl, mnextlink.group(1))            
        npages += 1
        log("Page %d %s" % (npages, nexturl))
        
        tabletext = scrape(nexturl, refererurl)
        #log(re.sub("<", "&lt;", tabletext))
        refererurl = nexturl
        #break
    return nrecords, npages



# iterate through day by day
day = datetime.date.today()
# all of 2008-2006 done 
# 
#day = datetime.date(2005, 7, 6)  # run back to 7/17
for i in range(30):
    sday = day.strftime("%d/%m/%Y")
    pday = None # scraperwiki.page_cache.getpagebyname(sday)
    if not pday:
        nrecords, npages = ScrapePlanningApplications(day, 0)
        pday =  "%d %d" % (nrecords, npages)
        log("Scraped %d from %s" % (nrecords, sday))
        #scraperwiki.page_cache.savepage("dayrec", sday, pday)
    else:
        log("skipping %s %s" % (sday, pday))
    day = day - datetime.timedelta(days=1)

        



import scraperwiki
import mechanize
import datetime
import re
import urllib2
import cookielib
import os

# http://hpzworkstations.com/
# Very involved Liverpool planning scraper attempting to get all fields out of their database, which goes back to 1996
# Searches for all applications on a single day, and handles the pagination of the list of applications which requires cookies to execute
# mechanize is unable to follow the links itself because the href values are stuffed with linefeeds, &#0D strings and control characters (see CleanCrapFromLink())

liverpoolplanningurl = "http://northgate.liverpool.gov.uk/planningexploreraa/"

# types of fields that have dates in them
decisionlist = ["Refuse", "Withdrawn", "Approve with Conditions", "Approve without Conditions", "Allowed", "Dismissed", "Prior Approval Given",
                "Split Decision", "Certificate of Lawfulness - Granted", 
                "Final Decision - Dismissed", "Final Decision - Withdrawn", "Conditions Discharged", "No Objections"]
datetypes = ["Date %s" % d  for d in decisionlist ]
datetypes.extend(["Date Registered", "Comments Until", "Appeal Lodged", "Application Registered", "Date Decision"])


cj = cookielib.CookieJar()  # also used by the mechanize.Browser
urllibopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllibopener.addheaders.append (('x-runid', os.environ['RUNID']))

def scrape(url, refererurl):
    try:
        fin = urllibopener.open(url)
        text = fin.read()
        fin.close()
    except:
        log("gone bad " + url)
        return ""
    return text

    #req = urllib2.Request(data["url"])
    #req.add_header('Referer', refererurl)
    #rr = urllib2.urlopen(req)


import time
def log(s):
    time.sleep(0.15)
    print str(s)
    time.sleep(0.2)

def CleanupData(data):
    # convert the location
    if 'Location Co ordinates' in data:
        mcoords = re.match('Easting(\d*)Northing(\d*)$', data['Location Co ordinates'])
        if mcoords.group(1) and mcoords.group(2):  # missing coordinates leave the numbers blank
            seasting = mcoords.group(1)
            snorthing = mcoords.group(2)
            if len(seasting) == 6:
                seasting += "0"
            if len(snorthing) == 6:
                snorthing += "0"
            easting = int(seasting) / 10.0
            northing = int(snorthing) / 10.0
            data["latlng"] = scraperwiki.geo.os_easting_northing_to_latlng(easting, northing)
            data["location"] = "OSEastingNorthing(%f, %f)" % (easting, northing)
        del data['Location Co ordinates']

    # markup dates
    for k in data:
        if k in datetypes:
            mdate = re.match("\s*(\d\d)-(\d\d)-(\d\d\d\d)$", data[k])
            if mdate:
                data[k] = datetime.date(int(mdate.group(3)), int(mdate.group(2)), int(mdate.group(1)))
            else:
                log("Bad date %s %s" % (k, data[k]))

    # separate telephone numbers from case officer
    if "Case Officer / Tel" in data:
        mcaseofficertel = re.match("(.*?)\s*(\d+)$", data["Case Officer / Tel"])
        if mcaseofficertel:
            caseofficer = mcaseofficertel.group(1)
            data["telephone"] = mcaseofficertel.group(2)
        else:
            caseofficer = data["Case Officer / Tel"]
        if caseofficer != data["Planning Officer"]:
            log("Planning/Case %s %s" % (data["Planning Officer"], caseofficer))
        del data["Case Officer / Tel"]
    
    if "Applicant" in data:
        data["Applicant"] = re.sub("&amp;", "&", data["Applicant"])
    if "Agent" in data:
        data["Agent"] = re.sub("&amp;", "&", data["Agent"])

    data["date"] = data["Date Registered"]

    
            
# there are multiple ul lists containing duplicate entries on the
def ParsePlanningDetails(data, text):
    dets = re.search("(?i)<h1>Details Page for Planning Application\xc2\xa0-\xc2\xa0(.*)</h1>", text)
    if not dets:
        log("failed: " + text)
        return
    if data["Application Number"] != dets.group(1):
        log("Application num failure %s %s" % (data["Application Number"], dets.group(1)))
    
    # all relevant lists
    ulists = re.findall("(?si)<ul class=\"list\">(.*?)</ul>", text)
    for ul in ulists[:-1]: # the last list leads to more links

        # all rows in relevant lists
        kv = re.findall("(?s)<li>\s*<div>\s*<span>\s*(.*?)\s*</span>\s*(.*?)\s*</div>\s*</li>", ul)
        #log("= " + str(kv))
        for k, v in kv:
            lv = re.sub("&#xD;|&#xA;|\xc2|\xa0|\r", "", v).strip()
            lv = re.sub("é", "e", lv)
            lv = re.sub("\xbd|\xbf", "?", lv)
            #log("kv %s,%s" % (k, lv))
            lv = unicode(lv, errors="replace")
            
            if k not in data:
                if lv:  # only include if there is an entry here
                    data[k] = lv
            elif data[k] != lv:
                dv = data[k]
                if k in ["Decision", "Appeal Decision"] and data[k] in decisionlist:
                    if len(lv) < len(dv):
                        dv, lv = lv, dv  # sometimes the date is in the index
                    if lv[:len(dv)] == dv:
                        data["Date " + k] = lv[len(data[k])+1:]
                    else:
                        log("FDetails don't match: %s %s %s" % (k, data[k], lv))
                elif re.sub("\s", "", dv) != re.sub("\s", "", lv):
                    log("Details don't match: :%s: :%s: :%s:" % (k, data[k], lv))
            


def CleanCrapFromLink(surl, clen):
    clen = re.sub("&#xD;|&#xA;|\t", "", clen)
    clen = re.sub(" ", "%20", clen)
    clen = re.sub("&amp;", "&", clen)
    return surl + clen

                            
def ParseSearchResultTableRow(surl, headers, cols):
    assert len(headers) == len(cols), cols
    data = dict(zip(headers, cols))
    
    # separate link and application number
    mappl = re.search('(?si)\s*<a class="data_text" href="(StdDetails.aspx?[^\"]*)">([^<]*)</a>', data["Application Number"])
    data["Application Number"] = mappl.group(2)
    data["url"] = CleanCrapFromLink(surl, mappl.group(1))
    
    return data


def ParseSearchResultTable(surl, text):

    # table with results
    mtable = re.search('(?s)<table[^>]*? summary=\"Results of the Search\"[^>]*?(.*?)</table>', text)
    if not mtable:
        if not re.search('No Records Found.', text):
            log("missing No records: " + re.sub("<", "&lt;", text))
        return [ ]

    # rows
    rows = re.findall("(?si)<tr[^>]*>(.*?)</tr>", mtable.group(1))
    headers = re.findall("<th class=\"data_header\">(.*?)</th>", rows[0])
     
    # process each application in table
    results = [ ]
    for row in rows[1:]:
        cols = re.findall("(?si)<td.*?>(.*?)</td>", row)                          
        aproc = ParseSearchResultTableRow(surl, headers, cols)
        results.append(aproc)
    return results
    
                                          
def ScrapePlanningApplications(lastday, daysback):
    firstday = lastday - datetime.timedelta(days=daysback)
    #log("Doing " + str(firstday))
    
    cj.clear()
    br = mechanize.Browser()
    br.addheaders = [ [ 'x-runid', os.environ['RUNID'] ] ]
    
    
    br.set_cookiejar(cj)
    br.open(liverpoolplanningurl)
            
    br.select_form(name="M3Form")

    br["dateStart"] = firstday.strftime("%d/%m/%Y")    
    br["dateEnd"] = lastday.strftime("%d/%m/%Y")
    br["rbGroup"] = ["rbRange"]
    g = br.submit()
    tabletext = g.read()
                  
    surl = re.sub("(?s)StdResults.*$", "", br.geturl())
        
    npages, nrecords = 0, 0
    refererurl = br.geturl()
    
    while True:
        rows = ParseSearchResultTable(surl, tabletext)
        for data in rows:
            #log(nrecords)
            ParsePlanningDetails(data, scrape(data["url"], refererurl))
            CleanupData(data)
            #log("-  " + str(data))
            scraperwiki.datastore.save(unique_keys=["Application Number"], data=data)
            nrecords += 1
        
        mnextlink = re.search('(?s)<a class="noborder" href="(StdResults.aspx[^"]*?)"><img src="/PlanningExplorerAA/SiteFiles/Skins/Default_AA/Images/arrowr.gif" alt="Go to next page "', tabletext)
        if not mnextlink:
            break
        
        nexturl = CleanCrapFromLink(surl, mnextlink.group(1))            
        npages += 1
        log("Page %d %s" % (npages, nexturl))
        
        tabletext = scrape(nexturl, refererurl)
        #log(re.sub("<", "&lt;", tabletext))
        refererurl = nexturl
        #break
    return nrecords, npages



# iterate through day by day
day = datetime.date.today()
# all of 2008-2006 done 
# 
#day = datetime.date(2005, 7, 6)  # run back to 7/17
for i in range(30):
    sday = day.strftime("%d/%m/%Y")
    pday = None # scraperwiki.page_cache.getpagebyname(sday)
    if not pday:
        nrecords, npages = ScrapePlanningApplications(day, 0)
        pday =  "%d %d" % (nrecords, npages)
        log("Scraped %d from %s" % (nrecords, sday))
        #scraperwiki.page_cache.savepage("dayrec", sday, pday)
    else:
        log("skipping %s %s" % (sday, pday))
    day = day - datetime.timedelta(days=1)

        



import scraperwiki
import mechanize
import datetime
import re
import urllib2
import cookielib
import os

# http://hpzworkstations.com/
# Very involved Liverpool planning scraper attempting to get all fields out of their database, which goes back to 1996
# Searches for all applications on a single day, and handles the pagination of the list of applications which requires cookies to execute
# mechanize is unable to follow the links itself because the href values are stuffed with linefeeds, &#0D strings and control characters (see CleanCrapFromLink())

liverpoolplanningurl = "http://northgate.liverpool.gov.uk/planningexploreraa/"

# types of fields that have dates in them
decisionlist = ["Refuse", "Withdrawn", "Approve with Conditions", "Approve without Conditions", "Allowed", "Dismissed", "Prior Approval Given",
                "Split Decision", "Certificate of Lawfulness - Granted", 
                "Final Decision - Dismissed", "Final Decision - Withdrawn", "Conditions Discharged", "No Objections"]
datetypes = ["Date %s" % d  for d in decisionlist ]
datetypes.extend(["Date Registered", "Comments Until", "Appeal Lodged", "Application Registered", "Date Decision"])


cj = cookielib.CookieJar()  # also used by the mechanize.Browser
urllibopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllibopener.addheaders.append (('x-runid', os.environ['RUNID']))

def scrape(url, refererurl):
    try:
        fin = urllibopener.open(url)
        text = fin.read()
        fin.close()
    except:
        log("gone bad " + url)
        return ""
    return text

    #req = urllib2.Request(data["url"])
    #req.add_header('Referer', refererurl)
    #rr = urllib2.urlopen(req)


import time
def log(s):
    time.sleep(0.15)
    print str(s)
    time.sleep(0.2)

def CleanupData(data):
    # convert the location
    if 'Location Co ordinates' in data:
        mcoords = re.match('Easting(\d*)Northing(\d*)$', data['Location Co ordinates'])
        if mcoords.group(1) and mcoords.group(2):  # missing coordinates leave the numbers blank
            seasting = mcoords.group(1)
            snorthing = mcoords.group(2)
            if len(seasting) == 6:
                seasting += "0"
            if len(snorthing) == 6:
                snorthing += "0"
            easting = int(seasting) / 10.0
            northing = int(snorthing) / 10.0
            data["latlng"] = scraperwiki.geo.os_easting_northing_to_latlng(easting, northing)
            data["location"] = "OSEastingNorthing(%f, %f)" % (easting, northing)
        del data['Location Co ordinates']

    # markup dates
    for k in data:
        if k in datetypes:
            mdate = re.match("\s*(\d\d)-(\d\d)-(\d\d\d\d)$", data[k])
            if mdate:
                data[k] = datetime.date(int(mdate.group(3)), int(mdate.group(2)), int(mdate.group(1)))
            else:
                log("Bad date %s %s" % (k, data[k]))

    # separate telephone numbers from case officer
    if "Case Officer / Tel" in data:
        mcaseofficertel = re.match("(.*?)\s*(\d+)$", data["Case Officer / Tel"])
        if mcaseofficertel:
            caseofficer = mcaseofficertel.group(1)
            data["telephone"] = mcaseofficertel.group(2)
        else:
            caseofficer = data["Case Officer / Tel"]
        if caseofficer != data["Planning Officer"]:
            log("Planning/Case %s %s" % (data["Planning Officer"], caseofficer))
        del data["Case Officer / Tel"]
    
    if "Applicant" in data:
        data["Applicant"] = re.sub("&amp;", "&", data["Applicant"])
    if "Agent" in data:
        data["Agent"] = re.sub("&amp;", "&", data["Agent"])

    data["date"] = data["Date Registered"]

    
            
# there are multiple ul lists containing duplicate entries on the
def ParsePlanningDetails(data, text):
    dets = re.search("(?i)<h1>Details Page for Planning Application\xc2\xa0-\xc2\xa0(.*)</h1>", text)
    if not dets:
        log("failed: " + text)
        return
    if data["Application Number"] != dets.group(1):
        log("Application num failure %s %s" % (data["Application Number"], dets.group(1)))
    
    # all relevant lists
    ulists = re.findall("(?si)<ul class=\"list\">(.*?)</ul>", text)
    for ul in ulists[:-1]: # the last list leads to more links

        # all rows in relevant lists
        kv = re.findall("(?s)<li>\s*<div>\s*<span>\s*(.*?)\s*</span>\s*(.*?)\s*</div>\s*</li>", ul)
        #log("= " + str(kv))
        for k, v in kv:
            lv = re.sub("&#xD;|&#xA;|\xc2|\xa0|\r", "", v).strip()
            lv = re.sub("é", "e", lv)
            lv = re.sub("\xbd|\xbf", "?", lv)
            #log("kv %s,%s" % (k, lv))
            lv = unicode(lv, errors="replace")
            
            if k not in data:
                if lv:  # only include if there is an entry here
                    data[k] = lv
            elif data[k] != lv:
                dv = data[k]
                if k in ["Decision", "Appeal Decision"] and data[k] in decisionlist:
                    if len(lv) < len(dv):
                        dv, lv = lv, dv  # sometimes the date is in the index
                    if lv[:len(dv)] == dv:
                        data["Date " + k] = lv[len(data[k])+1:]
                    else:
                        log("FDetails don't match: %s %s %s" % (k, data[k], lv))
                elif re.sub("\s", "", dv) != re.sub("\s", "", lv):
                    log("Details don't match: :%s: :%s: :%s:" % (k, data[k], lv))
            


def CleanCrapFromLink(surl, clen):
    clen = re.sub("&#xD;|&#xA;|\t", "", clen)
    clen = re.sub(" ", "%20", clen)
    clen = re.sub("&amp;", "&", clen)
    return surl + clen

                            
def ParseSearchResultTableRow(surl, headers, cols):
    assert len(headers) == len(cols), cols
    data = dict(zip(headers, cols))
    
    # separate link and application number
    mappl = re.search('(?si)\s*<a class="data_text" href="(StdDetails.aspx?[^\"]*)">([^<]*)</a>', data["Application Number"])
    data["Application Number"] = mappl.group(2)
    data["url"] = CleanCrapFromLink(surl, mappl.group(1))
    
    return data


def ParseSearchResultTable(surl, text):

    # table with results
    mtable = re.search('(?s)<table[^>]*? summary=\"Results of the Search\"[^>]*?(.*?)</table>', text)
    if not mtable:
        if not re.search('No Records Found.', text):
            log("missing No records: " + re.sub("<", "&lt;", text))
        return [ ]

    # rows
    rows = re.findall("(?si)<tr[^>]*>(.*?)</tr>", mtable.group(1))
    headers = re.findall("<th class=\"data_header\">(.*?)</th>", rows[0])
     
    # process each application in table
    results = [ ]
    for row in rows[1:]:
        cols = re.findall("(?si)<td.*?>(.*?)</td>", row)                          
        aproc = ParseSearchResultTableRow(surl, headers, cols)
        results.append(aproc)
    return results
    
                                          
def ScrapePlanningApplications(lastday, daysback):
    firstday = lastday - datetime.timedelta(days=daysback)
    #log("Doing " + str(firstday))
    
    cj.clear()
    br = mechanize.Browser()
    br.addheaders = [ [ 'x-runid', os.environ['RUNID'] ] ]
    
    
    br.set_cookiejar(cj)
    br.open(liverpoolplanningurl)
            
    br.select_form(name="M3Form")

    br["dateStart"] = firstday.strftime("%d/%m/%Y")    
    br["dateEnd"] = lastday.strftime("%d/%m/%Y")
    br["rbGroup"] = ["rbRange"]
    g = br.submit()
    tabletext = g.read()
                  
    surl = re.sub("(?s)StdResults.*$", "", br.geturl())
        
    npages, nrecords = 0, 0
    refererurl = br.geturl()
    
    while True:
        rows = ParseSearchResultTable(surl, tabletext)
        for data in rows:
            #log(nrecords)
            ParsePlanningDetails(data, scrape(data["url"], refererurl))
            CleanupData(data)
            #log("-  " + str(data))
            scraperwiki.datastore.save(unique_keys=["Application Number"], data=data)
            nrecords += 1
        
        mnextlink = re.search('(?s)<a class="noborder" href="(StdResults.aspx[^"]*?)"><img src="/PlanningExplorerAA/SiteFiles/Skins/Default_AA/Images/arrowr.gif" alt="Go to next page "', tabletext)
        if not mnextlink:
            break
        
        nexturl = CleanCrapFromLink(surl, mnextlink.group(1))            
        npages += 1
        log("Page %d %s" % (npages, nexturl))
        
        tabletext = scrape(nexturl, refererurl)
        #log(re.sub("<", "&lt;", tabletext))
        refererurl = nexturl
        #break
    return nrecords, npages



# iterate through day by day
day = datetime.date.today()
# all of 2008-2006 done 
# 
#day = datetime.date(2005, 7, 6)  # run back to 7/17
for i in range(30):
    sday = day.strftime("%d/%m/%Y")
    pday = None # scraperwiki.page_cache.getpagebyname(sday)
    if not pday:
        nrecords, npages = ScrapePlanningApplications(day, 0)
        pday =  "%d %d" % (nrecords, npages)
        log("Scraped %d from %s" % (nrecords, sday))
        #scraperwiki.page_cache.savepage("dayrec", sday, pday)
    else:
        log("skipping %s %s" % (sday, pday))
    day = day - datetime.timedelta(days=1)

        



import scraperwiki
import mechanize
import datetime
import re
import urllib2
import cookielib
import os

# http://hpzworkstations.com/
# Very involved Liverpool planning scraper attempting to get all fields out of their database, which goes back to 1996
# Searches for all applications on a single day, and handles the pagination of the list of applications which requires cookies to execute
# mechanize is unable to follow the links itself because the href values are stuffed with linefeeds, &#0D strings and control characters (see CleanCrapFromLink())

liverpoolplanningurl = "http://northgate.liverpool.gov.uk/planningexploreraa/"

# types of fields that have dates in them
decisionlist = ["Refuse", "Withdrawn", "Approve with Conditions", "Approve without Conditions", "Allowed", "Dismissed", "Prior Approval Given",
                "Split Decision", "Certificate of Lawfulness - Granted", 
                "Final Decision - Dismissed", "Final Decision - Withdrawn", "Conditions Discharged", "No Objections"]
datetypes = ["Date %s" % d  for d in decisionlist ]
datetypes.extend(["Date Registered", "Comments Until", "Appeal Lodged", "Application Registered", "Date Decision"])


cj = cookielib.CookieJar()  # also used by the mechanize.Browser
urllibopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllibopener.addheaders.append (('x-runid', os.environ['RUNID']))

def scrape(url, refererurl):
    try:
        fin = urllibopener.open(url)
        text = fin.read()
        fin.close()
    except:
        log("gone bad " + url)
        return ""
    return text

    #req = urllib2.Request(data["url"])
    #req.add_header('Referer', refererurl)
    #rr = urllib2.urlopen(req)


import time
def log(s):
    time.sleep(0.15)
    print str(s)
    time.sleep(0.2)

def CleanupData(data):
    # convert the location
    if 'Location Co ordinates' in data:
        mcoords = re.match('Easting(\d*)Northing(\d*)$', data['Location Co ordinates'])
        if mcoords.group(1) and mcoords.group(2):  # missing coordinates leave the numbers blank
            seasting = mcoords.group(1)
            snorthing = mcoords.group(2)
            if len(seasting) == 6:
                seasting += "0"
            if len(snorthing) == 6:
                snorthing += "0"
            easting = int(seasting) / 10.0
            northing = int(snorthing) / 10.0
            data["latlng"] = scraperwiki.geo.os_easting_northing_to_latlng(easting, northing)
            data["location"] = "OSEastingNorthing(%f, %f)" % (easting, northing)
        del data['Location Co ordinates']

    # markup dates
    for k in data:
        if k in datetypes:
            mdate = re.match("\s*(\d\d)-(\d\d)-(\d\d\d\d)$", data[k])
            if mdate:
                data[k] = datetime.date(int(mdate.group(3)), int(mdate.group(2)), int(mdate.group(1)))
            else:
                log("Bad date %s %s" % (k, data[k]))

    # separate telephone numbers from case officer
    if "Case Officer / Tel" in data:
        mcaseofficertel = re.match("(.*?)\s*(\d+)$", data["Case Officer / Tel"])
        if mcaseofficertel:
            caseofficer = mcaseofficertel.group(1)
            data["telephone"] = mcaseofficertel.group(2)
        else:
            caseofficer = data["Case Officer / Tel"]
        if caseofficer != data["Planning Officer"]:
            log("Planning/Case %s %s" % (data["Planning Officer"], caseofficer))
        del data["Case Officer / Tel"]
    
    if "Applicant" in data:
        data["Applicant"] = re.sub("&amp;", "&", data["Applicant"])
    if "Agent" in data:
        data["Agent"] = re.sub("&amp;", "&", data["Agent"])

    data["date"] = data["Date Registered"]

    
            
# there are multiple ul lists containing duplicate entries on the
def ParsePlanningDetails(data, text):
    dets = re.search("(?i)<h1>Details Page for Planning Application\xc2\xa0-\xc2\xa0(.*)</h1>", text)
    if not dets:
        log("failed: " + text)
        return
    if data["Application Number"] != dets.group(1):
        log("Application num failure %s %s" % (data["Application Number"], dets.group(1)))
    
    # all relevant lists
    ulists = re.findall("(?si)<ul class=\"list\">(.*?)</ul>", text)
    for ul in ulists[:-1]: # the last list leads to more links

        # all rows in relevant lists
        kv = re.findall("(?s)<li>\s*<div>\s*<span>\s*(.*?)\s*</span>\s*(.*?)\s*</div>\s*</li>", ul)
        #log("= " + str(kv))
        for k, v in kv:
            lv = re.sub("&#xD;|&#xA;|\xc2|\xa0|\r", "", v).strip()
            lv = re.sub("é", "e", lv)
            lv = re.sub("\xbd|\xbf", "?", lv)
            #log("kv %s,%s" % (k, lv))
            lv = unicode(lv, errors="replace")
            
            if k not in data:
                if lv:  # only include if there is an entry here
                    data[k] = lv
            elif data[k] != lv:
                dv = data[k]
                if k in ["Decision", "Appeal Decision"] and data[k] in decisionlist:
                    if len(lv) < len(dv):
                        dv, lv = lv, dv  # sometimes the date is in the index
                    if lv[:len(dv)] == dv:
                        data["Date " + k] = lv[len(data[k])+1:]
                    else:
                        log("FDetails don't match: %s %s %s" % (k, data[k], lv))
                elif re.sub("\s", "", dv) != re.sub("\s", "", lv):
                    log("Details don't match: :%s: :%s: :%s:" % (k, data[k], lv))
            


def CleanCrapFromLink(surl, clen):
    clen = re.sub("&#xD;|&#xA;|\t", "", clen)
    clen = re.sub(" ", "%20", clen)
    clen = re.sub("&amp;", "&", clen)
    return surl + clen

                            
def ParseSearchResultTableRow(surl, headers, cols):
    assert len(headers) == len(cols), cols
    data = dict(zip(headers, cols))
    
    # separate link and application number
    mappl = re.search('(?si)\s*<a class="data_text" href="(StdDetails.aspx?[^\"]*)">([^<]*)</a>', data["Application Number"])
    data["Application Number"] = mappl.group(2)
    data["url"] = CleanCrapFromLink(surl, mappl.group(1))
    
    return data


def ParseSearchResultTable(surl, text):

    # table with results
    mtable = re.search('(?s)<table[^>]*? summary=\"Results of the Search\"[^>]*?(.*?)</table>', text)
    if not mtable:
        if not re.search('No Records Found.', text):
            log("missing No records: " + re.sub("<", "&lt;", text))
        return [ ]

    # rows
    rows = re.findall("(?si)<tr[^>]*>(.*?)</tr>", mtable.group(1))
    headers = re.findall("<th class=\"data_header\">(.*?)</th>", rows[0])
     
    # process each application in table
    results = [ ]
    for row in rows[1:]:
        cols = re.findall("(?si)<td.*?>(.*?)</td>", row)                          
        aproc = ParseSearchResultTableRow(surl, headers, cols)
        results.append(aproc)
    return results
    
                                          
def ScrapePlanningApplications(lastday, daysback):
    firstday = lastday - datetime.timedelta(days=daysback)
    #log("Doing " + str(firstday))
    
    cj.clear()
    br = mechanize.Browser()
    br.addheaders = [ [ 'x-runid', os.environ['RUNID'] ] ]
    
    
    br.set_cookiejar(cj)
    br.open(liverpoolplanningurl)
            
    br.select_form(name="M3Form")

    br["dateStart"] = firstday.strftime("%d/%m/%Y")    
    br["dateEnd"] = lastday.strftime("%d/%m/%Y")
    br["rbGroup"] = ["rbRange"]
    g = br.submit()
    tabletext = g.read()
                  
    surl = re.sub("(?s)StdResults.*$", "", br.geturl())
        
    npages, nrecords = 0, 0
    refererurl = br.geturl()
    
    while True:
        rows = ParseSearchResultTable(surl, tabletext)
        for data in rows:
            #log(nrecords)
            ParsePlanningDetails(data, scrape(data["url"], refererurl))
            CleanupData(data)
            #log("-  " + str(data))
            scraperwiki.datastore.save(unique_keys=["Application Number"], data=data)
            nrecords += 1
        
        mnextlink = re.search('(?s)<a class="noborder" href="(StdResults.aspx[^"]*?)"><img src="/PlanningExplorerAA/SiteFiles/Skins/Default_AA/Images/arrowr.gif" alt="Go to next page "', tabletext)
        if not mnextlink:
            break
        
        nexturl = CleanCrapFromLink(surl, mnextlink.group(1))            
        npages += 1
        log("Page %d %s" % (npages, nexturl))
        
        tabletext = scrape(nexturl, refererurl)
        #log(re.sub("<", "&lt;", tabletext))
        refererurl = nexturl
        #break
    return nrecords, npages



# iterate through day by day
day = datetime.date.today()
# all of 2008-2006 done 
# 
#day = datetime.date(2005, 7, 6)  # run back to 7/17
for i in range(30):
    sday = day.strftime("%d/%m/%Y")
    pday = None # scraperwiki.page_cache.getpagebyname(sday)
    if not pday:
        nrecords, npages = ScrapePlanningApplications(day, 0)
        pday =  "%d %d" % (nrecords, npages)
        log("Scraped %d from %s" % (nrecords, sday))
        #scraperwiki.page_cache.savepage("dayrec", sday, pday)
    else:
        log("skipping %s %s" % (sday, pday))
    day = day - datetime.timedelta(days=1)

        



