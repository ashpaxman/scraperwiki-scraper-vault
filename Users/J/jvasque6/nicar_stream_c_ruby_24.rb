require 'scraperwiki'
require 'open-uri'
require 'nokogiri'

download = open('http://www.dol.gov/olms/regs/compliance/cba/Cba_CaCn.htm')
html = Nokogiri::HTML(download)
tables = html.search('table')
table = tables[2]

trs = table.search('tr')
puts trs[6]
require 'scraperwiki'
require 'open-uri'
require 'nokogiri'

download = open('http://www.dol.gov/olms/regs/compliance/cba/Cba_CaCn.htm')
html = Nokogiri::HTML(download)
tables = html.search('table')
table = tables[2]

trs = table.search('tr')
puts trs[6]
