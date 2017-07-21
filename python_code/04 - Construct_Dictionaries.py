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
    os.chdir('/Users/stevenfelix/Dropbox/DataScience/Projects/PsychologyToday/Data/')
    filename = input('Most recent pickled dataframe (with quotes): ')
    data = pd.read_pickle(filename)

    names = ['issues', 'specialties', 'treatmentorientation', 'mentalhealth']
    varinfo = decompose(data, names)

    with open("profiledict.json","w") as fd:
        json.dump(varinfo,fd)

    TFdfs = booldfs(['issues','specialties','treatmentorientation'], varinfo)

    # convert dictionary of dataframes to a dictionary of dictionarys, to store as JSON
    TFdicts = {key:TFdfs[key].to_dict() for key in TFdfs}

    with open("profilefeaturesdict_bool_dict.json","w") as fd:
        json.dump(TFdicts, fd)
        
    print ("""\n\nDictionaries completed and saved to file: \n
    profiledict.json\n
    profilefeaturesdict_bool_dict.json""")


################ run functions ############

main()
