###############################################################################
# START HERE: Tutorial 3: More advanced scraping. Shows how to follow 'next'
# links from page to page: use functions, so you can call the same code
# repeatedly. SCROLL TO THE BOTTOM TO SEE THE START OF THE SCRAPER.
###############################################################################
  
import scraperwiki
import re

from BeautifulSoup import BeautifulSoup
  
urls = {}

  
  
# define the order our columns are displayed in the datastore
scraperwiki.metadata.save('data_columns', ['Code','Title','Broader','BroaderTransitive','Related'])
  
#defines the next url to be passed
def next_url():
    for url in urls:
        next_url = base_url + url
        print next_url
        scrape_and_look_for_next_link(next_url)
          

# scrape_table function: gets passed an individual page to scrape
def scrape_table(soup):
    if(soup.find("table", { "class" : "results" })):
        data_table = soup.find("table", { "class" : "results" })
        rows = data_table.findAll("tr", { "class" : "current" })
        broader=rows[0].find("td").text

        for row in rows:
            # Set up our data record - we'll need it later
            record = {}
            table_cells = row.findAll("td")
            if(table_cells[1].find("a")):
                url=table_cells[1].find("a").get('href')
            elif(table_cells[0].find("a")):
                url=table_cells[0].find("a").get('href')
            flag=0
            for x in urls:
                if (url == x):
                    flag=1
                    break
            if (flag==0):
                urls.append(url)
            title=table_cells[3].text
            if (re.search("See also", title)):
                t= re.search("\[See also", title)
                ts=title[:t.start()]
                title=ts 
                tehs = {}
                tehref=table_cells[3].findAll("a")
                
                for index, teh in enumerate(tehref):
                    tehs[index] = teh.text
                
                out = []
                for object in tehs:                  
                    out.append(object)
                print tehs
                record['Related']=tehs
            #print t.group(3)
            if (table_cells[2].text):
                c = table_cells[2].text
                code=c[0:5]  
                record['Code']=code
                b=rows[1].findAll("td")
                br=b[1].text
                if(br):
                    broader=br
                    broaderTransitive=rows[0].find("td").text
                    record['Broader']=broader
                    record['BroaderTransitive'] = broaderTransitive
                else:
                    broader=rows[0].find("td").text
                    print "1.", code, "2.", title, "3.", broader,                          
            elif (table_cells[1].text):
                c = table_cells[1].text
                code=c[0:5]
                broader=rows[0].find("td").text
                print code, title, broader
            elif (table_cells[0].text):
                c = table_cells[0].text
                code=c[0:5]
            record['Code'] = code
            record['Title'] = title
            record['Broader'] = broader
            print record
            scraperwiki.datastore.save(["Code"], record)


def scrape_and_look_for_next_link(url):
    html = scraperwiki.scrape(url)
    soup = BeautifulSoup(html)
    scrape_table(soup)

  
# ---------------------------------------------------------------------------
# START HERE: define your starting URL - then
# call a function to scrape the first page in the series.
# ---------------------------------------------------------------------------
base_url = 'http://www.ams.org/mathscinet/msc/'
Pages=["01", "03", "05", "06", "08", "11", "12", "13", "14", "15", "16",  "17",  "18", "19", "20", "22", "26", "28", "30", "31", "32", "33", "34", "35", "37", "39", "40", "41", "42",  "43", "44", "45", "46", "47", "49", "51", "52", "53", "54", "55", "57", "58", "60", "62", "65", "68", "70", "74", "76", "78", "80", "81", "82", "83", "85", "86", "90", "91", "92", "93", "94", "97"]

starting_url = "msc2010.html?t=00-XX&s=&btn=Search&ls=Ct"
urls = [starting_url]
for page in Pages:
    print page
    url="msc2010.html?t="+page+"-XX&s=&btn=Search&ls=Ct"
    urls.append(url)
next_url()


###############################################################################
# START HERE: Tutorial 3: More advanced scraping. Shows how to follow 'next'
# links from page to page: use functions, so you can call the same code
# repeatedly. SCROLL TO THE BOTTOM TO SEE THE START OF THE SCRAPER.
###############################################################################
  
import scraperwiki
import re

from BeautifulSoup import BeautifulSoup
  
urls = {}

  
  
# define the order our columns are displayed in the datastore
scraperwiki.metadata.save('data_columns', ['Code','Title','Broader','BroaderTransitive','Related'])
  
#defines the next url to be passed
def next_url():
    for url in urls:
        next_url = base_url + url
        print next_url
        scrape_and_look_for_next_link(next_url)
          

# scrape_table function: gets passed an individual page to scrape
def scrape_table(soup):
    if(soup.find("table", { "class" : "results" })):
        data_table = soup.find("table", { "class" : "results" })
        rows = data_table.findAll("tr", { "class" : "current" })
        broader=rows[0].find("td").text

        for row in rows:
            # Set up our data record - we'll need it later
            record = {}
            table_cells = row.findAll("td")
            if(table_cells[1].find("a")):
                url=table_cells[1].find("a").get('href')
            elif(table_cells[0].find("a")):
                url=table_cells[0].find("a").get('href')
            flag=0
            for x in urls:
                if (url == x):
                    flag=1
                    break
            if (flag==0):
                urls.append(url)
            title=table_cells[3].text
            if (re.search("See also", title)):
                t= re.search("\[See also", title)
                ts=title[:t.start()]
                title=ts 
                tehs = {}
                tehref=table_cells[3].findAll("a")
                
                for index, teh in enumerate(tehref):
                    tehs[index] = teh.text
                
                out = []
                for object in tehs:                  
                    out.append(object)
                print tehs
                record['Related']=tehs
            #print t.group(3)
            if (table_cells[2].text):
                c = table_cells[2].text
                code=c[0:5]  
                record['Code']=code
                b=rows[1].findAll("td")
                br=b[1].text
                if(br):
                    broader=br
                    broaderTransitive=rows[0].find("td").text
                    record['Broader']=broader
                    record['BroaderTransitive'] = broaderTransitive
                else:
                    broader=rows[0].find("td").text
                    print "1.", code, "2.", title, "3.", broader,                          
            elif (table_cells[1].text):
                c = table_cells[1].text
                code=c[0:5]
                broader=rows[0].find("td").text
                print code, title, broader
            elif (table_cells[0].text):
                c = table_cells[0].text
                code=c[0:5]
            record['Code'] = code
            record['Title'] = title
            record['Broader'] = broader
            print record
            scraperwiki.datastore.save(["Code"], record)


def scrape_and_look_for_next_link(url):
    html = scraperwiki.scrape(url)
    soup = BeautifulSoup(html)
    scrape_table(soup)

  
# ---------------------------------------------------------------------------
# START HERE: define your starting URL - then
# call a function to scrape the first page in the series.
# ---------------------------------------------------------------------------
base_url = 'http://www.ams.org/mathscinet/msc/'
Pages=["01", "03", "05", "06", "08", "11", "12", "13", "14", "15", "16",  "17",  "18", "19", "20", "22", "26", "28", "30", "31", "32", "33", "34", "35", "37", "39", "40", "41", "42",  "43", "44", "45", "46", "47", "49", "51", "52", "53", "54", "55", "57", "58", "60", "62", "65", "68", "70", "74", "76", "78", "80", "81", "82", "83", "85", "86", "90", "91", "92", "93", "94", "97"]

starting_url = "msc2010.html?t=00-XX&s=&btn=Search&ls=Ct"
urls = [starting_url]
for page in Pages:
    print page
    url="msc2010.html?t="+page+"-XX&s=&btn=Search&ls=Ct"
    urls.append(url)
next_url()


