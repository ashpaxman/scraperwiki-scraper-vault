# Blank Python
# Name: Sandeep Moola Number:1020028
import scraperwiki
from BeautifulSoup import BeautifulSoup

print "Football"

HtmlPage = scraperwiki.scrape('http://en.wikipedia.org/wiki/List_of_football_clubs_in_England')
WebPageSource = BeautifulSoup(HtmlPage)
scraperwiki.metadata.save('data_columns', [ 'Teams','Leagues' ]) 
TableDetails = WebPageSource.find("table", { "class" : "wikitable" })
TableRows = TableDetails.findAll("tr")
print "Total Records in the Dictionary are:--",TableRows
for TableRow in TableRows:
        Details = {}
        TableColumns = TableRow.findAll("td")
        if TableColumns:
            Details['Teams'] = TableColumns[0].text  
            Details['Leagues'] = TableColumns[1].text     
            scraperwiki.datastore.save(["Teams"], Details)     
            print Details
# Blank Python
# Name: Sandeep Moola Number:1020028
import scraperwiki
from BeautifulSoup import BeautifulSoup

print "Football"

HtmlPage = scraperwiki.scrape('http://en.wikipedia.org/wiki/List_of_football_clubs_in_England')
WebPageSource = BeautifulSoup(HtmlPage)
scraperwiki.metadata.save('data_columns', [ 'Teams','Leagues' ]) 
TableDetails = WebPageSource.find("table", { "class" : "wikitable" })
TableRows = TableDetails.findAll("tr")
print "Total Records in the Dictionary are:--",TableRows
for TableRow in TableRows:
        Details = {}
        TableColumns = TableRow.findAll("td")
        if TableColumns:
            Details['Teams'] = TableColumns[0].text  
            Details['Leagues'] = TableColumns[1].text     
            scraperwiki.datastore.save(["Teams"], Details)     
            print Details
