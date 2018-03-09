from __future__ import division, print_function
import os
import requests
import pandas as pd
from io import StringIO, BytesIO
import numpy as np

def get_catalog(name, basepath="kepdata/"):
   fn = os.path.join(basepath, "{0}.h5".format(name))
   if os.path.exists(fn):
       return pd.read_hdf(fn, name)
   if not os.path.exists(basepath):
       os.makedirs(basepath)
   print("Downloading {0}...".format(name))
   url = ("http://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/"
          "nph-nstedAPI?table={0}&select=*").format(name)
   r = requests.get(url)
   if r.status_code != requests.codes.ok:
       r.raise_for_status()
   fh = BytesIO(r.content)
   df = pd.read_csv(fh)
   df.to_hdf(fn, name, format="t")
   return df
   

stlr = get_catalog("q1_q16_stellar")
ngc6791 = np.genfromtxt('NGC6791_params.csv', delimiter=',', names=True, dtype=None)
inds = [np.where(stlr.kepid == k)[0] for k in ngc6791['KIC']]

stlr_cols = []
for col in stlr.columns:
    if 'cdpp' not in col:
        continue
    stlr_cols.append(col)
    
f = open('NGC6791_cdpps.csv', 'w')
f.write('KIC, 2MASS')
for c in stlr_cols:
    f.write(', {0}'.format(c))
f.write('\n')
for i,n in enumerate(ngc6791):
    f.write('{0}, {1}'.format(n[0], n[1]))
    try:
        ind = np.where(stlr.kepid == n[0])[0][0]
        print(stlr.kepid[ind])
        for c in stlr_cols:
            f.write(', {0}'.format(getattr(stlr, c)[ind]))
        f.write('\n')
    except:
        for c in stlr_cols:
            f.write(', ')
        f.write('\n')
f.close()