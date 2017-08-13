"""
File: 02 - Scrape_Data.py
Author: Steven Felix
Description: Using the dictionary of therapists' IDs derived from '01 - Random_Sample.py', this script
         iterates through each ID, downloading and parsing the respective profile. Function
         saves a backup of the in-progress dataframe every 50 iterations. At completion
         the data frame is saved to a pickle. Data needs some editing before it can be
         saved as CSV (will be done in '03 - Data_Prep.py')

"""

import requests
import pandas as pd
import numpy as np
from lxml import html
import string
from random import uniform
import re
import time
import os
import string


######################## Run program ##################

# open list of ids
with open('ids.json','r') as fp:
    id_dict = json.load(fp)

# initalize dataframe [or make sure new dataframe conforms to following variable list]
varNames = ("id_num, name, title, degrees, city, state, ZIP, profile, years, school, statelicense, graduated, fee, insurance, " 
            "specialties, specialtiesnum, issues, issuesnum, mentalhealth, mentalhealthnum, sexuality, sexualitynum, " 
            "treatmentapproach, treatmentapproachnum, treatmentorientation, treatmentorientationnum, url")
varNamesList = varNames.split(", ")
therapistDF = pd.DataFrame(columns=varNamesList)    

# Note, therapistDF can be empty, initalized DF, or one with data already in it
therapistDF = scrape(id_dict, therapistDF, varNamesList)

######################### Functions ####################

def scrape(id_dict, df, variables):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'Accept_Encoding': 'gzip, deflate, sdch, br', 'Accept_Language':'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
    profBaseUrl = "https://therapists.psychologytoday.com/rms/prof_detail.php?profid="
    
    regDigits = re.compile('\d+')
    regDeg = re.compile("[a-zA-Z]+[-&\.a-zA-Z /]*")
    regText = re.compile("\w+[\w .]*")
    regFin = re.compile("\$?\w+[\w /.$()-]*")
    regex = (regDigits, regDeg, regText, regFin)
    
    # flatten the dictionary and remove duplicates
    all_ids = []
    for key in id_dict:
        all_ids.extend(id_dict[key])
    all_ids = list(set(all_ids))
    
    oldids = list(df.id_num)
    print 'length of full list of ids: {}'.format(len(all_ids))
    all_ids = [id_num for id_num in all_ids if id_num not in oldids]
    total = len(all_ids)
    print 'length of list of new ids: {}'.format(total)
    n = -1
    output = open("parsing_progress.txt", "w+")
    
    for id_num in all_ids:

        url = profBaseUrl + id_num
        
        # get content
        tree = get_content(url,headers, output)
        if tree == None: continue
        
        # parse and append content
        profileSeries = parse_content(tree, id_num, url, variables, regex)
        df = df.append(profileSeries, ignore_index = True)
        
        # log progress, and pickle dataframe periodically
        n +=1
        log('\nProfile ID {} successfully parsed (number {} of {})\n'.format(id_num,n,total-1), output)
        if n % 50 == 0:
            df.to_pickle('BACKUP_therapist_profiles.pkl') # just in case of errors
            log('\n**********Pickled at {}\n'.format(n), output)
        time.sleep(uniform(.5,1.5)*2)
    
    # save final data frame to pickle
    df.to_pickle('./data/therapist_profiles.pkl')
    #df.to_csv('therapist_profiles.csv', encoding='utf-8')
    log("\n\n****Process Complete: {} linked iterated [failed links not written] *****\n\n".format(n+1), output)
    
    output.close()
    return df


def log(event, destination):
    print event
    destination.write(event)


def get_links(pdDF):
    df = pd.read_pickle(pdDF)
    return [x for x in df.itertuples(index = False, name = None)]


def get_content(url, headers, outputlog):
    page = requests.get(url, headers = headers)
    if page.url == url and page.ok:
        return html.fromstring(page.content)
    else:
        log('URL did not process: {}'.format(url), outputlog)
        return None

