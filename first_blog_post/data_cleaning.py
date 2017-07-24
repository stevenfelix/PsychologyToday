import numpy as np
import pandas as pd

os.chdir('/Users/stevenfelix/Dropbox/DataScience/Projects/PsychologyToday/Data/')
data = pd.read_pickle('therapist_profiles_clean_07-20.pkl')

data.iloc[0,:]
data.reset_index(inplace=True)
data.reset_index(inplace=True)
data.columns