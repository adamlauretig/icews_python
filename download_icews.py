import urllib.request
import requests, zipfile, io
import pandas as pd
import numpy as np
# event codes ----
CAMEO_codefile = "CAMEO_codefile.txt"  # translates event text to CAMEO event codes
CAMEO_eventcodes = {}
fin = open(CAMEO_codefile,'r') 
caseno = 1
line = fin.readline()
while len(line) > 0:
    if line.startswith('LABEL'):
        part = line[line.find(' ')+1:].partition(' ') # split text on space, w/ text after "LABEL: "
        CAMEO_eventcodes[part[2][:-1]] = part[0][:-1] # assign to dict
        print(CAMEO_eventcodes[part[2][:-1]])
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
sectornames = {k:(v if v in agent_codes else 'OTH') for k,v in sectornames.items()}
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
    r = requests.get(urls[year])
    z = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_csv(z.open(zipfile.ZipFile.namelist(z)[0]), sep = "\t")
    # list(df.columns)
    df['Event Code'] = df['Event Text'].map(CAMEO_eventcodes)

    # [[dictionary.get(item, item) for item in lst] for lst in word_list]
    # dfCombined.loc[dfCombined[col].isnull(), 'col']
    df.loc[df['Source Sectors'].notnull(),'Source Sector Code'] = [[
        sectornames.get(item, item) for item in lst] for lst in df.loc[df[
            'Source Sectors'].notnull(), 'Source Sectors'].str.split(',') ]
    # df['Source Sectors', ]
    # df['Source Sector Code'] = reduce_sectors(df['Source Sector Code'])
    # df['Target Sector Code'] = df['Target Sectors'].map(sectornames)
    df.loc[df['Target Sectors'].notnull(),'Target Sector Code'] = [[
        sectornames.get(item, item) for item in lst] for lst in df.loc[df[
            'Target Sectors'].notnull(), 'Target Sectors'].str.split(',') ]

    # df['Target Sector Code'] = reduce_sectors(df['Target Sectors'])
    df['Source Country Code'] = df['Source Country'].map(countrycodes)
    df['Target Country Code'] = df['Target Country'].map(countrycodes)
    df['Event Short'] = df['Event Code'].str[:2]
    df['Event Short'] = df['Event Short'].astype('int')
    df['Quad Count'] = np.select([
        df['Event Short'].between(0, 5, inclusive = True),
        df['Event Short'].between(6, 8, inclusive = True),
        df['Event Short'].between(9, 13, inclusive = True),
        df['Event Short'].between(14, 20, inclusive = True),],
        ['Verbal Cooperation', 'Material Cooperation', 'Verbal Conflict', 'Material Conflict'], 
        default = 0
    )
    cols_to_use = ['Event Date', 'Event Text', 'Event Code', 'Source Sector Code', 
    'Target Sector Code', 'Source Country Code', 'Target Country Code', 'Quad Count']
    if deduplicate == True:
        df2 = df[cols_to_use].drop_duplicates()
        
    else:
        df2 = df[cols_to_use]

    if keep_sectors != True:
        df3 = df2.groupby(['Event Date', 'Source Country Code', 'Target Country Code', 'Quad Count']).size()
    else:
        df3 = df2.groupby(['Event Date', 'Source Country Code', 'Target Country Code', 'Source Sector Code', 
        'Target Sector Code','Quad Count']).size()
       
    return df3