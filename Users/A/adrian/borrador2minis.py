import scraperwiki
import urlparse
import lxml.html

# scrape_table function: gets passed an individual page to scrape
def scrape_divs(url):
    html = scraperwiki.scrape(url)
    print html
    root = lxml.html.fromstring(html)
#MAY BE BETTER TO USE     rows = root.cssselect("article div")  
#ALSO CAN THEN ADD alltext = row[0].text_content()
    #line below selects all <div class="block size3of4"> - note that because there is a space in the value of the div class, we need to put it in inverted commas as a string
    rows = root.cssselect("div#info") 
#ERROR generated by line 21 below can be corrected by changing above to rows = root.cssselect("article") or by using if statements below to test presence of h4, etc.
    for row in rows:
        # Set up our data record - we'll need it later
        print row
        record = {}
        #grab all <h4> tags within our <div>
        #inicializa las variables vacias por si no existen
        municipio = ""
        #membertitle = ""
        #memberbiog = ""
        


        h1s = row.cssselect("h1")
       
        #membername = h4s[0].text
#si no hay ninguno agarrar lo primero y ponerlo en membername
        if h1s:
            municipio=h1s[0].text


        record['Municipio'] = municipio
        #record['Title'] = membertitle
        #record['Description'] = memberbiog
        tds = row.cssselect("td")
        if tds:
            nomyApell=tds[1].text_content()
        record['NomYApell'] = nomyApell    
        print record, '------------'
        # Finally, save the record to the datastore - 'Name' is our unique key
#MAY BE WORTH USING A DIFFERENT KEY?
        scraperwiki.sqlite.save(["Municipio"], record)
        
#list of URLs with similar CMS compiled with this advanced search on Google:
#inurl:about-us/board.aspx CCG
#https://www.google.co.uk/search?q=ccg+nhs+uk+board&channel=linkdoctor&safe=on#hl=en&safe=active&sclient=psy-ab&q=inurl:about-us%2Fboard.aspx+CCG&oq=inurl:about-us%2Fboard.aspx+CCG

#ccglist = ['www.brentccg.nhs.uk/', 'www.ealingccg.nhs.uk/', 'www.hounslowccg.nhs.uk/', 'www.westlondonccg.nhs.uk/', 'www.centrallondonccg.nhs.uk/', #'www.harrowccg.nhs.uk/', 'www.hammersmithfulhamccg.nhs.uk/']
#for ccg in ccglist:
scrape_divs('http://www.mininterior.gov.ar/municipios/masinfo.php?municipio=BUE001&idName=municipios&idNameSubMenu=&idNameSubMenuDer=&idNameSubMenuDerNivel2=&idNameSubMenuDerPrincipal=')




import scraperwiki
import urlparse
import lxml.html

# scrape_table function: gets passed an individual page to scrape
def scrape_divs(url):
    html = scraperwiki.scrape(url)
    print html
    root = lxml.html.fromstring(html)
#MAY BE BETTER TO USE     rows = root.cssselect("article div")  
#ALSO CAN THEN ADD alltext = row[0].text_content()
    #line below selects all <div class="block size3of4"> - note that because there is a space in the value of the div class, we need to put it in inverted commas as a string
    rows = root.cssselect("div#info") 
#ERROR generated by line 21 below can be corrected by changing above to rows = root.cssselect("article") or by using if statements below to test presence of h4, etc.
    for row in rows:
        # Set up our data record - we'll need it later
        print row
        record = {}
        #grab all <h4> tags within our <div>
        #inicializa las variables vacias por si no existen
        municipio = ""
        #membertitle = ""
        #memberbiog = ""
        


        h1s = row.cssselect("h1")
       
        #membername = h4s[0].text
#si no hay ninguno agarrar lo primero y ponerlo en membername
        if h1s:
            municipio=h1s[0].text


        record['Municipio'] = municipio
        #record['Title'] = membertitle
        #record['Description'] = memberbiog
        tds = row.cssselect("td")
        if tds:
            nomyApell=tds[1].text_content()
        record['NomYApell'] = nomyApell    
        print record, '------------'
        # Finally, save the record to the datastore - 'Name' is our unique key
#MAY BE WORTH USING A DIFFERENT KEY?
        scraperwiki.sqlite.save(["Municipio"], record)
        
#list of URLs with similar CMS compiled with this advanced search on Google:
#inurl:about-us/board.aspx CCG
#https://www.google.co.uk/search?q=ccg+nhs+uk+board&channel=linkdoctor&safe=on#hl=en&safe=active&sclient=psy-ab&q=inurl:about-us%2Fboard.aspx+CCG&oq=inurl:about-us%2Fboard.aspx+CCG

#ccglist = ['www.brentccg.nhs.uk/', 'www.ealingccg.nhs.uk/', 'www.hounslowccg.nhs.uk/', 'www.westlondonccg.nhs.uk/', 'www.centrallondonccg.nhs.uk/', #'www.harrowccg.nhs.uk/', 'www.hammersmithfulhamccg.nhs.uk/']
#for ccg in ccglist:
scrape_divs('http://www.mininterior.gov.ar/municipios/masinfo.php?municipio=BUE001&idName=municipios&idNameSubMenu=&idNameSubMenuDer=&idNameSubMenuDerNivel2=&idNameSubMenuDerPrincipal=')




