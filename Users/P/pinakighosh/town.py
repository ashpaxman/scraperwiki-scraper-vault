import scraperwiki
import mechanize 
import re
import lxml.html
import sys
import requests
from bs4 import BeautifulSoup

url="http://www.censusindia.gov.in/Census_Data_2001/Census_Data_Online/Area_Profile/Town_Profile.aspx?cki=7H7pnwQvpHZ"
br = mechanize.Browser()
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
state_list=[]
flag=True
sl_no=0
dat=dict()
data_pts=[]
state=''
district=''
error=[]
for i in range(1,35):
    l=[]
    if i <10:
        st='0'+str(i)
        l.append(st)
    else:
        st=str(i)
        l.append(st)
    state_list.append(l)


for i in state_list:
    response = br.open(url)
    VAR1 = response.read() #reads the source file for the web page
    br.select_form("Form1")
    br.set_all_readonly(False)
    d=dict()
    for control in br.form.controls:
        d[control.name]=br[control.name]
    br["__EVENTTARGET"]=d['__EVENTTARGET']
    br["__EVENTARGUMENT"]=d['__EVENTARGUMENT']
    br["__LASTFOCUS"]=d['__LASTFOCUS']
    br["__VIEWSTATE"]=d['__VIEWSTATE']
    br["__EVENTVALIDATION"]=d['__EVENTVALIDATION']
    br["drpState"]=i
    response = br.submit()
    var=response.read()
    soup=BeautifulSoup(var)
    l=[]
    district_list=[]
    for opt in soup.findAll('select',{"name" : "drpDistrict"}):
        for option in opt.findAll('option'):
            #print option.get('value')
            l.append(str(option.get('value')))
            district_list.append(l)
            l=[]
    for j in district_list:
        print var
        root=lxml.html.fromstring(var)
        br.select_form("Form1")
        br.set_all_readonly(False)
        d=dict()
        for control in br.form.controls:
            d[control.name]=br[control.name]
        br["__EVENTTARGET"]=d['__EVENTTARGET']
        br["__EVENTARGUMENT"]=d['__EVENTARGUMENT']
        br["__LASTFOCUS"]=d['__LASTFOCUS']
        br["__VIEWSTATE"]=d['__VIEWSTATE']
        br["__EVENTVALIDATION"]=d['__EVENTVALIDATION']
        br["drpState"]=i
        br["drpDistrict"]=j
        response = br.submit()
        var=response.read()
        soup=BeautifulSoup(var)
        l=[]
        town_list=[]
        for opt in soup.findAll('select',{"name" : "drpTown"}):
            for option in opt.findAll('option'):
                l.append(option.get('value'))
                town_list.append(l)
                l=[]
        for k in town_list:
            sl_no+=1
            root=lxml.html.fromstring(var)
            br.select_form("Form1")
            br.set_all_readonly(False)
            for control in br.form.controls:
                d[control.name]=br[control.name]
            dat=dict()
            row=[]
            try:
                print i,j,k
                root=lxml.html.fromstring(var)
                br.select_form("Form1")
                br.set_all_readonly(False)
                for control in br.form.controls:
                    d[control.name]=br[control.name]
                dat=dict()
                row=[]
                
                try:
                    
                    br["__EVENTTARGET"]=d['__EVENTTARGET']
                    br["__EVENTARGUMENT"]=d['__EVENTARGUMENT']
                    br["__LASTFOCUS"]=d['__LASTFOCUS']
                    br["__VIEWSTATE"]=d['__VIEWSTATE']
                    br["__EVENTVALIDATION"]=d['__EVENTVALIDATION']
                    br["drpState"]=i
                    br["drpDistrict"]=j
                    br["drpTown"]=k
                    response = br.submit()
                    var=response.read()
                    root=lxml.html.fromstring(var)
                    for el in root.cssselect("div#pnlStateProfile table"):
                        for el2 in root.cssselect("tr td.GridHeader"):
                            for el3 in el2.cssselect("span#lblTownName"):
                                town=el3.text_content()
                                print town
                            for el3 in el2.cssselect("span#lblDistrictName"):
                                district=el3.text_content()
                                print district
                            for el3 in el2.cssselect("span#lblStateName"):
                                state=el3.text_content()
                                print state
                        for el2 in root.cssselect("tr.GridAlternativeRows td"):
                            text=el2.text_content().replace('\r\n','')
                            text=text.replace('\t','')
                            if flag:
                                flag=False
                                row.append(text)
                                data_pts.append(text)
                            else:
                                row.append(text)
                                dat[row[0]]=row[1]
                                flag=True
                                row=[]
                        for el2 in root.cssselect("tr.GridRows td"):
                            text=el2.text_content().replace('\r\n','')
                            text=text.replace('\t','')
                            if flag:
                                flag=False
                                row.append(text)
                                data_pts.append(text)
                            else:
                                row.append(text)
                                dat[row[0]]=row[1].replace(',','')
                                flag=True
                                row=[]
                        scraperwiki.sqlite.save(unique_keys=["sl_no"],data={"sl_no":sl_no,"Population Total":dat['Population-Total'],"Proportion of Urban Population Percentage":dat['Proportion of Urban Population (%)'],"Population Urban":dat['Population-Urban'],"Sex Ratio 0 to 6 Year":dat['Sex Ratio(0-6 Year)'],"SC Population":dat['SC Population'],"Sex Ratio of ST":dat['Sex Ratio (ST)'],"Literates":dat['Literates'],"Proportion of ST Percentage":dat['Proportion of ST (%)'],"Total Workers":dat['Total Workers'],"Work Participation Rate Percentage":dat['Work Participation Rate (%)'],"Marginal Worker":dat['Marginal Worker'],"Percentage of Marginal Worker":dat['% of Marginal Worker'],"CL Main and Marginal":dat['CL (Main+Marginal)'],"Proportion of CL Percentage":dat['Proportion of CL (%)'],"HHI Main plus Marginal":dat['HHI (Main+Marginal)'],"Proportion of HHI Percentage":dat['Proportion of HHI (%)'],"Number of Households":dat['Number of Households'],"Average Household Size per Household":dat['Average Household Size(per Household)'],"Population Rural":dat['Population-Rural'],"Sex Ratio":dat['Sex Ratio'],"Population 0 to 6 Years":dat['Population(0-6Years)'],"Sex Ratio SC":dat['Sex Ratio (SC)'],"ST Population":dat['ST Population'],"Proportion of SC Percentage":dat['Proportion of SC (%)'],"Illiterates":dat['Illiterates'],"Literacy Rate Percentage":dat['Literacy Rate (%)'],"Main Worker":dat['Main Worker'],"Percentage of Main Workers":dat['% of Main Workers'],"Non Worker":dat['Non Worker'],"Percentage of non Workers":dat['% of non Workers'],"Al Main plus Marginal":dat['Al (Main+Marginal)'],"Proportion of AL percentage":dat['Proportion of AL (%)'],"OW Main Marginal":dat['OW (Main+Marginal)'],"Proportion of OW Percentage":dat['Proportion of OW (%)'],"State Name":state,"District Name":district,"Sub District Name":town})
                        state='#'
                        district='#'
                        town='#'
                
                except Exception,e:
                     print str(e)
                     print 'hehe'
                     break           
            except:
                #break
                print 'haha'
                if state=='#' and district=='#':
                    break
                else:
                    error.append(state+';'+district)
