#This is the first pass at a scraper of Excel files. 
#Currently it scrapes the first sheet of one spreadsheet, identified by URL
#NEED TO ADD: 
#All sheets - keys grabbed from header row
#More than one spreadsheet, linked from one URL

#useful guides at:
#https://scraperwiki.com/docs/python/python_excel_guide/
#http://blog.scraperwiki.com/2011/09/14/scraping-guides-excel-spreadsheets/
#https://scraperwiki.com/docs/python/tutorials/

#import scraperwiki library 
import scraperwiki

#import xlrd library - documentation at https://secure.simplistix.co.uk/svn/xlrd/trunk/xlrd/doc/xlrd.html
import xlrd

#URL = 'http://transparency.dh.gov.uk/2012/10/26/winter-pressures-daily-situation-reports-2012-13/'

#set a variable for the spreadsheet location
XLS = 'http://tna.europarchive.org/20110116113217/http://www.food.gov.uk/multimedia/spreadsheets/cofids.xls'

#use the scrape function on that spreadsheet to create a new variable
xlbin = scraperwiki.scrape(XLS)
#use the open_workbook function on that new variable to create another
book = xlrd.open_workbook(file_contents=xlbin)

#use the sheet_by_index method to open the 15th (14) sheet in variable 'book' - and put it into new variable 'sheet'
sheet = book.sheet_by_index(14)

#use the row_values method and index (0) to grab the first row of 'sheet', and put all cells into the list variable 'title'
title = sheet.row_values(0)
#print the string "Title:", followed by the second item (column) in the variable 'title' 
print "Title:", title[1]

#put cells from the first row into 'keys' variable 
keys = sheet.row_values(0)
record = {}

#loop through a range - from the 3rd item (2) to a number generated by using the .nrows method on 'sheet' (to find number of rows in that sheet)
#put each row number in 'rownumber' as you loop
for rownumber in range(2, sheet.nrows):
    print rownumber
    record['Food_Code'] = sheet.row_values(rownumber)[0]
    record['Name'] = sheet.row_values(rownumber)[1]
    record['EnergyK_cal'] = sheet.row_values(rownumber)[8]
    record['Protein'] = sheet.row_values(rownumber)[10]
    record['Carbs'] = sheet.row_values(rownumber)[11]
    record['Total_sugar'] = sheet.row_values(rownumber)[12]
    record['Starch'] = sheet.row_values(rownumber)[13]
    
    #print "---", record
    scraperwiki.datastore.save(["Name"], record)
    

#This is the first pass at a scraper of Excel files. 
#Currently it scrapes the first sheet of one spreadsheet, identified by URL
#NEED TO ADD: 
#All sheets - keys grabbed from header row
#More than one spreadsheet, linked from one URL

#useful guides at:
#https://scraperwiki.com/docs/python/python_excel_guide/
#http://blog.scraperwiki.com/2011/09/14/scraping-guides-excel-spreadsheets/
#https://scraperwiki.com/docs/python/tutorials/

#import scraperwiki library 
import scraperwiki

#import xlrd library - documentation at https://secure.simplistix.co.uk/svn/xlrd/trunk/xlrd/doc/xlrd.html
import xlrd

#URL = 'http://transparency.dh.gov.uk/2012/10/26/winter-pressures-daily-situation-reports-2012-13/'

#set a variable for the spreadsheet location
XLS = 'http://tna.europarchive.org/20110116113217/http://www.food.gov.uk/multimedia/spreadsheets/cofids.xls'

#use the scrape function on that spreadsheet to create a new variable
xlbin = scraperwiki.scrape(XLS)
#use the open_workbook function on that new variable to create another
book = xlrd.open_workbook(file_contents=xlbin)

#use the sheet_by_index method to open the 15th (14) sheet in variable 'book' - and put it into new variable 'sheet'
sheet = book.sheet_by_index(14)

#use the row_values method and index (0) to grab the first row of 'sheet', and put all cells into the list variable 'title'
title = sheet.row_values(0)
#print the string "Title:", followed by the second item (column) in the variable 'title' 
print "Title:", title[1]

#put cells from the first row into 'keys' variable 
keys = sheet.row_values(0)
record = {}

#loop through a range - from the 3rd item (2) to a number generated by using the .nrows method on 'sheet' (to find number of rows in that sheet)
#put each row number in 'rownumber' as you loop
for rownumber in range(2, sheet.nrows):
    print rownumber
    record['Food_Code'] = sheet.row_values(rownumber)[0]
    record['Name'] = sheet.row_values(rownumber)[1]
    record['EnergyK_cal'] = sheet.row_values(rownumber)[8]
    record['Protein'] = sheet.row_values(rownumber)[10]
    record['Carbs'] = sheet.row_values(rownumber)[11]
    record['Total_sugar'] = sheet.row_values(rownumber)[12]
    record['Starch'] = sheet.row_values(rownumber)[13]
    
    #print "---", record
    scraperwiki.datastore.save(["Name"], record)
    

