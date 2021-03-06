###############################################################################
# START HERE: Tutorial 3: More advanced scraping. Shows how to follow 'next' 
# links from page to page: use functions, so you can call the same code 
# repeatedly. SCROLL TO THE BOTTOM TO SEE THE START OF THE SCRAPER.
###############################################################################
require 'nokogiri'
require 'open-uri'

BASE_URL = 'http://www.lacentrale.fr/listing_auto.php?SS_CATEGORIE=45%2C46&marque=LOTUS&modele=EXIGE&prix_mini=&prix_maxi=&energie=&annee=&km_maxi=&annee2=&conso=&co2=&opt=&version=&transmission=&couleur=&nbportes=&photo=&new_annonce=&cp=&origine='

# define the order our columns are displayed in the datastore
ScraperWiki.save_var('data_columns', ['ID','model','power', 'version', 'price', 'mileage','year'])

# scrape_table function: gets passed an individual page to scrape
def scrape_table(page)
  i=0
  data_table = page.css('table#TabAnn').collect do |row|
  while (i<19) 
    i=i+1
    sel="tr#ul_"+"#{i}"
    selv="tr#ul_"+"#{i}b"
    record = {}
    record ['model'] = 'Lotus Exige'
    record['version'] = row.css(selv).css('td.lcversion').inner_text.strip() #gsub(/\s/,'')
    record['power'] = record['version'].scan(/[^\s]*(280|260|243|221|192|179)[^@]*/).flatten[0]
    row_data = row.css(sel)
    
    record['mileage']     = row_data.css('td.lcmileage').inner_text.strip().gsub(/\s/,'')
    record['price']  = row_data.css('td.lcprice').inner_text.strip().gsub(/\u20AC/,'').gsub(/\s/,'')
    record['year'] = row_data.css('td.lcyear').inner_text.strip()
    record ['ID'] = record['version'] + record['price']
    # Print out the data we've gathered
    puts record
  end

    # Finally, save the record to the datastore - 'Artist' is our unique key
    #ScraperWiki.save("ID", record)
    ScraperWiki.save_sqlite(unique_keys=["ID"], record)
p ScraperWiki.show_tables()


  end
end

#        scrape_and_look_for_next_link(starting_url)

## scrape_and_look_for_next_link function: calls the scrape_table
# function, then hunts for a 'next' link: if one is found, calls itself again
def scrape_and_look_for_next_link(url)
    page = Nokogiri::HTML(open(url))
    scrape_table(page)
    next_link = page.at_css('a.next')
    if next_link 
      puts next_link
      next_url = BASE_URL + next_link['href']
      puts next_url
      scrape_and_look_for_next_link(next_url)
    end
end

# ---------------------------------------------------------------------------
# START HERE - define your starting URL - then 
# call a function to scrape the first page in the series.
# ---------------------------------------------------------------------------
starting_url = BASE_URL #+ 'example_table_1.html'
#scrape_and_look_for_next_link(starting_url)
scrape_table(Nokogiri::HTML(open(starting_url)))
###############################################################################
# START HERE: Tutorial 3: More advanced scraping. Shows how to follow 'next' 
# links from page to page: use functions, so you can call the same code 
# repeatedly. SCROLL TO THE BOTTOM TO SEE THE START OF THE SCRAPER.
###############################################################################
require 'nokogiri'
require 'open-uri'

BASE_URL = 'http://www.lacentrale.fr/listing_auto.php?SS_CATEGORIE=45%2C46&marque=LOTUS&modele=EXIGE&prix_mini=&prix_maxi=&energie=&annee=&km_maxi=&annee2=&conso=&co2=&opt=&version=&transmission=&couleur=&nbportes=&photo=&new_annonce=&cp=&origine='

# define the order our columns are displayed in the datastore
ScraperWiki.save_var('data_columns', ['ID','model','power', 'version', 'price', 'mileage','year'])

# scrape_table function: gets passed an individual page to scrape
def scrape_table(page)
  i=0
  data_table = page.css('table#TabAnn').collect do |row|
  while (i<19) 
    i=i+1
    sel="tr#ul_"+"#{i}"
    selv="tr#ul_"+"#{i}b"
    record = {}
    record ['model'] = 'Lotus Exige'
    record['version'] = row.css(selv).css('td.lcversion').inner_text.strip() #gsub(/\s/,'')
    record['power'] = record['version'].scan(/[^\s]*(280|260|243|221|192|179)[^@]*/).flatten[0]
    row_data = row.css(sel)
    
    record['mileage']     = row_data.css('td.lcmileage').inner_text.strip().gsub(/\s/,'')
    record['price']  = row_data.css('td.lcprice').inner_text.strip().gsub(/\u20AC/,'').gsub(/\s/,'')
    record['year'] = row_data.css('td.lcyear').inner_text.strip()
    record ['ID'] = record['version'] + record['price']
    # Print out the data we've gathered
    puts record
  end

    # Finally, save the record to the datastore - 'Artist' is our unique key
    #ScraperWiki.save("ID", record)
    ScraperWiki.save_sqlite(unique_keys=["ID"], record)
p ScraperWiki.show_tables()


  end
end

#        scrape_and_look_for_next_link(starting_url)

## scrape_and_look_for_next_link function: calls the scrape_table
# function, then hunts for a 'next' link: if one is found, calls itself again
def scrape_and_look_for_next_link(url)
    page = Nokogiri::HTML(open(url))
    scrape_table(page)
    next_link = page.at_css('a.next')
    if next_link 
      puts next_link
      next_url = BASE_URL + next_link['href']
      puts next_url
      scrape_and_look_for_next_link(next_url)
    end
end

# ---------------------------------------------------------------------------
# START HERE - define your starting URL - then 
# call a function to scrape the first page in the series.
# ---------------------------------------------------------------------------
starting_url = BASE_URL #+ 'example_table_1.html'
#scrape_and_look_for_next_link(starting_url)
scrape_table(Nokogiri::HTML(open(starting_url)))
