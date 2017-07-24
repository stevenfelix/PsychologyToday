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
from collections import defaultdict

os.chdir('/Users/stevenfelix/Dropbox/DataScience/Projects/PsychologyToday/data/')

""" File needs a lot of editing!"""

################### Retrieving Random Links #########################

def select_profiles(n, starting_dict = defaultdict(list)):
    """Semi-randomly acquires the profile IDs for therapists and returns them as a dictionary organized by state.
    
    Inputs:
        n - pandas Series listing the number of links desired per state
        starting_list - Optional; a Dictionary of lists. Keys are the abbreviation for each state, and
                        contents is a list of profile IDs that have already beens sampled from that state
    
    This process frequently encounters errors. The function is designed to append new profile links
    to list 'l' in place. This way even if you get an error, you won't lose the URLs you have already
    scraped. To pick up where you left off after an error, simply provide the existing list of links
    to 'starting_list'.
    
    """
    
    # progress log to review for errors, etc.
    output = open("output.txt", "a+")
    
    
    # local variables
    searchBaseUrl = 'https://therapists.psychologytoday.com/rms/prof_results.php?search='
    profBaseUrl = "https://therapists.psychologytoday.com/rms/prof_detail.php?profid="
    zipdb = ZipCodeDatabase()
    states = needed.index
    regprofid = re.compile('(?<=profid=)[0-9]+')
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'Accept_Encoding': 'gzip, deflate, sdch, br', 'Accept_Language':'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
            
    for state in states:

        # select the zips available to each state
        zips = [z.zip for z in zipdb.find_zip(state = state)]
        numzips = len(zips)
        
        while n > len(starting_dict[state]):
            
            unique_id = None
            while unique_id is None:
                time.sleep(uniform(.5,1.5)*2)
                randzip = zips[randint(0, numzips-1)]
                url = searchBaseUrl + randzip
                searchrequest = requests.get(url, headers = headers)
                searchtree = html.fromstring(searchrequest.content)
                links = searchtree.xpath('//a/@href')
                #links = [link for link in links if profBaseUrl in link]
                unique_id = get_unique_id(links, starting_dict[state], regprofid)

            # append id
            starting_dict[state].append(unique_id)

            # print progress to console
            print '{} of {} for {}: ID = {}'.format(len(starting_dict[state]),n,state,unique_id)
            
            output.write(str(unique_id))
    output.close()
    return starting_dict

def get_unique_id(links, id_list, regex):
    ids = [m.group() for link in links for m in [regex.search(link)] if m]
    ids = set(ids)
    for id_num in ids:
        if id_num in id_list:
            print 'duplicate moving on'
            continue
        else:
            return id_num
    return None

    

### don't save as text!!, anything else, please
#with open('output.txt', 'w+') as f: 
#    f.write(str(links))


states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

needed = pd.Series(2,index = states)


#starting_dict = defaultdict(list, keys = states)
starting_dict = defaultdict(list)

links_dict = select_profiles(2, starting_dict)
starting_dict


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