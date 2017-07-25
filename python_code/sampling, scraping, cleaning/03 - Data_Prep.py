"""
File:       03 - Data_Prep.py
Author:     Steven Felix
Purpose:    Given a raw dataframe from '02-Scrape_Data.py', this file checks for duplicates,
            deals with encoding issues (so we can save as CSV), drops profiles with addresses,
            not in the 50 US states (and DC), and makes sure numeric variables have the appropriate,
            dtype. A CSV file is output.

"""

import pandas as pd
import numpy as np
import re
from collections import defaultdict
import time

def clean_data(data, statedict):
    #remove duplicates
    df2 = data[[(not i) for i in data.id_num.duplicated()]]
    df2 = df2.reset_index().drop(u'index',axis =1)

    #encode column names as asci
    df2.columns = [c.encode('ascii') for c in df2.columns]
    
    # drop rows with non 50-states / DC
    df2 = df2[[(state in statedict['all_states']) for state in df2.state]]
    
    # remove unicode errors
    # first, find out which columns have unicode
    unicols = []
    for col in df2:
        if df2[col].apply(lambda x: isinstance(x,unicode)).any():
            unicols.append(col)
    unicols.remove('profile')
    
    # second, encode columns
    df2.loc[:,unicols] = df2[unicols].applymap(encodestrings)
    df2.loc[:,'profile'] = df2['profile'].apply(encodeprofile)
    
    # add in region
    df2['region'] = [statedict[state] for state in df2.state]
    
    del df2['sexualitynum'] # few therapists include this
    del df2['specialtiesnum'] # PT limits to 3 specialities, so most everyone lists 3
    
    df2 = df2[df2.title != 'treatment facility']
    df2 = df2.reset_index().drop('index',axis = 1)#.set_index('name')
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


def encodestrings(x):
    return np.nan if pd.isnull(x) else x.replace(u'\xa0', u' ').encode()

#else: return (x.replace(u'\xa0', u' ').replace(u'\xe9',u' ').replace(u'\xae',u' ').replace(u'\xf3',u' ')
#                .replace(u'\xe1', u' ').replace(u'\xf1', u' ')).encode()

def encodeprofile(x):
        return repr(x).encode() if isinstance(x,unicode) else x


def summarizedata(df):
    print '\n\nShape: ', df.shape, '\n\n'
    print df.dtypes, '\n\n'
    print df.state.value_counts(), '\n\n'
    print df.region.value_counts(), '\n\n'
    

def main():
    filename = input("Raw data file name (must be pickled pandas DataFrame, in quotes): ")
    df = pd.read_pickle('./data/'+filename)
    stateinfo  = get_stateinfo()
    df = clean_data(df, stateinfo)
    summarizedata(df)
    #df.to_pickle('/Users/stevenfelix/Dropbox/DataScience/Projects/PsychologyToday/Data/therapist_profiles_clean_' + time.strftime("%m-%d") +'.pkl')
    return df

##########

#data = test()
data = main()
data.to_csv('./data/therapist_profiles.csv')
