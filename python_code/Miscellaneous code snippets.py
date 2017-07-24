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