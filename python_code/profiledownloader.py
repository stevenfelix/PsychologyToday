import requests
import pandas as pd
import numpy as np
from lxml import html
import string
from random import uniform
import re
import time
import os

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'Accept_Encoding': 'gzip, deflate, sdch, br', 'Accept_Language':'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
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
    if 'output.txt' in filenames: output = open("output.txt", "a+")
    else: output = open("output.txt", "w+")
    n = 0
    for city in cities:
        currentProfile = get_first_profile("https://therapists.psychologytoday.com/rms/state/MA/%s.html" % city)
        if not currentProfile: log('\nNo starting profile in %s, skipping to next city.\n' % city); continue
        profid = regprofid.search(currentProfile).group()
        log('\n\n****Starting profile in %s: %s; \n%s\n' % (city, profid, currentProfile), output)
        previousProfile = None; nextProfile = None
        for i in range(1,200):
            profid = regprofid.search(currentProfile).group()
            if profid in ids:
                nextProfile = get_next_profile(currentProfile)['nextProfile']
                log('\nFile already scraped: %s_%s.txt\n%s \n' % (city, profid, currentProfile), output)
            else:
                nextProfile = scrapeProf(currentProfile, city, profid)
                log('\nFile %d successfully written: %s_%s.txt\n%s \n' % (n, city, profid, currentProfile), output)
                ids.append(profid)
                n += 1
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


cities = "Sommervile, Brighton, Allston, Watertown, Newton, Belmont"
cities = cities.split(", ")


scrape(cities)