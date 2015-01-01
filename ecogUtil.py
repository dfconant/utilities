#-------------------------------------------------------------------------------
# Name:        ecogUtil
# Purpose:     utility functions to interact with ECoG data
#
# Author:      David Cpmamt
#
# Created:     Dec 24, 2014
# Last Updated: Dec 24, 2014
#-------------------------------------------------------------------------------

import os
import numpy as np



def wav2chan(wavN):
    wav = int(str(wavN)[0]) - 1
    e = int(str(wavN)[1:])
    chan = wav*64 + e
    return chan