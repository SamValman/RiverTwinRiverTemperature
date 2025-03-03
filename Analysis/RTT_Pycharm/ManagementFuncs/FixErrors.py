# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 14:23:59 2024

@author: lgxsv2
"""

import pandas as pd 
import os
import math

os.chdir(r'D:\RT_temperaturePrivate\Analysis\Figures')
from genericFigureFuncs import organiseMultipleDfs
#%%
rivName='Nile'
# fpr21 = r"D:\RT_temperaturePrivate\Data\imagery\Planet\centerPixels\Rhone_2021-02-17_2021-12-03.csv"
# fpy21 = r"D:\RT_temperaturePrivate\Data\imagery\Planet\centerPixels\Yangtze_2021-01-13_2021-11-29.csv"
# fpr23 = "D:\RT_temperaturePrivate\Data\imagery\Planet\centerPixels\Rhone_2023-01-31_2023-12-25.csv"
# fpy23 = r"D:\RT_temperaturePrivate\Data\imagery\Planet\centerPixels\Yangtze_2023-01-03_2023-12-28.csv"
# fpn21 = r"D:\RT_temperaturePrivate\Data\imagery\Planet\centerPixels\Nile_2021-01-21_2021-12-16.csv"
# fpy23 = r"D:\RT_temperaturePrivate\Data\imagery\Planet\centerPixels\Yangtze_2023-01-03_2023-12-28.csv"
fpn23 = r"D:\RT_temperaturePrivate\Data\imagery\Planet\centerPixels\Nile_2023-01-03_2023-12-13.csv"
def saveCSVs(fp, riverName):
    df = pd.read_csv(fp)
    
    for index, row in df.iterrows():
        
        
        if len(row.dropna())>0:
           name = riverName+'_'+ row[0]+'.csv'
           xs, ys =[], []
           
           for i in range(len(row)-1):
               ind = i+1
               xy = row[ind]
               

               if type(xy)== str: 
                   x,y = xy.split(',')
                   x = float(x[1:])
                   y = float(y[:-1])
               elif math.isnan(xy):
                   x = 0
                   y = 0
               xs.append(x)
               ys.append(y)
           opdf = pd.DataFrame({'x':xs, 'y':ys})
           p = r'D:\RT_temperaturePrivate\Data\temperaturePoints\checkPoints_' + riverName
           path = os.path.join(p, name)
           opdf.to_csv(path)
    print('done')
            
        


# saveCSVs(fpn21, rivName)
saveCSVs(fpn23, rivName)

