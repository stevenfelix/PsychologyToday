import pandas as pd
import numpy as np
from lxml import html
import requests
import string
import re
import time
from datetime import date
from random import uniform


varNames = "name, title, degrees, profile, years, school, statelicense, graduated, fee, insurance, specialties, specialtiesNum, issues, issuesNum, mentalhealth, mentalhealthNum, sexuality, sexualityNum, txapproach, txapproachNum, orientation, orientationNum, url"
varNamesList = varNames.split(", ")
therapistDF = pd.DataFrame(columns=varNamesList)


def scrape(url):
    regDeg = re.compile("[a-zA-Z]+[a-zA-Z /]*")
    regText = re.compile("\w+[\w .]*")
    regFin = re.compile("\$?\w+[\w /.$()-]*")
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'Accept_Encoding': 'gzip, deflate, sdch, br', 'Accept_Language':'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
    global therapistDF
    global varNamesList
    
    for i in range(0,100):
        page = requests.get(url, headers = headers)
        tree = html.fromstring(page.content)
        
        name = tree.xpath('//div[@id="profHdr"]//h1/text()')[0]
        name = regDeg.search(name).group()
        
        profile = tree.xpath('//div[@class="statementPara"]/text()')
        profile = "\n".join(profile)
        
        degrees = tree.xpath('//div[@id="profHdr"]//h2//text()')
        degrees = [m.group(0) for degree in degrees for m in [regDeg.search(degree)] if m]
        title = degrees.pop(0)
        degrees = ", ".join(degrees)
        
        quals = tree.xpath('//div[@class="profile-qualifications"]//text()')
        quals =[m.group(0) for qual in quals for m in [regText.search(qual)] if m]
        try:
            years = quals[quals.index('Years in Practice')+1]
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
        except ValueError:
            fee = np.nan
        try:
            insurance = finances[finances.index('Accepts Insurance')+1]
        except ValueError:
            insurance = np.nan
        
        ## Xpath locations for Specialties are not consistent from profile to profile, and people have
        ## specialities of varying lengths, so, here I select a section of the profile with a consistent,
        ## unique html class attribute and then parse it myself.
        
        #regSpec = re.compile("\w+[\w]*")
        specsRaw = tree.xpath('//div[@class="spec-list"]//text()')
        specs =[m.group(0) for spec in specsRaw for m in [regFin.search(spec)] if m]
        specsRawText = ', '.join(specsRaw)
        specsText = ', '.join(specs)
        
        # (hopefully exhaustive) list of potential headers
        headersPot = ['Treatment Approach','Sexuality','Specialties', 'Issues', 'Mental Health', 'Client Focus','Religious Orientation','Age', 'Categories','Treatment Orientation','Modality']
        # list of headers in profile
        headersList = [head for head in headersPot if head in specs]
        # create dictionary providing index of each header, so they can be sorted
        headersDict = {}
        for head in headersList: headersDict[head] = specs.index(head)
        # sorted list of headers (for starting and stopping points for each sub section)
        headersSorted = sorted(headersList, key=headersDict.get)
        
        if "Specialties" in headersSorted:
            nextHead = headersSorted[headersSorted.index("Specialties")+1]
            specialties = specs[headersDict["Specialties"]+1:headersDict[nextHead]]
            specialtiesNum = len(specialties)
            specialties = ', '.join(specialties)
        else: specialties = np.nan; specialtiesNum = np.nan
        
        if "Issues" in headersSorted:
            nextHead = headersSorted[headersSorted.index("Issues")+1]
            issues = specs[headersDict["Issues"]+1:headersDict[nextHead]]
            issuesNum = len(issues)
            issues = ', '.join(issues)
        else: issues = np.nan; issuesNum = np.nan
        
        if "Mental Health" in headersSorted:
            nextHead = headersSorted[headersSorted.index("Mental Health")+1]
            mentalhealth = specs[headersDict["Mental Health"]+1:headersDict[nextHead]]
            mentalhealthNum = len(mentalhealth)
            mentalhealth = ', '.join(mentalhealth)
        else: mentalhealth = np.nan; mentalhealthNum = np.nan
        
        
        if "Sexuality" in headersSorted:
            nextHead = headersSorted[headersSorted.index("Sexuality")+1]
            sexuality = specs[headersDict["Sexuality"]+1:headersDict[nextHead]]
            sexualityNum = len(sexuality)
            sexuality = ', '.join(sexuality)
        else: sexuality= np.nan; sexualityNum = np.nan
        
        if "Treatment Approach" in headersSorted:
            nextHead = headersSorted[headersSorted.index("Treatment Approach")+1]
            txapproach = specs[headersDict["Treatment Approach"]+1:headersDict[nextHead]]
            txapproachNum = len(txapproach)
            txapproach = ', '.join(txapproach)
        else: txapproach = np.nan; txapproachNum = np.nan
        
        
        if "Treatment Orientation" in headersSorted:
            nextHead = headersSorted[headersSorted.index("Treatment Orientation")+1]
            orientation = specs[headersDict["Treatment Orientation"]+1:headersDict[nextHead]]
            orientationNum = len(orientation)
            orientation = ', '.join(orientation)
        else: orientation = np.nan; orientationNum = np.nan
        
        x = pd.Series(data = [name, title, degrees, profile, years, school, statelicense, graduated, fee, 
                                insurance, specialties, specialtiesNum, issues, issuesNum, mentalhealth, 
                                mentalhealthNum, sexuality, sexualityNum, txapproach, txapproachNum, orientation, 
                                orientationNum, url], index = varNamesList)
        
        therapistDF = therapistDF.append(x, ignore_index = True)
        
        nextLink =  tree.xpath('//a[@class="profile-next"]/@href')
        nextLink = nextLink[0]
        url = nextLink
        time.sleep(uniform(.5,1.5)*5)


url = "https://therapists.psychologytoday.com/rms/prof_detail.php?profid=254452&ref=1&sid=1486700821.2187_5826&city=Boston&county=Suffolk&state=MA&tr=ResultsName"
scrape(url)

today = date.today().isoformat()
os.chdir('/Users/stevenfelix/Dropbox/JobSearch/DataScienceProjects/PsychologyToday/')

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('psychologytoday%s.xlsx' % today, engine='xlsxwriter')
# Convert the dataframe to an XlsxWriter Excel object.
therapistDF.to_excel(writer, sheet_name='Sheet1')
# Close the Pandas Excel writer and output the Excel file.
writer.save()

## Next steps:
# Currently, you give this a starting profile, and it just continues by going " next"
