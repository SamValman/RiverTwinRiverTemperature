# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 02:01:24 2025

@author: lgxsv2
"""

import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np 

import matplotlib.dates as mdates
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import datetime
import os 

os.chdir(r'D:\RT_temperaturePrivate\Analysis\Figures')
from genericFigureFuncs import organiseMultipleDfs, smoothData, postProcessingErrorRemovalIMPORTANT, getSetVars

#%%
rn = 'Nile'
yr = '2023'
driver = 'D:'
base, rivers, years = getSetVars(driver) 

# get files 
L8 = os.path.join(base, f"{rn}LS8_{yr}.csv")
L9 = os.path.join(base, f"{rn}LS9_{yr}.csv")
As = os.path.join(base, f"{rn}Aster_{yr}.csv")
ES = os.path.join(base, f"{rn}ES_{yr}.csv")


# put into list to combine
fps = [L8,L9, As, ES]
fps = [L8, L9, As,  ES]

# manually post process for removal
df = organiseMultipleDfs(fps)
df = postProcessingErrorRemovalIMPORTANT(df, rn, yr, driver, verbose=False)



r = df.loc['2023-04-25'].dropna()    

plt.close('all')
plt.figure()
plt.scatter(r.index, r)
plt.show()


# df2 = df[df>35]

# print((df > 35).sum().sum())
# result = df[df > 35].dropna(how='all')

# # Print the index and column names of those values
# for (index, column), value in result.stack().items():
#     print(f"Index: {index}, Column: {column}, Value: {value}")
    
# r = result.loc['2022-07-14'].dropna()    

# value_to_find = 36.47048138850238
# matching_dates = df[df == value_to_find].stack().index
# print(matching_dates)

