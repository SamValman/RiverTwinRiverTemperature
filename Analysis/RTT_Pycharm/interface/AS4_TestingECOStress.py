# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 12:28:07 2024

@author: lgxsv2
"""

###############################################################################
# there are 5 steps to using ECOSTRESS in This study. 
#1. download ecostress imagery using Harddrive_PreProcessing
#2. sort dates out in ECOSTRESS Folder
#3. feed ecostress dates into processing.py - might need to add the dates to the landsat output files too
#4. get WST 
#5. Plot as you would
###############################################################################












import sys
import pandas as pd
driver = 'D:'

sys.path.append(driver + '\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\ManagementFuncs')
sys.path.append(driver + '\\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\TemperatureFuncs')
sys.path.append(driver + '\\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\InterfaceFunctions')


from ProcessWST import ProcessWST
import time
from fileUtils import changeExtractionDate
import Harddrive_PreProcessing as hpp







#%% Section 1 

# AOI_fp = r"D:\RT_temperaturePrivate\Data\AoI\FinalBuffers\Rhone.geojson"
# AOI_fp = r"D:\RT_temperaturePrivate\Data\AoI\FinalBuffers\Yangtze.geojson"
AOI_fp = r"D:\RT_temperaturePrivate\Data\AoI\FinalBuffers\Nile.geojson"


roi = hpp.sortAOIForECOSTRESS(AOI_fp)

urls_all, df_all = hpp.getAssetList(('2021-01-01','2023-12-31'),[], roi)


### If we want coincident dates - there are few
# OtherSatDates = r"D:\RT_temperaturePrivate\Data\imagery\Planet\centerPixels\RhonTest2.csv"
# OtherSatDates = list(pd.read_csv(OtherSatDates)['date'])
# urls, df = getAssetList(('2022-01-01','2022-12-31'), OtherSatDates, roi)
# print(f'Other satellites provide {len(OtherSatDates)} \n Ecostress has {len(df_all)} \n of which {len(df)} are coincident')
uniqueDates = df_all['start_datetime'].dt.date.unique()

print(f'There are {len(df_all)} total images from {len(uniqueDates)} days')
print('Starting download')
# hpp.downloadEcostress(urls_all, 'D:', 'Nile')
print('Download complete')

#%%

# SORT OUT ECOSTRESS FOLDER - after this step need to manually merge because its easier. 

folderp = r"D:\RT_temperaturePrivate\Data\imagery\ECOSTRESS\Rhone"
# bn  = hpp.sortNamingConvention(folderp)        

folderp = r"D:\RT_temperaturePrivate\Data\imagery\ECOSTRESS\Yangtze"
# bn  = hpp.sortNamingConvention(folderp)        

folderp = r"D:\RT_temperaturePrivate\Data\imagery\ECOSTRESS\Nile"
# bn  = hpp.sortNamingConvention(folderp)        


#%%


















































#%% vars

riverName = 'Rhone' 
driver = 'D:'
satellites = ['EcoStress']
# locations = pd.DataFrame({'date':['2022-12-05']}, index=['2022-12-05'])
# locations = r"D:\RT_temperaturePrivate\Data\imagery\Planet\centerPixels\Nile_2022-01-01_2022-12-10.csv"
locations = "D:\RT_temperaturePrivate\Data\imagery\Planet\centerPixels\RhonTest2.csv"


#%%

dfList, outSat = ProcessWST(driver, riverName, locations, satellites, save=False, op='')

#%%
opfn = r'D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneEcostress_2022.csv'
dfList[0].to_csv(opfn)



#%%

# quick comparison
eco = dfList[0]
ls8 = pd.read_csv(r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneLS8_2022.csv")
ls9 = pd.read_csv(r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneLS9_2022.csv")
a = pd.read_csv(r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneASTER_2022.csv")

eco = eco.iloc[56]
ls8 = ls8.iloc[56]
ls9 = ls9.iloc[56]
a = a.iloc[56]





