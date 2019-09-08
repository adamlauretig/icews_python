import urllib.request
import requests, zipfile, io
import pandas as pd

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
cols_to_use = ['Event Date', 'Source Sectors', 'Source Country', 'Target Sectors', 'Target Country', 'Event Text']
df2 = df[cols_to_use]
df2['Event Text'].map(CAMEO_eventcodes)