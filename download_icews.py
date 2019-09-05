import urllib.request
import requests, zipfile, io
import pandas as pd

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




urls_to_download = ['https://dataverse.harvard.edu/api/access/datafile/:persistentId?persistentId=doi:10.7910/DVN/28075/WNOBVV']
r = requests.get(urls_to_download[0])
z = zipfile.ZipFile(io.BytesIO(r.content))
df = pd.read_csv(z.open(zipfile.ZipFile.namelist(z)[0]), sep = "\t")
list(df.columns)
df['CAMEO Code']