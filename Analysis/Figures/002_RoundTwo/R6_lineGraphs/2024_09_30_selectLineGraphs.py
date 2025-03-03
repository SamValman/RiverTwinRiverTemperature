# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 14:04:30 2024

@author: lgxsv2
"""

import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np 
import datetime
import os 

os.chdir(r'D:\RT_temperaturePrivate\Analysis\Figures')
from genericFigureFuncs import organiseMultipleDfs, smoothData, postProcessingErrorRemovalIMPORTANT

def SimpleLine(df, relative='T'):
    
    plt.figure()
    for index, row in df.iterrows():
        # print(index)
        if index == datetime.datetime.strptime('2022-08-04 00:00:00', '%Y-%m-%d %H:%M:%S'):
            row = row[row > 30]
        # remove "no" results
        row = row[row > 0]
        x = row.index.astype(int) # Column names as integers (0 to 99)
        if len(relative)>3:
            y = list(row.values-row.mean())
            plt.ylim(-2,4)

        else:
            y = row.values
        # get label 
        lab = index.strftime('%Y-%m-%d')
        plt.plot(x,y, label=lab)
        plt.xlabel('Distance downstream (km)')
        plt.ylabel(f'{relative}emperature ($^o$c)')  
    
    plt.legend()
    plt.show()













#%%

ls8_Rhone = r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneLS8_2022.csv"
ls9_Rhone = r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneLS9_2022.csv"
A_Rhone = r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneAster_2022.csv"

riverName = 'Rhone'
year = 2022
fps = [ls8_Rhone, ls9_Rhone, A_Rhone]


# ls8_Yangtze = r"D:\RT_temperaturePrivate\Data\temperaturePoints\YangtzeLS8_2022.csv"
# ls9_Yangtze = r"D:\RT_temperaturePrivate\Data\temperaturePoints\YangtzeLS9_2022.csv"
# A_Yangtze = r"D:\RT_temperaturePrivate\Data\temperaturePoints\YangtzeAster_2022.csv"
# riverName = 'Yangtze'
# year = 2022
# fps = [ls8_Yangtze, ls9_Yangtze, A_Yangtze]


# ls8_Nile = r"D:\RT_temperaturePrivate\Data\temperaturePoints\NileLS8_2022.csv"
# ls9_Nile = r"D:\RT_temperaturePrivate\Data\temperaturePoints\NileLS9_2022.csv"
# A_Nile = r"D:\RT_temperaturePrivate\Data\temperaturePoints\NileAster_2022.csv"
# riverName = 'Nile'
# year = 2022
# fps = [ls8_Nile, ls9_Nile, A_Nile]



df = organiseMultipleDfs(fps)
df = postProcessingErrorRemovalIMPORTANT(df, riverName, year, driver='D:')

#%%

# get the number per row 
nrow = df.notna().sum(axis=1)

best = nrow[nrow == nrow.max()]



#%% get the top 10%
#####

nrowSorted = nrow.sort_values(ascending=False)

#  number of rows top 10%
topTen = int(len(nrowSorted) * 0.10)

# Select 
topTen = nrowSorted.head(topTen)

df10 = df.loc[topTen.index]  

#%%
### plot these best ones normally first
plt.close('all')
SimpleLine(df10)
# SimpleLine(df)


#%%
# plot averages

# SimpleLine(df, relative='Relative t')
SimpleLine(df10, relative='Relative t')

















