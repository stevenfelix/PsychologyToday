import pandas as pd
import numpy as np
import re
import os
from collections import defaultdict
import time

def clean_data(data, statedict):
    #remove duplicates
    df2 = data[[(not i) for i in data.name.duplicated()]]
    df2 = df2.reset_index().drop(u'index',axis =1)

    #encode column names as asci
    df2.columns = [c.encode('ascii') for c in df2.columns]

    ## remove duplicates
    
    # change states to ascii
    for ind,s in enumerate(df2['state']):
        try:
            df2.loc[ind,'state'] = s.replace(u'\xa0', u' ').encode()
        except AttributeError:
            df2.loc[ind,'state'] = 'NA'.encode()
    
    # drop states
    df2 = df2[[(state in statedict['all_states']) for state in df2.state]]
    
    # add in region
    df2['region'] = [statedict[state] for state in df2.state]
    
    del df2['sexualitynum'] # few therapists include this
    del df2['specialtiesnum'] # PT limits to 3 specialities, so most everyone lists 3
    
    df2 = df2[df2.title != 'treatment facility']
    df2 = df2.reset_index().drop('index',axis = 1).set_index('name')
    del df2.index.name
    
    numvars = ['issuesnum','treatmentapproachnum','treatmentorientationnum','mentalhealthnum','years']
    df2.loc[:,numvars] = df2.loc[:,numvars].astype(float)
    return df2

def get_stateinfo():
    south = ('Delaware, Maryland, Florida, Georgia, North Carolina, South Carolina, Virginia, West Virginia, Alabama, ' +
            'Kentucky, Mississippi, Tennessee, Arkansas, Louisiana, Oklahoma, Texas').split(', ')
    northeast = ('Maine, New Hampshire, Vermont, Massachusetts, Connecticut, Rhode Island, New York, Pennsylvania, ' + 
            'New Jersey, District of Columbia').split(', ')
    midwest = 'Illinois, Indiana, Iowa, Kansas, Michigan, Minnesota, Missouri, Nebraska, North Dakota, Ohio, South Dakota, Wisconsin'.split(', ')
    mountain = 'Montana, Wyoming, Colorado, New Mexico, Idaho, Utah, Arizona, Nevada'.split(', ')
    pacific = 'California, Oregon, Washington, Hawaii, Alaska'.split(', ')
    stateinfo = defaultdict()
    regions = ['south', 'northeast', 'midwest', 'mountain', 'pacific']
    for region in regions:
        regionlist = eval(region)
        for state in regionlist:
            stateinfo[state] = region
    stateinfo['all_states'] = south + northeast + midwest + mountain + pacific
    return stateinfo

def summarizedata(df):
    print '\n\nShape: ', df.shape, '\n\n'
    print df.dtypes, '\n\n'
    print df.state.value_counts(), '\n\n'
    print df.region.value_counts(), '\n\n'
    

def main():
    os.chdir('/Users/stevenfelix/Dropbox/DataScience/Projects/PsychologyToday/Data/')
    filename = input("Raw data file name (must be pickled pandas DataFrame, in quotes): ")
    df = pd.read_pickle(filename)
    stateinfo  = get_stateinfo()
    df = clean_data(df, stateinfo)
    summarizedata(df)
    df.to_pickle('/Users/stevenfelix/Dropbox/DataScience/Projects/PsychologyToday/Data/therapist_profiles_clean_' + time.strftime("%m-%d") +'.pkl')
    return df



#data = test()
data = main()


