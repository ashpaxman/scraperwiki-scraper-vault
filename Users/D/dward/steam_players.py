import scraperwiki
from lxml import etree

def saveToStore(data):
    scraperwiki.sqlite.execute("CREATE TABLE IF NOT EXISTS steam_players ('ID' string, 'Location' string, 'Joined_Date' string, PRIMARY KEY('ID'))")
    scraperwiki.sqlite.execute("INSERT OR REPLACE INTO steam_players ('ID', 'Location', 'Joined_Date') VALUES (?, ?, ?)", (data['ID'], data['Location'], data['Joined_Date']))
    scraperwiki.sqlite.commit()

def scrape(url):
    try:
        tree = etree.parse(url + "?xml=1")
        id = tree.xpath('/profile/steamID64')[0].text
        location = ''
        joined_date = ''
        if len(tree.xpath('/profile/location')) == 1:
            location = tree.xpath('/profile/location')[0].text
        if len(tree.xpath('/profile/memberSince')) == 1:
            joined_date = tree.xpath('/profile/memberSince')[0].text
        data = {
            'ID'          : id,
            'Location'    : location,
            'Joined_Date' : joined_date
        }
        saveToStore(data)
        return 1
    except Exception, err:
        return 0

def start():
    scraperwiki.sqlite.attach("get_steam_user_profile_pages", "src")
    results = scraperwiki.sqlite.select("URL from src.userpages order by UserName DESC")
    for row in results:
        scrape(row['URL'])

start()import scraperwiki
from lxml import etree

def saveToStore(data):
    scraperwiki.sqlite.execute("CREATE TABLE IF NOT EXISTS steam_players ('ID' string, 'Location' string, 'Joined_Date' string, PRIMARY KEY('ID'))")
    scraperwiki.sqlite.execute("INSERT OR REPLACE INTO steam_players ('ID', 'Location', 'Joined_Date') VALUES (?, ?, ?)", (data['ID'], data['Location'], data['Joined_Date']))
    scraperwiki.sqlite.commit()

def scrape(url):
    try:
        tree = etree.parse(url + "?xml=1")
        id = tree.xpath('/profile/steamID64')[0].text
        location = ''
        joined_date = ''
        if len(tree.xpath('/profile/location')) == 1:
            location = tree.xpath('/profile/location')[0].text
        if len(tree.xpath('/profile/memberSince')) == 1:
            joined_date = tree.xpath('/profile/memberSince')[0].text
        data = {
            'ID'          : id,
            'Location'    : location,
            'Joined_Date' : joined_date
        }
        saveToStore(data)
        return 1
    except Exception, err:
        return 0

def start():
    scraperwiki.sqlite.attach("get_steam_user_profile_pages", "src")
    results = scraperwiki.sqlite.select("URL from src.userpages order by UserName DESC")
    for row in results:
        scrape(row['URL'])

start()