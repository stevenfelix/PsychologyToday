import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import pdist, cdist, squareform
from sklearn.manifold import MDS
import matplotlib.pyplot as plt

import scipy as sp
import matplotlib as mpl
import matplotlib.cm as cm

#import time
from collections import Counter
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 100)
pd.set_option('display.notebook_repr_html', True)
import seaborn as sns
sns.set_style("whitegrid")
sns.set_context("poster")
import json
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import math

os.chdir('/Users/stevenfelix/Dropbox/DataScience/Projects/PsychologyToday/')
data = pd.read_csv('./data/therapist_profiles.csv', index_col='id_num')

with open("./data/profiledict.json", "r") as fd:
    profiledict = json.load(fd)
with open("./data/profilefeatures_bool_dict.json", "r") as fd:
    featuresdict = json.load(fd)

def get_subset(df, feature_class, feature):
    df1 = pd.DataFrame(featuresdict[feature_class])
    df1.index = df1.index.astype(int)
    df1 = df.join(df1[feature])
    return df1[df1[feature] == 1]

#### Let's say we're looking for depression therapists
#### We've narrowed down our list.  Now what? How do we chooes? What are the relevant
#### Dimensions along which we should look?
df = get_subset(data,'specialties','depression')
freeresponse = df.profile
freeresponse.dropna(inplace=True)

# exract features from text (ie word frequencies)
# -- possible decisions: use raw counts vs. idf
# -- use bi-grams for more information?

# fit tokenizer
tfidf = TfidfVectorizer(stop_words = 'english', max_features=300) # play with max features
y = tfidf.fit_transform(freeresponse)

y.toarray().shape
# compute similarity/dissimilarity matrix
dist = squareform(pdist(y.toarray(), 'jaccard'))

# conduct MDS
seed = np.random.RandomState(seed=3)
mds = MDS(n_components=2, max_iter=100,  random_state=seed,
                   dissimilarity="precomputed", n_jobs=1)

try:
    mds.fit(dist)
except ValueError:
    # remove the row and column (symmetric) with NaN
    x = pd.DataFrame(dist)
    ind = x.iloc[0,:][x.iloc[0,:].isnull()].index
    x.drop(ind, axis = 1,inplace=True)
    x.drop(ind, axis = 0,inplace=True)
    dist = np.asarray(x)
    mds.fit(dist)


pos = mds.embedding_

# plot MDS / try to understand the dimensions
s = 100
plt.scatter(pos[:, 0], pos[:, 1], color='turquoise', lw=.1, label='MDS', alpha=.2)

a = 2
a







#### preparing issues data
issues = pd.DataFrame(featuresdict['issues'])
Counter(issues['none'])[1] # number of providers who listed NO issues whatsoever, 
                            #lets remove then

## dealing with the 'none's
issues.drop(issues.none[issues.none == 1].index, inplace = True)
issues.drop('none',inplace= True, axis = 1)
a = issues.sum(axis=1) # total number of issues per provider
a[a == 0].count() # number of providers with no listed issues in their pro
issues['other'] = 0
issues['other'][a==0] = 1
Counter(issues['other']) # should equal 7