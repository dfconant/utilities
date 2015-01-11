#-------------------------------------------------------------------------------
# Name:        ecogUtil
# Purpose:     utility functions to interact with ECoG data
#
# Author:      David Cpmamt
#
# Created:     Dec 24, 2014
# Last Updated: Dec 24, 2014
#-------------------------------------------------------------------------------

import os,sys
import numpy as np
import glob
import shutil

def wav2chan(wavN):
    wav = int(str(wavN)[0]) - 1
    e = int(str(wavN)[1:])
    chan = wav*64 + e
    return chan
    

def interpJPEG():
    ind=[0];
    grad = 1;
    imgs = np.array(glob.glob('*.jpg'))
    for i in imgs: 
        ind.append(int(i[15:-4]))
        grad = ind[-1]-ind[-2]
        if grad > 1:
            for num in range(grad-1):
                print(i[0:15]+str(ind[-1]-num-1).zfill(6)+'.jpg')
                shutil.copyfile(i,i[0:15]+str(ind[-1]-num-1).zfill(6)+'.jpg')

