import urllib.request
import requests, zipfile, io
import pandas as pd


urls_to_download = ['https://dataverse.harvard.edu/api/access/datafile/:persistentId?persistentId=doi:10.7910/DVN/28075/WNOBVV']
r = requests.get(urls_to_download[0])
z = zipfile.ZipFile(io.BytesIO(r.content))
df = pd.read_csv(z.open(zipfile.ZipFile.namelist(z)[0]), sep = "\t")
df.head()