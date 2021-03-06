# Blank Ruby

html = ScraperWiki::scrape("http://web.archive.org/web/20110514112442/http://unstats.un.org/unsd/demographic/products/socind/education.htm")
p html

require 'nokogiri'
doc = Nokogiri::HTML html
doc.search("div[@align='left'] tr").each do |v|
  cells = v.search 'td'
  if cells.count == 12
    data = {
      country: cells[0].inner_html,
      yearsofschooling: cells[7].inner_html.to_i
    }
    ScraperWiki::save_sqlite(['country'], data)
  end
end


    ScraperWiki::save_sqlite(['country'], data)

