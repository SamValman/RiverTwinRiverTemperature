# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 11:29:48 2024

@author: lgxsv2
"""
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import scipy
import os 


os.chdir(r'D:\RT_temperaturePrivate\Analysis\Figures')
from genericFigureFuncs import organiseMultipleDfs, postProcessingErrorRemovalIMPORTANT

#%%
# data funcs 
def getData(base, riverName, year, driver='D:'):
    
    fp8 = os.path.join(base, riverName+'LS8_'+year+'.csv')
    fp9 = os.path.join(base, riverName+'LS9_'+year+'.csv')
    fpA = os.path.join(base, riverName+'ASTER_'+year+'.csv')

    fps =[fp8, fp9, fpA]
    df = organiseMultipleDfs(fps)
    df = postProcessingErrorRemovalIMPORTANT(df, riverName, year, driver)
    
    
 
    
    return df

#%%

def DaysOver30heatmap(df):
    
    binDf = (df > 30).sum(axis=0)
    # print(binDf)
    plt.figure(figsize=(10, 8))
    plt.imshow(binDf, cmap='Reds', aspect='auto')

    # sns.heatmap(binDf, cmap="Reds", cbar=False)
    plt.title("Heatmap of Days and Sites with Temperature Over 30°C")
    plt.colorbar(label='Over 30°C')

    plt.xlabel("Days")
    plt.ylabel("Sites")
    plt.show()
    
def DaysOver30(df):
    
    plt.figure()
    binDf = (df > 30).sum(axis=0)
    
    plt.bar(binDf.index, binDf)
    
    plt.ylabel("Days over 30 $^o$c")
    plt.xlabel("Downstream Km")
    plt.xticks(rotation=90)  

    plt.show()
    
def daysOver30Panel(base, year='2022'):
    
    Rhone = getData(base, 'Rhone', year, driver='D:')
    Nile = getData(base, 'Nile', year, driver='D:')
    Yangtze = getData(base, 'Yangtze', year, driver='D:')

    ## bin into over 30s
    binR = (Rhone > 30).sum(axis=0)
    binN = (Nile > 30).sum(axis=0)
    binY = (Yangtze > 30).sum(axis=0)
    
    
    fig, ax = plt.subplots(3,1, sharex=True)
    

    
    
    # labels
    fig.text(0.04, 0.5, "Days with water surface temperature over 30 $^o$c", va='center', rotation='vertical', fontsize=12)
    fig.text(0.45, 0.05, "Downstream Kilometre", va='center', fontsize=12)
    ax[0].set_ylabel("Rhône")
    ax[1].set_ylabel("Nile")
    ax[2].set_ylabel("Yangtze")

    
    ## plot these bars
    ax[0].bar(binR.index, binR, color='gray')
    ax[1].bar(binN.index, binN, color='gray')
    ax[2].bar(binY.index, binY, color='gray')
    
    ## ticks
    plt.xlim(-1,100)
    xtick_positions = np.arange(0, 100, 5)  # 0, 9, 19, ..., 99
    ax[2].set_xticks(xtick_positions)
    ax[2].set_xticklabels([str(i) for i in xtick_positions], rotation=90)
    
    for i in [0,1,2]:
        ax[i].set_ylim(0, 12)
        # ax[i].set_yticks(range(0, 13))
        ax[i].set_yticks([0, 4, 8, 12])


    
    plt.show()
    
#%%
# ls8_Rhone = r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneLS8_2022.csv"
# ls9_Rhone = r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneLS9_2022.csv"
# df = organiseMultipleDfs([ls9_Rhone, ls8_Rhone])
# df = postProcessingErrorRemovalIMPORTANT(df, 'Rhone', 2022, driver='D:')

#%%
base = 'D:' + '/RT_temperaturePrivate/Data/temperaturePoints'
plt.close('all')
daysOver30Panel(base)
# DaysOver30(df)
# DaysOver30heatmap(df)