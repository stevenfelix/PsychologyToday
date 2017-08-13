##### Getting city, state, and zip code DataFrame ##########

from pyzipcode import ZipCodeDatabase

def get_zipcodes():
    db = ZipCodeDatabase()
    
    # get zip that is roughly in middle of the country
    kc1 = db.find_zip(city = "Kansas City")[0]
    
    # get all zips within 10000 miles of Kansas City (ie, all zips in the database)
    allzips = [z.zip for z in db.get_zipcodes_around_radius(kc1.zip, 10000)]
    
    # combine zips with city and state information,
    allzipinfo = [(db[z].zip,db[z].city,db[z].state) for z in allzips]
    df_allzipinfo = pd.DataFrame(allzipinfo, columns=['ZIP','city','state'])
    
    #remove ZIPS not part of the 50 US states
    df_allzipinfo = df_allzipinfo.loc[[(state not in ['PR','AS','VI']) for state in df_allzipinfo.state]]
    return df_allzipinfo


#### moving from unicode to str

df.loc[:,['state','city','ZIP']] = df[['state','city','ZIP']].applymap(encodestrings)

def encodestrings(x):
    if pd.isnull(x): return np.nan
    else: return x.replace(u'\xa0', u' ').replace(u'\xe9',u' ').encode()

###### regional analyses

# Process and plot data for each relevant variable
def region_plots(variable,topnum,prettytitle,ax):
    df = pd.DataFrame(features_dict[variable])
    df.index = df.index.astype(int)
    #if u'' in df.columns:
    #    df = df.drop(u'',axis=1)
    top10 = df.sum().sort_values(ascending=False)[:topnum].index
    df_top10 = df[top10]
    df_top10 = df_top10.join(data.region)
    dflong = pd.melt(frame=df_top10, id_vars='region', value_vars=top10)
    sns.barplot(x ='variable', y='value', orient = 'v',hue = 'region', data = dflong, errwidth = 2, ax = ax);
    sns.despine();
    title = "Top {} {} by Region".format(topnum,prettytitle)
    ax.set_title(title);
    ax.set_xlabel('')
    labels = ['\n'.join(i.replace('and ','').replace('or ','').split()) for i in top10]
    if variable == 'treatmentorientation': ax.set_xticklabels(labels,rotation=30)
    else: ax.set_xticklabels(labels)
    ax.set_ylabel('Proportion of providers in each \nregion endorsing response');

# Loop through 3 variables
fig,axs = plt.subplots(3,1,figsize = (15,24), sharey=True)
regionplots = [('specialties',10, "Specialties", axs[0]),
                ('issues',10, "Issues", axs[1]),
                ('treatmentorientation',12, "Treatment Orientations", axs[2])]
for variable, topnum, title, ax in regionplots:
    region_plots(variable,topnum,title,ax)
fig.tight_layout();


### graphing title X gender, two different ways

top10 = data.title.value_counts()[:9].index
data['title10'] = [title if title in top10 else 'other' for title in data.title]
top10 = data.title10.value_counts().index

# side by side
fig, ax = plt.subplots(figsize=(10,5))
d2 = data[data.gender2 != 'unknown']
dummies = pd.get_dummies(d2.gender2).join(d2.title10)
dummies_long = pd.melt(frame = dummies, id_vars = 'title10')
dummies_long.head()
sns.barplot(x ='title10', y='value', orient = 'v',hue = 'variable', order=top10, data = dummies_long, errwidth = 2, ax = ax);
labels = ['\n'.join(i.replace('and ','').replace('or ','').replace('& ','').split()) for i in top10]
ax.set_xticklabels(labels, rotation = 90)
ax.legend(bbox_to_anchor=(1.05, .65), loc=2, borderaxespad=0.)
sns.despine()

# spread / differences
vals = dummies_long.groupby(['title10','variable']).mean()
vals.reset_index(inplace=True)
diffs = vals.groupby('title10').value.apply(lambda x: np.diff(x)[0] *-1)
ax = diffs.plot(kind='bar')
ax.axhline(y=0, color = 'black');
sns.despine(bottom = True)

##### fee by gender 
recodes = {'male': 'male', 'female': 'female', 'mostly_female': 'female', 'mostly_male':'male', 'andy':'unknown','unknown':'unknown'}
data['gender2'] = data.gender.map(recodes)

def bygender(series):
    if np.issubdtype(series.dtype, np.number):
        series.hist(grid=False, by=data.gender2)
        print 'Mean {} by gender\n'.format(series.name)
        print data.groupby(data.gender2)[series.name].mean()
    else:
        series.plot()

    sns.despine()

bygender(data.fee)  


#### java script
<script>
  function code_toggle() {
    if (code_shown){
      $('div.input').hide('500');
      $('#toggleButton').val('Show Code')
    } else {
      $('div.input').show('500');
      $('#toggleButton').val('Hide Code')
    }
    code_shown = !code_shown
  }

  $( document ).ready(function(){
    code_shown=false;
    $('div.input').hide()
  });
</script>
<form action="javascript:code_toggle()"><input type="submit" id="toggleButton" value="Show Code"></form>
