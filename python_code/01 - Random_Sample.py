import pandas as pd
import numpy as np
from lxml import html
import string
from random import uniform, randint
import re
import time
import requests
import os
from pyzipcode import ZipCodeDatabase
import json

os.chdir('/Users/stevenfelix/Dropbox/DataScience/Projects/PsychologyToday/Data/')

""" File needs a lot of editing!"""

################### Retrieving Random Links #########################
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'Accept_Encoding': 'gzip, deflate, sdch, br', 'Accept_Language':'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
            
def get_zipcodes():
    db = ZipCodeDatabase()
    kc1 = db.find_zip(city = "Kansas City")[0]
    allzips = [z.zip for z in db.get_zipcodes_around_radius(kc1.zip, 10000)]
    allzipinfo = [(db[z].zip,db[z].city,db[z].state) for z in allzips]
    df_allzipinfo = pd.DataFrame(allzipinfo, columns=['ZIP','city','state'])
    df_allzipinfo = df_allzipinfo.loc[[(state not in ['PR','AS','VI']) for state in df_allzipinfo.state]]
    return df_allzipinfo


def get_links(n, zipdb, states, linklist = None):
    """Searches psychologytoday's directory for a randomly-selected US zipcode n times. 
    Returns a list containing the hyperlinks for the first search-result in each search (n links)."""
    
    output = open("output.txt", "a+")
    
    if linklist: l = linklist
    else: l = []
    searchBaseUrl = 'https://therapists.psychologytoday.com/rms/prof_results.php?search='
    profBaseUrl = "https://therapists.psychologytoday.com/rms/prof_detail.php?profid="
    for state in states:
        zips = [z.zip for z in zipdb.find_zip(state = state)]
        numzips = len(zips)
        for i in range(n[state]):
            # random zip code
            randzip = zips[randint(0, numzips-1)]
            url = searchBaseUrl + randzip
            
            # request search page
            searchrequest = requests.get(url, headers = headers)
            #searchrequest.status_code == requests.codes.ok
            searchtree = html.fromstring(searchrequest.content)
            links = searchtree.xpath('//a/@href')
            links = [link for link in links if profBaseUrl in link]
            print '{} of {} for {}'.format(i,n[state],state)
            if links: t = (randzip,links[0])
            else: t = (randzip,None)
            l.append(t)
            output.write(str(t))
            print t
            time.sleep(uniform(.5,1.5)*2)
    output.close()
    return l

with open('output.txt', 'w+') as f: 
    f.write(str(links))



linksnew = get_links(needed, db, needed.index, linklist = links)
#linksnew = get_links(1000)

#################### re-opening links from file #########################

def linksfromfile(file):
    with open(file, 'r') as f: 
        linkfile = f.read()
    urlregex = re.compile("[hN][^']+")
    zipregex = re.compile("(?<=u')\d+")
    return zip(zipregex.findall(linkfile),urlregex.findall(linkfile))

links2 = linksfromfile('output.txt')


"""
inds = []
for ind,val in enumerate(links):
    if val[1] != None:
        if not re.match('http', val[1]):
            inds.append(ind)

[links[i] for i in inds]
for i in inds:
    ZIP = links[i][0]
    links[i] = (ZIP, None)
[links[i] for i in inds]
"""

################### Construct Data Frames and Pickle ##################

#df = pd.read_pickle('searchlinks_pd_DF.pkl')
#links = [x for x in df.itertuples(index = False, name = None)]


# DF of search links
db = ZipCodeDatabase()
df = pd.DataFrame(links, columns=['searchZIP','profileURL'])
df['searchCity'] = [db[x].city for x in df.searchZIP]
df['searchState'] = [db[x].state for x in df.searchZIP]
#df = df.loc[[(state not in non51) for state in df.searchState]]
#df.to_pickle('searchlinks_pd_DF.pkl')

needed = 200 - df.searchState.value_counts()
needed = needed.drop(['VI','AS','PR'])
needed



####################### investigating data ##########################

### proportions of zipcodes in each state
zips_per_state = df_allzipinfo.state.value_counts()
zip_proportions = zips_per_state*100/df_allzipinfo.shape[0]
df_zipprop = pd.concat([zip_proportions,df.searchState.value_counts()*100/df.shape[0]],axis = 1, ignore_index=False)
df_zipprop.columns = ['dictionary','pt_searches']
df_zipprop.sort_values(by='pt_searches',axis=0)

df.searchState.value_counts()

CAzips = db.find_zip(state="CA")
len(CAzips)