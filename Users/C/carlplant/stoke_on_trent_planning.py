import scraperwiki
from datetime import date

# London Planning Applications

scrape_lib = scraperwiki.utils.swimport("pa_scraper_library")

#LINE BELOW COMMENTED OUT AND REPLACED
REGION = 'Stoke on Trent'
REGION = ['Stoke on Trent']
DB_START = 65 # default date (in YYYY-MM-DD format) to scrape from (or a number if you want it to start x days ago)
DB_END = 0 # default date (in YYYY-MM-DD format) to scrape to (or a number if you want it to stop x days ago)
MAX_PER_SESSION = 100 # maximum records to get in one go from one authority
NUM_PER_DAY = 10

def daily_schedule(day_num = -1):
    if day_num < 0:
        day_num = date.today().weekday()
    if day_num >= 6: # on Sunday
        scrape_lib.do_cleanup()
        return
    auth_list = scrape_lib.get_auths(REGION)
    auth_list = sorted(auth_list, cmp=lambda x,y: cmp(x.get('last_date'),y.get('last_date'))) # sort by most recent application date
    for i in range(0, min(NUM_PER_DAY, len(auth_list))):
        scrape_lib.gather_applications(auth_list[i], DB_START, DB_END, MAX_PER_SESSION)
    print "Completed daily update for "+date.today().strftime('%A')

            
# uncomment this to refresh the authorities list completely
# this is the nuclear option which means all data gets gathered again from DB_START
#scraperwiki.sqlite.execute("drop table if exists authorities")
#scraperwiki.sqlite.commit()

# uncomment this to start again on any single authority
#scrape_lib.restart_authority('Epping Forest')
# uncomment this to clear any single authority
#scrape_lib.remove_authority('Epping Forest')

#uncomment these lines to to do a short test scrape on one authority
auth_list = scrape_lib.get_auths(['Stoke on Trent']) # NB simple string is a region, list is a list of authorities
for auth in auth_list:
    scrape_lib.gather_applications(auth, DB_START, DB_END, 50, 240)

# uncomment this to activate the daily scraping schedule
daily_schedule()

# show table types
tables = scraperwiki.sqlite.show_tables()
print tables['authorities']
print tables['applications']
info = scraperwiki.sqlite.table_info(name="applications")
for column in info:
    print column['name'], column['type']



import scraperwiki
from datetime import date

# London Planning Applications

scrape_lib = scraperwiki.utils.swimport("pa_scraper_library")

#LINE BELOW COMMENTED OUT AND REPLACED
REGION = 'Stoke on Trent'
REGION = ['Stoke on Trent']
DB_START = 65 # default date (in YYYY-MM-DD format) to scrape from (or a number if you want it to start x days ago)
DB_END = 0 # default date (in YYYY-MM-DD format) to scrape to (or a number if you want it to stop x days ago)
MAX_PER_SESSION = 100 # maximum records to get in one go from one authority
NUM_PER_DAY = 10

def daily_schedule(day_num = -1):
    if day_num < 0:
        day_num = date.today().weekday()
    if day_num >= 6: # on Sunday
        scrape_lib.do_cleanup()
        return
    auth_list = scrape_lib.get_auths(REGION)
    auth_list = sorted(auth_list, cmp=lambda x,y: cmp(x.get('last_date'),y.get('last_date'))) # sort by most recent application date
    for i in range(0, min(NUM_PER_DAY, len(auth_list))):
        scrape_lib.gather_applications(auth_list[i], DB_START, DB_END, MAX_PER_SESSION)
    print "Completed daily update for "+date.today().strftime('%A')

            
# uncomment this to refresh the authorities list completely
# this is the nuclear option which means all data gets gathered again from DB_START
#scraperwiki.sqlite.execute("drop table if exists authorities")
#scraperwiki.sqlite.commit()

# uncomment this to start again on any single authority
#scrape_lib.restart_authority('Epping Forest')
# uncomment this to clear any single authority
#scrape_lib.remove_authority('Epping Forest')

#uncomment these lines to to do a short test scrape on one authority
auth_list = scrape_lib.get_auths(['Stoke on Trent']) # NB simple string is a region, list is a list of authorities
for auth in auth_list:
    scrape_lib.gather_applications(auth, DB_START, DB_END, 50, 240)

# uncomment this to activate the daily scraping schedule
daily_schedule()

# show table types
tables = scraperwiki.sqlite.show_tables()
print tables['authorities']
print tables['applications']
info = scraperwiki.sqlite.table_info(name="applications")
for column in info:
    print column['name'], column['type']