print errorimport scraperwiki
import mechanize 
import re
import lxml.html
import sys
import requests
from bs4 import BeautifulSoup

url="http://www.censusindia.gov.in/Census_Data_2001/Census_Data_Online/Area_Profile/Town_Profile.aspx?cki=7H7pnwQvpHZ"
br = mechanize.Browser()
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
state_list=[]
flag=True
sl_no=0
dat=dict()
data_pts=[]
state=''
district=''
error=[]
for i in range(1,35):
    l=[]
    if i <10:
        st='0'+str(i)
        l.append(st)
    else:
        st=str(i)
        l.append(st)
    state_list.append(l)


for i in state_list:
    response = br.open(url)
    VAR1 = response.read() #reads the source file for the web page
    br.select_form("Form1")
    br.set_all_readonly(False)
    d=dict()
    for control in br.form.controls:
        d[control.name]=br[control.name]
    br["__EVENTTARGET"]=d['__EVENTTARGET']
    br["__EVENTARGUMENT"]=d['__EVENTARGUMENT']
    br["__LASTFOCUS"]=d['__LASTFOCUS']
    br["__VIEWSTATE"]=d['__VIEWSTATE']
    br["__EVENTVALIDATION"]=d['__EVENTVALIDATION']
    br["drpState"]=i
    response = br.submit()
    var=response.read()
    soup=BeautifulSoup(var)
    l=[]
    district_list=[]
    for opt in soup.findAll('select',{"name" : "drpDistrict"}):
        for option in opt.findAll('option'):
            #print option.get('value')
            l.append(str(option.get('value')))
            district_list.append(l)
            l=[]
    for j in district_list:
        print var
        root=lxml.html.fromstring(var)
        br.select_form("Form1")
        br.set_all_readonly(False)
        d=dict()
        for control in br.form.controls:
            d[control.name]=br[control.name]
        br["__EVENTTARGET"]=d['__EVENTTARGET']
        br["__EVENTARGUMENT"]=d['__EVENTARGUMENT']
        br["__LASTFOCUS"]=d['__LASTFOCUS']
        br["__VIEWSTATE"]=d['__VIEWSTATE']
        br["__EVENTVALIDATION"]=d['__EVENTVALIDATION']
        br["drpState"]=i
        br["drpDistrict"]=j
        response = br.submit()
        var=response.read()
        soup=BeautifulSoup(var)
        l=[]
        town_list=[]
        for opt in soup.findAll('select',{"name" : "drpTown"}):
            for option in opt.findAll('option'):
                l.append(option.get('value'))
                town_list.append(l)
                l=[]
        for k in town_list:
            sl_no+=1
            root=lxml.html.fromstring(var)
            br.select_form("Form1")
            br.set_all_readonly(False)
            for control in br.form.controls:
                d[control.name]=br[control.name]
            dat=dict()
            row=[]
            try:
                print i,j,k
                root=lxml.html.fromstring(var)
                br.select_form("Form1")
                br.set_all_readonly(False)
                for control in br.form.controls:
                    d[control.name]=br[control.name]
                dat=dict()
                row=[]
                
                try:
                    
                    br["__EVENTTARGET"]=d['__EVENTTARGET']
                    br["__EVENTARGUMENT"]=d['__EVENTARGUMENT']
                    br["__LASTFOCUS"]=d['__LASTFOCUS']
                    br["__VIEWSTATE"]=d['__VIEWSTATE']
                    br["__EVENTVALIDATION"]=d['__EVENTVALIDATION']
                    br["drpState"]=i
                    br["drpDistrict"]=j
                    br["drpTown"]=k
                    response = br.submit()
                    var=response.read()
                    root=lxml.html.fromstring(var)
                    for el in root.cssselect("div#pnlStateProfile table"):
                        for el2 in root.cssselect("tr td.GridHeader"):
                            for el3 in el2.cssselect("span#lblTownName"):
                                town=el3.text_content()
                                print town
                            for el3 in el2.cssselect("span#lblDistrictName"):
                                district=el3.text_content()
                                print district
                            for el3 in el2.cssselect("span#lblStateName"):
                                state=el3.text_content()
                                print state
                        for el2 in root.cssselect("tr.GridAlternativeRows td"):
                            text=el2.text_content().replace('\r\n','')
                            text=text.replace('\t','')
                            if flag:
                                flag=False
                                row.append(text)
                                data_pts.append(text)
                            else:
                                row.append(text)
                                dat[row[0]]=row[1]
                                flag=True
                                row=[]
                        for el2 in root.cssselect("tr.GridRows td"):
                            text=el2.text_content().replace('\r\n','')
                            text=text.replace('\t','')
                            if flag:
                                flag=False
                                row.append(text)
                                data_pts.append(text)
                            else:
                                row.append(text)
                                dat[row[0]]=row[1].replace(',','')
                                flag=True
                                row=[]
                        scraperwiki.sqlite.save(unique_keys=["sl_no"],data={"sl_no":sl_no,"Population Total":dat['Population-Total'],"Proportion of Urban Population Percentage":dat['Proportion of Urban Population (%)'],"Population Urban":dat['Population-Urban'],"Sex Ratio 0 to 6 Year":dat['Sex Ratio(0-6 Year)'],"SC Population":dat['SC Population'],"Sex Ratio of ST":dat['Sex Ratio (ST)'],"Literates":dat['Literates'],"Proportion of ST Percentage":dat['Proportion of ST (%)'],"Total Workers":dat['Total Workers'],"Work Participation Rate Percentage":dat['Work Participation Rate (%)'],"Marginal Worker":dat['Marginal Worker'],"Percentage of Marginal Worker":dat['% of Marginal Worker'],"CL Main and Marginal":dat['CL (Main+Marginal)'],"Proportion of CL Percentage":dat['Proportion of CL (%)'],"HHI Main plus Marginal":dat['HHI (Main+Marginal)'],"Proportion of HHI Percentage":dat['Proportion of HHI (%)'],"Number of Households":dat['Number of Households'],"Average Household Size per Household":dat['Average Household Size(per Household)'],"Population Rural":dat['Population-Rural'],"Sex Ratio":dat['Sex Ratio'],"Population 0 to 6 Years":dat['Population(0-6Years)'],"Sex Ratio SC":dat['Sex Ratio (SC)'],"ST Population":dat['ST Population'],"Proportion of SC Percentage":dat['Proportion of SC (%)'],"Illiterates":dat['Illiterates'],"Literacy Rate Percentage":dat['Literacy Rate (%)'],"Main Worker":dat['Main Worker'],"Percentage of Main Workers":dat['% of Main Workers'],"Non Worker":dat['Non Worker'],"Percentage of non Workers":dat['% of non Workers'],"Al Main plus Marginal":dat['Al (Main+Marginal)'],"Proportion of AL percentage":dat['Proportion of AL (%)'],"OW Main Marginal":dat['OW (Main+Marginal)'],"Proportion of OW Percentage":dat['Proportion of OW (%)'],"State Name":state,"District Name":district,"Sub District Name":town})
                        state='#'
                        district='#'
                        town='#'
                
                except Exception,e:
                     print str(e)
                     print 'hehe'
                     break           
            except:
                #break
                print 'haha'
                if state=='#' and district=='#':
                    break
                else:
                    error.append(state+';'+district)
print error