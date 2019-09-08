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

# agents/sectors ----
agentnames = "agentnames.txt"
sectornames = {}
fin = open(agentnames,'r') 
line = fin.readline()
while len(line) > 0:
    part = line.split("\t")
    sectornames[part[0]] = part[1]
    line = fin.readline()

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


urls_to_download = ['https://dataverse.harvard.edu/api/access/datafile/:persistentId?persistentId=doi:10.7910/DVN/28075/WNOBVV']
r = requests.get(urls_to_download[0])
z = zipfile.ZipFile(io.BytesIO(r.content))
df = pd.read_csv(z.open(zipfile.ZipFile.namelist(z)[0]), sep = "\t")
list(df.columns)
df['Event Date']
df['Source Name'].head()
df['Source Sectors'].head()
df['Source Country'].head()
df['CAMEO Code'].head()
df['Intensity'].head()
df['Event Code'] = df['Event Text'].map(CAMEO_eventcodes)
df['Source Sector Code'] = df['Source Sectors'].map(sectornames)
df['Target Sector Code'] = df['Target Sectors'].map(sectornames)
df['Source Country Code'] = df['Source Country'].map(countrycodes)
df['Target Country Code'] = df['Target Country'].map(countrycodes)
cols_to_use = ['Event Date', 'Event Text', 'Event Code', 'Source Sector Code', 'Target Sector Code', 'Source Country Code', 'Target Country Code']
df2 = df[cols_to_use]
df2['Event Short'] = df2['Event Code'].str[:2]
df2['Event Short'] = df2['Event Short'].astype('int')
df2['Quad Count'] = np.select(
    [
        df2['Event Short'].between(0, 5, inclusive = True),
        df2['Event Short'].between(6, 8, inclusive = True),
        df2['Event Short'].between(9, 13, inclusive = True),
        df2['Event Short'].between(14, 20, inclusive = True),
    ],
    ['Verbal Cooperation', 'Material Cooperation', 'Verbal Conflict', 'Material Conflict'], 
    default = 0
)