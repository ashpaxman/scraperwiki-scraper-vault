require 'nokogiri'
require 'uri'
require 'open-uri'

base_url = "http://gtr.rcuk.ac.uk:80/project/"
files = ["28E6E7DE-26C6-4904-BF14-F1C23FAEEEFE","DFC465CA-50EC-41F8-B6C0-5CD0948446B8","6015B1B9-A5EA-445F-99C6-BA1BC4960AF1","BE199C09-3D21-4291-B2CF-EEE9140F9DA0","DF6DA0F2-20F4-4811-8AF6-11A5FEA856D9","80877CD6-6D92-491B-88C8-2B921278C511","93EE9E98-9A06-4A19-9FEB-361753260C64","101BA5C6-6A58-410F-9D37-877D248186F2","0806A6A6-4282-4616-BCEA-FBB1ADCBF8FB","30353109-C45A-4A95-BE0B-996ADD799E88","31B3F9BD-B905-44A9-A9F5-6537A2B3664A","4B0ADC38-AE20-45EE-98D1-B8D31F02FC7F","5274095A-6965-4895-8D56-595BF65DFA2B","6EBD6295-576B-4940-A759-D7991270735C","84542516-B687-4F5B-98A3-16FC5826A6B1","9674061F-ED7F-4B87-A832-F95DA03AF304","A214D68F-CEEB-4E29-8B24-57C69C9BB43F","CC8726CC-3BC9-41BE-9A45-1D0063038804","F9D92013-8918-4C3D-8DBD-2F1721FB177B","11AC2E4F-235A-44D0-B209-54CCE8FE73B3","7D6035EE-6039-4F08-96DF-2CDB5EEF9F89","70B943A5-4BDF-4AC7-AEF1-4FC8EB6BCA25","D8286EF7-6884-4C54-A037-6DBB3B7E5615","1161415A-D5C3-4EEE-B7C4-21375ED92723","17CDC5D2-E8D5-409B-8E7C-C43128393FB4","1D22DDBA-ED79-4326-975C-5FE036E90224","3C707F52-BEA6-4B9F-85CD-A43C774F92E7","3D1DF59C-B44B-4407-A277-1A99A56D3B42","454AB4C8-43E5-482E-991F-0164C710F86D","576005FF-6952-44D9-8404-40AD4E13008E","76C24E0A-49BA-4DA2-88B8-C796BFF1D13E","AE69E9E2-555E-445D-A6BF-F5FBDCD485EF","AE25B6D4-3CA6-4934-AD95-1C1A32A3E1B7","40C45963-AB71-4608-A0E8-9AB744566FA6","1C889FB1-153A-4089-9B06-6861DF0758F4"]

files.each do |file|
  url = base_url + file + ".xml"
  page = Nokogiri::XML(open(url))

  page.xpath('/gtr:projectOverview/gtr:projectComposition/gtr:project/gtr:publications/gtr:publication').each do |project|
    t = project.xpath('gtr:title').inner_text
    a = project.xpath('gtr:abstractText').inner_text
    i = project.xpath('gtr:id').inner_text
    p = project.xpath('gtr:publications').inner_text
    ScraperWiki::save_sqlite(['id'], {"id" => i, "title" => t, "abstract" => a, "publications" => p})
  end
end
require 'nokogiri'
require 'uri'
require 'open-uri'

base_url = "http://gtr.rcuk.ac.uk:80/project/"
files = ["28E6E7DE-26C6-4904-BF14-F1C23FAEEEFE","DFC465CA-50EC-41F8-B6C0-5CD0948446B8","6015B1B9-A5EA-445F-99C6-BA1BC4960AF1","BE199C09-3D21-4291-B2CF-EEE9140F9DA0","DF6DA0F2-20F4-4811-8AF6-11A5FEA856D9","80877CD6-6D92-491B-88C8-2B921278C511","93EE9E98-9A06-4A19-9FEB-361753260C64","101BA5C6-6A58-410F-9D37-877D248186F2","0806A6A6-4282-4616-BCEA-FBB1ADCBF8FB","30353109-C45A-4A95-BE0B-996ADD799E88","31B3F9BD-B905-44A9-A9F5-6537A2B3664A","4B0ADC38-AE20-45EE-98D1-B8D31F02FC7F","5274095A-6965-4895-8D56-595BF65DFA2B","6EBD6295-576B-4940-A759-D7991270735C","84542516-B687-4F5B-98A3-16FC5826A6B1","9674061F-ED7F-4B87-A832-F95DA03AF304","A214D68F-CEEB-4E29-8B24-57C69C9BB43F","CC8726CC-3BC9-41BE-9A45-1D0063038804","F9D92013-8918-4C3D-8DBD-2F1721FB177B","11AC2E4F-235A-44D0-B209-54CCE8FE73B3","7D6035EE-6039-4F08-96DF-2CDB5EEF9F89","70B943A5-4BDF-4AC7-AEF1-4FC8EB6BCA25","D8286EF7-6884-4C54-A037-6DBB3B7E5615","1161415A-D5C3-4EEE-B7C4-21375ED92723","17CDC5D2-E8D5-409B-8E7C-C43128393FB4","1D22DDBA-ED79-4326-975C-5FE036E90224","3C707F52-BEA6-4B9F-85CD-A43C774F92E7","3D1DF59C-B44B-4407-A277-1A99A56D3B42","454AB4C8-43E5-482E-991F-0164C710F86D","576005FF-6952-44D9-8404-40AD4E13008E","76C24E0A-49BA-4DA2-88B8-C796BFF1D13E","AE69E9E2-555E-445D-A6BF-F5FBDCD485EF","AE25B6D4-3CA6-4934-AD95-1C1A32A3E1B7","40C45963-AB71-4608-A0E8-9AB744566FA6","1C889FB1-153A-4089-9B06-6861DF0758F4"]

files.each do |file|
  url = base_url + file + ".xml"
  page = Nokogiri::XML(open(url))

  page.xpath('/gtr:projectOverview/gtr:projectComposition/gtr:project/gtr:publications/gtr:publication').each do |project|
    t = project.xpath('gtr:title').inner_text
    a = project.xpath('gtr:abstractText').inner_text
    i = project.xpath('gtr:id').inner_text
    p = project.xpath('gtr:publications').inner_text
    ScraperWiki::save_sqlite(['id'], {"id" => i, "title" => t, "abstract" => a, "publications" => p})
  end
end