def parse_content(tree, id_num, url, variablenames, regex):
    regDigits, regDeg, regText, regFin = regex
    commondegrees = 'PhD PsyD EdM LMHC MD Med NP MSM MS MhD'.lower().split(' ')
    
    name = tree.xpath('//div[@id="profHdr"]//h1/text()')
    if name:
        name = regDeg.search(name[0]).group()

    profile = tree.xpath('//div[@class="statementPara"]/text()')
    profile = "\n".join(profile)
    profile = profile.strip().replace('\n',' ')
    
    degrees = tree.xpath('//div[@id="profHdr"]//h2//text()')
    degrees = [m.group(0).lower() for degree in degrees for m in [regDeg.search(degree)] if m]
    if degrees:
        if degrees[0] in commondegrees:
            title = np.nan
        else:
            title = degrees.pop(0)
        degrees = ", ".join(degrees)
    else:
        title = np.nan
        degrees = np.nan
    

    city = tree.xpath('//div[@class="address address-rank-1"]//div[@itemprop="address"]//span[@itemprop="addressLocality"]/text()')
    try: city = city[0].encode()
    except IndexError: city = np.nan
    
    state = tree.xpath('//div[@class="address address-rank-1"]//div[@itemprop="address"]//span[@itemprop="addressRegion"]/text()')
    try: state = state[0].replace(u'\xa0', u' ').encode()
    except IndexError: state = np.nan
    
    ZIP = tree.xpath('//div[@class="address address-rank-1"]//div[@itemprop="address"]//span[@itemprop="postalcode"]/text()')
    try: ZIP = ZIP[0].encode()
    except IndexError: ZIP = np.nan
    
    quals = tree.xpath('//div[@class="profile-qualifications"]//text()')
    quals =[m.group(0) for qual in quals for m in [regText.search(qual)] if m]
    
    try:
        years = quals[quals.index('Years in Practice')+1]
        years = regDigits.search(years).group(0)
    except ValueError:
        years = np.nan
    try:
        school = quals[quals.index('School')+1]
    except ValueError:
        school = np.nan
    try:
        statelicense = quals[quals.index('License No. and State')+1]
    except ValueError:
        statelicense = np.nan;
    try:
        graduated = quals[quals.index('Year Graduated')+1]
    except ValueError:
        graduated = np.nan
    
    finances = tree.xpath('//div[@class="profile-finances"]//text()')
    finances =[m.group(0) for finance in finances for m in [regFin.search(finance)] if m]
    try:
        fee = finances[finances.index('Avg Cost (per session)')+1]
        fee = regDigits.findall(fee)
        fee = [int(n) for n in fee]
        fee = np.mean(fee)
    except ValueError:
        fee = np.nan
    try:
        insurance = finances[finances.index('Accepts Insurance')+1]
    except ValueError:
        insurance = np.nan
    
    ## Xpath inconsistent for Specialties, also varying lengths. Better to parse raw list

    specsRaw = tree.xpath('//div[@class="spec-list"]//text()')
    specs =[m.group(0) for spec in specsRaw for m in [regFin.search(spec)] if m]
    #specsRawText = ', '.join(specsRaw) # could add to DF to check for bugs
    #specsText = ', '.join(specs) # could add to DF to check for bugs
    
    # (hopefully exhaustive) list of potential headers
    headersPot = ['Treatment Approach','Sexuality','Specialties', 'Issues', 'Mental Health', 'Client Focus','Religious Orientation','Age', 'Categories','Treatment Orientation','Modality']
    # list of headers in profile
    headersList = [head for head in headersPot if head in specs]
    # create dictionary providing index of each header in original list of specialties, so they can be sorted
    headersDict = {}
    for head in headersList:
        headersDict[head] = specs.index(head)
    # sorted list of headers (for starting and stopping points for each sub section)
    headersSorted = sorted(headersList, key=headersDict.get)
    
    myheaders = 'Specialties, Issues, Mental Health, Sexuality, Treatment Approach, Treatment Orientation, Age'
    myheaders = myheaders.split(', ')
    
    for header in myheaders:
        exec(header.replace(" ", "").lower() + ',' + header.replace(" ", "").lower() + 'num = parseSpecialties' 
            '(header,headersSorted,headersDict, specs)')

    #id = regDigits.search(file).group()
    
    x = pd.Series(data = [id_num, name, title, degrees, city, state, ZIP, profile, years, school, statelicense, graduated, fee,
                         insurance,specialties, specialtiesnum, issues, issuesnum, mentalhealth, mentalhealthnum,
                         sexuality, sexualitynum,treatmentapproach, treatmentapproachnum, treatmentorientation,
                         treatmentorientationnum, url], index = variablenames)
    return x
    #os.rename(profileDir + file, profileDir + 'processed/' + file)

def parseSpecialties(header, sortedheaders, dictionary, datalist):
    """ Given: a list of raw items, a list of headers sorted as they appear in raw items,
        a dictionary of the indices of the headers in the raw items, a desired header:
        Return: a tuple containing string of subcategory items and count of these items"""
    if header in sortedheaders:
        try:
            nextheader = sortedheaders[sortedheaders.index(header)+1]
            specialties = datalist[dictionary[header]+1:dictionary[nextheader]]
        except IndexError: 
            specialties = datalist[dictionary[header]+1:len(datalist)]
        specialtiesNum = len(specialties)
        specialties = ', '.join(specialties)
        return specialties, specialtiesNum
    else:
        return np.nan, np.nan


