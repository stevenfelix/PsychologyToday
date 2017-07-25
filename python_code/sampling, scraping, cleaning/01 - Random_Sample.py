import pandas as pd
import numpy as np
from lxml import html
import string
from random import uniform, randint
import re
import time
import requests
import json
from pyzipcode import ZipCodeDatabase
from collections import defaultdict


################### Functions #########################

def select_profiles(n, id_dict):
    """Semi-randomly acquires the profile IDs for therapists and returns them as a dictionary organized by state.
    
    Inputs:
        n - integer - number of links per state desired
        id_dict -  a defaultdict(list) to update with links for each state. id_dict may simply
                   be an initialized defaultdict, or it can be a defaultdict that already has
                   key/value pairs. id_dict is updated in place so that all ids will be saved
                   even if the function reaches an error.
    Output:  no output. Defaultdict is updated in place"""
    
    # local variables
    # urls and headers
    searchBaseUrl = 'https://therapists.psychologytoday.com/rms/prof_results.php?search='
    profBaseUrl = "https://therapists.psychologytoday.com/rms/prof_detail.php?profid="
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'Accept_Encoding': 'gzip, deflate, sdch, br', 'Accept_Language':'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
    # database of zipcodes
    zipdb = ZipCodeDatabase()
    # regular expression to parse IDs from urls
    regprofid = re.compile('(?<=profid=)[0-9]+')

    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]      
    
    # get n unique IDs from each state
    for state in states:
        
        zips = [z.zip for z in zipdb.find_zip(state = state)]
        numzips = len(zips)
        
        while n > len(starting_dict[state]):
            unique_id = None
            iters = 0  # this will allow us to continue to next state if can't find any more unique IDs
            
            while unique_id is None:
                iters += 1
                print "Loop: {}".format(iters)
                if iters == 20:
                    print 'After 20 iterations, could not find new ID in {}'.format(state)
                    break
                time.sleep(uniform(.5,1.5)*2)
                randzip = zips[randint(0, numzips-1)]
                url = searchBaseUrl + randzip
                searchrequest = requests.get(url, headers = headers)
                searchtree = html.fromstring(searchrequest.content)
                links = searchtree.xpath('//a/@href')
                #links = [link for link in links if profBaseUrl in link]
                unique_id = get_unique_id(links, starting_dict[state], regprofid)
            
            # If 20 loops without finding 
            if iters == 20: break
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
            print 'Duplicate moving on'
            continue
        else:
            return id_num
    return None


##############   Run Function    ##################


# When starting from scratch run the next line
# When re-starting after an error, provide a 
# defaultdict containing the links that have already been sampled 
id_dict = defaultdict(list)

# run the program
select_profiles(200, id_dict)
starting_dict

# check numbers / state
for k in id_dict:
    print k, len(id_dict[k])

# save as JSON
with open('../Data/ids.json', 'w') as fp:
    json.dump(id_dict, fp)

#with open('ids.json','r') as fp:
#    id_dict = json.load(fp)

