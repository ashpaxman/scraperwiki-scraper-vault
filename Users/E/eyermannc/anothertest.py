import scraperwiki
wikipedia_utils = scraperwiki.swimport("wikipedia_utils")

title = "Aquamole Pot"

if KeyError:
    pass 

val = wikipedia_utils.GetWikipediaPage(title)
res = wikipedia_utils.ParseTemplates(val["text"])
print res               # prints everything we have found in the text
infobox_ukcave = dict(res["templates"]).get("Infobox ukcave")
print infobox_ukcave    # prints just the ukcave infobox

lcavepages = wikipedia_utils.GetWikipediaCategoryRecurse("Analgesics")
scraperwiki.sqlite.save(["title"], lcavepages, "cavepages")

import scraperwiki
wikipedia_utils = scraperwiki.swimport("wikipedia_utils")

title = "Aquamole Pot"

if KeyError:
    pass 

val = wikipedia_utils.GetWikipediaPage(title)
res = wikipedia_utils.ParseTemplates(val["text"])
print res               # prints everything we have found in the text
infobox_ukcave = dict(res["templates"]).get("Infobox ukcave")
print infobox_ukcave    # prints just the ukcave infobox

lcavepages = wikipedia_utils.GetWikipediaCategoryRecurse("Analgesics")
scraperwiki.sqlite.save(["title"], lcavepages, "cavepages")

