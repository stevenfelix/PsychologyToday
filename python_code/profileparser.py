import pandas as pd
import numpy as np
from lxml import html
import string
import re
from datetime import date
import os

os.getcwd()
profileDir = '/Users/stevenfelix/Dropbox/JobSearch/DataScienceProjects/PsychologyToday/profiles/'
os.chdir(profileDir)

regDigits = re.compile('\d+')
filenames = os.listdir(profileDir)
filenames = [file for file in filenames if regDigits.search(file)]
len(filenames)

varNames = ("name, title, degrees, city, profile, years, school, statelicense, graduated, fee, insurance, " 
            "specialties, specialtiesnum, issues, issuesnum, mentalhealth, mentalhealthnum, sexuality, sexualitynum, " 
            "treatmentapproach, treatmentapproachnum, treatmentorientation, treatmentorientationnum, file, url")

varNamesList = varNames.split(", ")
therapistDF = pd.DataFrame(columns=varNamesList)

def parseProfile(fileList):
    global therapistDF
    regDeg = re.compile("[a-zA-Z]+[-&\.a-zA-Z /]*")
    regText = re.compile("\w+[\w .]*")
    regFin = re.compile("\$?\w+[\w /.$()-]*")
    commondegrees = 'PhD PsyD EdM LMHC MD Med NP MSM MS MhD'.lower()
    commondegrees = commondegrees.split(' ')
    for file in filenames:
        profileText  = open(file, 'r').read()
        tree = html.fromstring(profileText)
        
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
        
        quals = tree.xpath('//div[@class="profile-qualifications"]//text()')
        quals =[m.group(0) for qual in quals for m in [regText.search(qual)] if m]

        city = tree.xpath('//div[@class="address address-rank-1"]//div[@itemprop="address"]//span[@itemprop="addressLocality"]/text()')
        try: city = city[0]
        except IndexError: city = np.nan
        
        try:
            years = quals[quals.index('Years in Practice')+1]
            years = [int(m.group(0)) for year in years for m in [regDigits.search(years)] if m]
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
        for head in headersList: headersDict[head] = specs.index(head)
        # sorted list of headers (for starting and stopping points for each sub section)
        headersSorted = sorted(headersList, key=headersDict.get)
        
        myheaders = 'Specialties, Issues, Mental Health, Sexuality, Treatment Approach, Treatment Orientation, Age'
        myheaders = myheaders.split(', ')
        
        for header in myheaders:
            exec(header.replace(" ", "").lower() + ',' + header.replace(" ", "").lower() + 'num = parseSpecialties' 
                '(header,headersSorted,headersDict, specs)')

        id = regDigits.search(file).group()
        url = 'https://therapists.psychologytoday.com/rms/prof_detail.php?profid=%s' % id
        
        x = pd.Series(data = [name, title, degrees, city, profile, years, school, statelicense, graduated, fee,
                             insurance,specialties, specialtiesnum, issues, issuesnum, mentalhealth, mentalhealthnum,
                             sexuality, sexualitynum,treatmentapproach, treatmentapproachnum, treatmentorientation,
                             treatmentorientationnum, file, url], index = varNamesList)
        therapistDF = therapistDF.append(x, ignore_index = True)
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


parseProfile(filenames)


today = date.today().isoformat()
os.chdir('/Users/stevenfelix/Dropbox/JobSearch/DataScienceProjects/PsychologyToday/')


# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('psychologytoday%s.xlsx' % today, engine='xlsxwriter')
# Convert the dataframe to an XlsxWriter Excel object.
therapistDF.to_excel(writer, sheet_name='Sheet1')
# Close the Pandas Excel writer and output the Excel file.
writer.save()

## counting number of various degrees
degreesString = ', '.join(therapistDF['degrees'])
re.search('ma\b', therapistDF.loc[29, 'degrees']).group()
re.findall('\\n', 'ma mad,\n phd')