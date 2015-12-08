cd Dropbox/EC41
import os
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import scipy as sp
import scipy.io
import tables
import h5py
subj = 'EC41';
blocks = 20;
datatype = [1,2,3];
dtnames = np.array(['AA','ProdAud','StimAud','Kin','Timeseries','ANIN4']);
datatype = [x-1 for x in datatype];  #fix for 0 indexing
dataFile = subj+'_B'+str(blocks)+'_'+'_'.join(list(dtnames[datatype]))+'.mat'

f = h5py.File(dataFile,'r')



d = dict(f)
v = d.values()
k = d.keys()
for c in range(len(d.keys())):
    globals().[k[c]] = v[c]


d = dict(f)
v = d.values()
for k in d.keys():
    globals().[k] = 