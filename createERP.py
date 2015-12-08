#createERP.py


import os
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import scipy as sp
import scipy.io

def evnt2ERP(evnt):
    
    print('a')


def mat2ERP(Ymat):
    mat = sp.io.loadmat(Ymat);
    D = mat['neuralY']
    return D
    
    
def plotERP(D,onset,fs):
#Given a electrodesXtimeXtrials matrix, generates ERPs with 1 sec on 
#either side of the (user defined) onset
#Transposed from Ben Dichter's plotERP.m
#David Conant 12/17/14 

    ERP = np.nanmean(D,axis=2);
    ERPerr = np.nanstd(D,axis=2)/D.shape[2];
    
    minall = np.nanmin(D)
    maxall = np.nanmax(D)
    
    ind = floor(np.arange(onset-fs,onset+fs,1))
    ind.astype(int)
    t = ind/200.0;
    
    for e in range(256):
        fig, axes = plt.subplots(figsize=(36,24))
        ax = fig.add_subplot(16,16,e)
        d = ERP[e,ind]
        err = ERPerr[e,ind]
        plt.plot(t,d)
        plt.fill_between(t,d-err,d+err)
        plt.ylim([minall,maxall])
        fig.subplots_adjust(hspace=.05) # Put some space between the plots for ease of viewing
        
    #rcParams['font.family'] = 'sans-serif'
    #rcParams['text.usetex'] = False
    #rcParams['axes.labelsize'] = 10
    #rcParams['xtick.labelsize'] = 10
    #rcParams['ytick.labelsize'] = 10
    #rcParams['legend.fontsize'] = 10
        
    #savefig("EC34_Vowel_ERPs.pdf") 
    
