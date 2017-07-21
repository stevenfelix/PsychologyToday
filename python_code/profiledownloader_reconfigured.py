import pandas as pd
import numpy as np
from lxml import html
import string
from random import uniform
import re
import time
import requests
import os
from pyzipcode import ZipCodeDatabase

os.chdir('/Users/stevenfelix/Dropbox/DataScience/Projects/PsychologyToday/Data/')

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'Accept_Encoding': 'gzip, deflate, sdch, br', 'Accept_Language':'en-US,en;q=0.8',
            'Connection': 'keep-alive'}


################### Retrieving Random Links #########################

def get_zipcodes():
    db = ZipCodeDatabase()
    kc1 = db.find_zip(city = "Kansas City")[0]
    return [z.zip for z in db.get_zipcodes_around_radius(kc1.zip, 10000)]
    

def get_links(n, linklist = None):
    """Searches psychologytoday's directory for a randomly-selected US zipcode n times. 
    Returns a list containing the hyperlinks for the first search-result in each search (n links)."""
    if linklist: l = linklist
    else: l = []
    searchBaseUrl = 'https://therapists.psychologytoday.com/rms/prof_results.php?search='
    profBaseUrl = "https://therapists.psychologytoday.com/rms/prof_detail.php?profid="

    allzips = get_zipcodes()
    for i in range(n):
        randzip = allzips[random.randint(1, numzips)]
        url = searchBaseUrl + randzip
    
        searchrequest = requests.get(url, headers = headers)
        #searchrequest.status_code == requests.codes.ok
        searchtree = html.fromstring(searchrequest.content)
        links = searchtree.xpath('//a/@href')
        links = [link for link in links if profBaseUrl in link]
        print '{} of {}'.format(i,n)
        if links:
            l.append((randzip,links[0]))
            print (randzip,links[0])
        else:
            l.append((randzip,None))
            print (randzip,None)
        time.sleep(uniform(.5,1.5)*2)
    return l


linksnew = get_links(1000)
len(links)
links is linksnew


df = pd.DataFrame(links, columns=['searchZIP','profileURL'])
df['searchCity'] = [db[x].city for x in df.searchZIP]
df['searchState'] = [db[x].state for x in df.searchZIP]
non51 = ['PR','AS','VI']
df = df.loc[[(state not in non51) for state in df.searchState]]
#df.to_pickle('searchlinks.pkl')
df.head()
df.searchState.value_counts()


### create data frame of my zipcode dictionary
allzipinfo = [(db[z].zip,db[z].city,db[z].state) for z in allzips]
df_allzipinfo = pd.DataFrame(allzipinfo, columns=['ZIP','city','state'])

# remove non 50 states / PR
df_allzipinfo = df_allzipinfo.loc[[(state not in non51) for state in df_allzipinfo.state]]
df_allzipinfo.state.value_counts().shape
#df_allzipinfo.to_pickle('allzipinfo.pkl')

### proportions of zipcodes in each state
zips_per_state = df_allzipinfo.state.value_counts()
zip_proportions = zips_per_state*100/df_allzipinfo.shape[0]
df_zipprop = pd.concat([zip_proportions,df.searchState.value_counts()*100/df.shape[0]],axis = 1, ignore_index=False)
df_zipprop.columns = ['dictionary','pt_searches']
df_zipprop.sort_values(by='pt_searches',axis=0)



regprofileurl = re.compile('https://therapists\.psychologytoday\.com/rms/prof_detail\.php\?profid\?\=')
regprofid = re.compile('(?<=profid=)[0-9]+')
regDigits = re.compile('\d+')
profBaseUrl = "https://therapists.psychologytoday.com/rms/prof_detail.php?profid="
profileDir = '/Users/samf526/Dropbox/JobSearch/DataScienceProjects/PsychologyToday/profiles'
os.chdir(profileDir)

filenames = os.listdir(profileDir)
filenames = [file for file in filenames if '.txt' in file]
ids = [m.group(0) for file in filenames for m in [regDigits.search(file)] if m]

def scrape(cities):
    global ids
    
    # to log the progress and errors from the scraper:
    if 'output.txt' in filenames: output = open("output.txt", "a+")
    else: output = open("output.txt", "w+")
    
    # Iterate through given cities
    n = 0
    for city in cities:
        
        # Start from initial search reseult page
        currentProfile = get_first_profile("https://therapists.psychologytoday.com/rms/state/MA/%s.html" % city)
        if not currentProfile: log('\nNo starting profile in %s, skipping to next city.\n' % city); continue
        profid = regprofid.search(currentProfile).group()
        log('\n\n****Starting profile in %s: %s; \n%s\n' % (city, profid, currentProfile), output)
        previousProfile = None; nextProfile = None
        
        # Download up to 200 profiles from each city
        for i in range(1,200):
            profid = regprofid.search(currentProfile).group()
            
            # Check to see if we've already scraped this page, if so, parse it to get link to 'nextProfile' and move on
            if profid in ids:
                nextProfile = get_next_profile(currentProfile)['nextProfile']
                log('\nFile already scraped: %s_%s.txt\n%s \n' % (city, profid, currentProfile), output)
            
            # parse the current page, save it to disk, and return the nextLink
            else:
                nextProfile = scrapeProf(currentProfile, city, profid)
                log('\nFile %d successfully written: %s_%s.txt\n%s \n' % (n, city, profid, currentProfile), output)
                ids.append(profid)
                n += 1
            
            # Catch problems: If currentProfile is rornonexistant, nextProfile == None
            # This could probably be improved. You could probably check for the Requests response
            # in the original scrapping of Current Profile
            
            if not nextProfile:
                #os.rename('%s_%s.txt' % (city,profid), '%s_%s_ERROR.txt' % (city,profid))
                log(('\n\n ***Bad (pro)file: %s_%s.txt\n***%s \n\n***Return to: %s\n' % 
                    (city,profid, currentProfile, previousProfile)), output)
                currentProfile = raw_input("No 'next' link found, please enter new link. Try here: " 
                                            "\n%s\nOr enter 'next' to go to next city:" % previousProfile)
                ids.remove(profid)
                time.sleep(uniform(.5,1.5)*5)
                if currentProfile == 'next': break
                else: continue
            
            # move to next profile
            previousProfile = currentProfile
            currentProfile = nextProfile
            time.sleep(uniform(.5,1.5)*5)
    log("\n\n****Process Complete: %d files written *****\n\n" % n, output)
    output.close()


def log(event, destination):
    print event
    destination.write(event)

def get_first_profile(url):
    global profBaseUrl
    global headers
    pageCity = requests.get(url, headers = headers)
    treeCity = html.fromstring(pageCity.content)
    links = treeCity.xpath('//a/@href')
    links = [link for link in links if profBaseUrl in link]
    return links[0] if links else None

def get_next_profile(url):
    global headers
    profilePage = requests.get(url, headers = headers)
    tree = html.fromstring(profilePage.content)
    nextLink = tree.xpath('//a[@class="profile-next"]/@href')
    if nextLink: nextLink = nextLink[0]
    else: nextLink =  None
    return {"nextProfile": nextLink, "profileString":profilePage.content}

def scrapeProf(url, city, idnum):
    dic = get_next_profile(url)
    with open('%s_%s.txt' % (city,idnum), "w") as text_file:
        text_file.write(dic['profileString'])
    return dic['nextProfile']


# California
# MA: "Sommervile, Brighton, Allston, Watertown, Newton, Belmont"
cities = "Sommervile, Brighton, Allston, Watertown, Newton, Belmont"
cities = cities.split(", ")

scrape(cities)