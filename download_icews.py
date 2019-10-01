import urllib.request
import requests, zipfile, io
import pandas as pd
import numpy as np
import pickle
# event codes ----

# agent cleaning code taken/modified from Phil Schrodt (https://github.com/openeventdata/text_to_CAMEO)
CAMEO_codefile = "CAMEO_codefile.txt"  # translates event text to CAMEO event codes
CAMEO_eventcodes = {}
fin = open(CAMEO_codefile,'r') 
caseno = 1
line = fin.readline()
while len(line) > 0:
    if line.startswith('LABEL'):
        part = line[line.find(' ')+1:].partition(' ') # split text on space, w/ text after "LABEL: "
        CAMEO_eventcodes[part[2][:-1]] = part[0][:-1] # assign to dict
        # print(CAMEO_eventcodes[part[2][:-1]])
        caseno += 1
    #	if caseno > 32: break   # debugging exit 		
    line = fin.readline()
fin.close()

# agents/sectors ----
agentnames = "agentnames.txt"
sectornames = {}
fin = open(agentnames,'r') 
line = fin.readline()
while len(line) > 0:
    part = line.split("\t")
    sectornames[part[0]] = part[1]
    line = fin.readline()
fin.close()
agent_codes = ['GOV','MIL','REB','OPP', 'PTY', 'COP',
'JUD','SPY','IGO','MED','EDU','BUS','CRM','CVL','---']
# using a dict comprehension here
sectornames = {k:(
    v if v in agent_codes else 'OTH') for k,v in sectornames.items()}
sectornames['nan']  = 'OTH'
# countrynames ----
countrynames = "countrynames.txt"
countrycodes = {}
fin = open(countrynames, 'r')
line = fin.readline()
COW = False
while len(line) > 0:
    part = line.split("\t")
    if COW == False:
        countrycodes[ part[0] ] = part[1]
    else:
        countrycodes[ part[0] ] = part[2][:-1]
    line = fin.readline()
fin.close()

# urls ----
icews_urls = 'icews_files.txt'
urls = {}
fin = open(icews_urls, 'r')
line = fin.readline()
while len(line) > 0:
    part = line.split("\t")
    urls[ part[0]] = part[1]
    line = fin.readline()
fin.close()


def download_icews(year, deduplicate = True, keep_sectors = False):
    """ A function to download and clean ICEWS data files from Harvard's Dataverse
    Arguments:
        year: a string matching a year in 'icews_urls'
        deduplicate: a Boolean. should events be de-duplicated by day?
        keep_sectors: a Boolean. Should the final dataframe include sector variables? """ 
    r = requests.get(urls[year])
    z = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_csv(z.open(zipfile.ZipFile.namelist(z)[0]), sep = "\t")
    # list(df.columns)
    df['Event Code'] = df['Event Text'].map(CAMEO_eventcodes)
    df.loc[df['Source Sectors'].notnull(),'Source Sector Code'] = [[
        sectornames.get(item, item) for item in lst] for lst in df.loc[df[
            'Source Sectors'].notnull(), 'Source Sectors'].str.split(',') ]
    df.loc[df['Source Sector Code'].notnull(),'Source Sector Code'] = [
        ','.join(lst) for lst in df.loc[df['Source Sector Code'].notnull(), 
        'Source Sector Code']]
    df.loc[df['Target Sectors'].notnull(),'Target Sector Code'] = [[
        sectornames.get(item, item) for item in lst] for lst in df.loc[df[
            'Target Sectors'].notnull(), 'Target Sectors'].str.split(',') ]
    df.loc[df['Target Sector Code'].notnull(),'Target Sector Code'] = [
        ','.join(lst) for lst in df.loc[df['Target Sector Code'].notnull(), 
        'Target Sector Code']]
    df.loc[df['Source Country'].notnull(),'Source Country Code'] = [[
        countrycodes.get(item, item) for item in lst] for lst in df.loc[df[
            'Source Country'].notnull(), 'Source Country'].str.split(',') ]
    df.loc[df['Source Country Code'].notnull(),'Source Country Code'] = [
        ','.join(lst) for lst in df.loc[df['Source Country Code'].notnull(), 
        'Source Country Code']]            
    df.loc[df['Target Country'].notnull(),'Target Country Code'] = [[
        countrycodes.get(item, item) for item in lst] for lst in df.loc[df[
            'Target Country'].notnull(), 'Target Country'].str.split(',') ]
    df.loc[df['Target Country Code'].notnull(),'Target Country Code'] = [
        ','.join(lst) for lst in df.loc[df['Target Country Code'].notnull(), 
        'Target Country Code']]  
    df['Event Short'] = df['Event Code'].str[:2]
    df['Event Short'] = df['Event Short'].astype('int')
    df['Quad Count'] = np.select([
        df['Event Short'].between(0, 5, inclusive = True),
        df['Event Short'].between(6, 8, inclusive = True),
        df['Event Short'].between(9, 13, inclusive = True),
        df['Event Short'].between(14, 20, inclusive = True),],
        ['Verbal Cooperation', 'Material Cooperation', 
        'Verbal Conflict', 'Material Conflict'], 
        default = 0
    )
    cols_to_use = ['Event Date', 'Event Text', 'Event Code', 
    'Source Sector Code', 'Target Sector Code', 'Source Country Code', 
    'Target Country Code', 'Quad Count']
    if deduplicate == True:
        df2 = df[cols_to_use].drop_duplicates()
        
    else:
        df2 = df[cols_to_use]

    if keep_sectors != True:
        df3 = df2.groupby(['Event Date', 'Source Country Code', 
        'Target Country Code', 'Quad Count']).size()
    else:
        df3 = df2.groupby(['Event Date', 'Source Country Code', 
        'Target Country Code', 'Source Sector Code', 
        'Target Sector Code','Quad Count']).size()
       
    return df3


# df_1995 = download_icews('1995')
# df_1996 = download_icews('1996')

# A loop through all the urls to create a dictionary of ICEWS events,
# and then, converting this dictionary to a dataframe
icews_sets = {}
dates = list(urls.keys())
for i in dates:
    print(i + "\n")
    icews_sets[i] = download_icews(i)

icews_df = pd.DataFrame.from_dict(icews_sets)
file_to_use = open("icews_df.obj", 'wb')
pickle.dump(icews_df, file_to_use)
file_to_use.close()