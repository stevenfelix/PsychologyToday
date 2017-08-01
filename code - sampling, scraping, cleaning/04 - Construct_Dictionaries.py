"""
File:       04 - Construct_Dictionaries_ListData.py
Author:     Steven Felix
Purpose:    There are 4 variables in the raw data that consist of lists. They include each therapist's
            specialities, treatment orientations, issues treated, and mental health issues treated. To
            process these lists and put them into a form that is useable for data analysis, this script
            will output two files:
            
            profilefeaturesdict_bool_dict.json - this is a dictionary of dataframes. There is one dataframe
                                                 for each of the 4 list variables. Each dataframe consists of
                                                 a column for any list-item that had over 20 responses. And each
                                                 column is is 0 or 1s, where 1 = provider endorsed.
            
            profiledict.json - this is a dictionary of dictionaries. THere are 4 sub-dictionarious -- one of each
                               of the list variables. And each subdictionary consists of two keys-value pairs:
                               - counts = a Counter object (ie a dictionary) giving the number of 
                                          providers endorsing every possible item from the respectivel list
                               - provider_lists = a dictionary mapping providers to a list of their services/specialties

"""

import pandas as pd
import numpy as np
from collections import Counter
import json

################ functions ################ 

def series_info(df, varname):
    """ 
    Purpose: This function takes provides summary information about variables in the dataset
            that consist of lists (e.g., of services, specialities, orientations)
    
    Input: Pandas df and variable name (the variable itelf )
        
    Returns: dictionary consisting of the following information:
        - counts = a Counter object (ie a dictionary) giving the number of 
          providers endorsing each service/specialty
        - provider_lists = a dictionary mapping providers to a list of their services/specialties"""
    
    dic = {}
    df[varname].fillna('None', inplace = True)
    list_of_lists = [list_str.lower().split(", ") for list_str in df[varname]]
    dic['provider_lists'] = dict(zip(df.index, list_of_lists))
    onelist = []
    [onelist.extend(l) for l in list_of_lists];
    dic['counts'] = Counter(onelist)
    return dic

def decompose(df, varlist):
    """
    Input: pandas data frame, and a list of variables to get info on
    
    Output: a dictionary of dictionaries, one for each variable in varlist"""
    
    dic = {}
    for var in varlist:
        dic[var] = series_info(df, var)
    return dic


def booldfs(variables, varinfo):
    """
    Constructs a dictionary of multiple dataframes. Each DataFrame consists
    of columns referring to possible values of a specific variable (e.g., specialties).
    Values are 0 = provider did not endorse this value, or 1 = provider endorsed this value).
    There is one dataframe for each variable supplied.
    Chosen values of variables to include are only those for which more than 10 providers endorsed it.
    """
    dic = {}
    for variable in variables:
        common = [k for k in varinfo[variable]['counts'] if varinfo[variable]['counts'][k] > 10]
        df = pd.DataFrame(columns=common, index = varinfo[variable]['provider_lists'].keys())
        df.fillna(0, inplace = True)
        for name in df.index:
            for item in varinfo[variable]['provider_lists'][name]:
                if item in df.columns:            # need to make sure we don't just create a new column
                    df.loc[name,item] = 1
                else: continue
        dic[variable] = df
    return dic


def main():
    data = pd.read_csv('./data/therapist_profiles.csv', index_col='id_num')
    names = ['issues', 'specialties', 'treatmentorientation', 'degrees']
    varinfo = decompose(data, names)

    with open("./data/profiledict.json","w") as fd:
        json.dump(varinfo,fd)

    # 'TF' = True/False, stored as 0's and 1's as indication of whether provider endorsed item
    TFdfs = booldfs(['issues','specialties','treatmentorientation','degrees'], varinfo)

    # convert dictionary of dataframes to a dictionary of dictionarys, to store as JSON
    TFdicts = {key:TFdfs[key].to_dict() for key in TFdfs}

    with open("./data/profilefeaturesdict_bool_dict.json","w") as fd:
        json.dump(TFdicts, fd)
        
    print ("""\n\nDictionaries completed and saved to file: \n
    profiledict.json\n
    profilefeaturesdict_bool_dict.json""")


################ run functions ############

main()
