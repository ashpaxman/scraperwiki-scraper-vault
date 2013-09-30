# This scraper extracts detailed standards information from the ISB Standards Library

import scraperwiki
import lxml.html

# Attach to main ISB Standards Library list
scraperwiki.sqlite.attach('isb_standards_library')

# Fetch list of all current standards
summary_data = scraperwiki.sqlite.select('* from isb_standards_library.swdata')

# Assemble the HTML to be inserted into the template

for d in summary_data:
    # Get some basic data for this standard
    standard_number = d['standard_number']
    # Establish the data dict to be saved for each item in summary_data
    data_to_save = {
        'standard_number': standard_number,
    }
    # Get the URL of the full standard data and scrape it
    release_url = d['standard_link']
    doc = lxml.html.parse(release_url).getroot()
    # Each page has several tables on it
    doc_tables = doc.cssselect('table[class="listing"]')
    # The first table has most of the useful info
    standard_details_table = doc_tables[0]
    # The first table has headings in the first column inside a th element
    # and the associated data in an adjacent td element. It always
    # follows the same format for each standard, so we don't need
    # to loop over it.
    table_rows = standard_details_table.cssselect('tr')
    for tr in table_rows:
        # Field name
        field_name = tr.cssselect('th')[0].text
        if field_name in ['Description', 'Applies To']:
            field_value = tr.cssselect('td')[0].text_content()
        else:
            field_value = tr.cssselect('td')[0].text
        # Augment data_to_save with the data we just got
        data_to_save[field_name] = field_value
        # Save the scraped data
    scraperwiki.sqlite.save(unique_keys=['standard_number'], data=data_to_save)
    

# This scraper extracts detailed standards information from the ISB Standards Library

import scraperwiki
import lxml.html

# Attach to main ISB Standards Library list
scraperwiki.sqlite.attach('isb_standards_library')

# Fetch list of all current standards
summary_data = scraperwiki.sqlite.select('* from isb_standards_library.swdata')

# Assemble the HTML to be inserted into the template

for d in summary_data:
    # Get some basic data for this standard
    standard_number = d['standard_number']
    # Establish the data dict to be saved for each item in summary_data
    data_to_save = {
        'standard_number': standard_number,
    }
    # Get the URL of the full standard data and scrape it
    release_url = d['standard_link']
    doc = lxml.html.parse(release_url).getroot()
    # Each page has several tables on it
    doc_tables = doc.cssselect('table[class="listing"]')
    # The first table has most of the useful info
    standard_details_table = doc_tables[0]
    # The first table has headings in the first column inside a th element
    # and the associated data in an adjacent td element. It always
    # follows the same format for each standard, so we don't need
    # to loop over it.
    table_rows = standard_details_table.cssselect('tr')
    for tr in table_rows:
        # Field name
        field_name = tr.cssselect('th')[0].text
        if field_name in ['Description', 'Applies To']:
            field_value = tr.cssselect('td')[0].text_content()
        else:
            field_value = tr.cssselect('td')[0].text
        # Augment data_to_save with the data we just got
        data_to_save[field_name] = field_value
        # Save the scraped data
    scraperwiki.sqlite.save(unique_keys=['standard_number'], data=data_to_save)
    

