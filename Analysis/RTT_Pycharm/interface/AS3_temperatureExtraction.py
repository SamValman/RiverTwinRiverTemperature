# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 14:02:08 2024

@author: lgxsv2
"""

import sys

driver = 'D:'

sys.path.append(driver + '\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\ManagementFuncs')
sys.path.append(driver + '\\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\TemperatureFuncs')
sys.path.append(driver + '\\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\InterfaceFunctions')


from ProcessWST import ProcessWST
import time
#%% VAR hard code
driver = 'D:'
satellites = ['EcoStress']#['Landsat8','Landsat9','Aster']

# locations = r"D:\RT_temperaturePrivate\Data\imagery\Planet\centerPixels\Rhone_2022-02-05_2022-11-26.csv"

# locations = r"D:\RT_temperaturePrivate\Data\imagery\Planet\centerPixels\Yangtze_2021-01-13_2021-11-29.csv"
locations = r"D:\RT_temperaturePrivate\Data\imagery\Planet\centerPixels\Yangtze_ES.csv"
riverName = 'Yangtze'
year = 2023

#%%
st = time.time()


dfList, outSat = ProcessWST(driver, riverName, locations, satellites, save=False, op='')
et = time.time()
#%%
print(f'Completed temperature extraction for {riverName}')
print(f'It took a total time of {int((et-st)/60)} minutes: \n starting at {st} and ending at {et} for a total of {len(dfList[0])} dates')

opfn = f'D:/RT_temperaturePrivate/Data/temperaturePoints/{riverName}_ES.csv'
dfList[0].to_csv(opfn)
def saveTempOutputs(dfList, riverName, year):
    
    opfn = f'D:/RT_temperaturePrivate/Data/temperaturePoints/{riverName}LS8_{year}.csv'
    dfList[0].to_csv(opfn)
    
    opfn = f'D:/RT_temperaturePrivate/Data/temperaturePoints/{riverName}LS9_{year}.csv'
    dfList[1].to_csv(opfn)
    
    opfn = f'D:/RT_temperaturePrivate/Data/temperaturePoints/{riverName}Aster_{year}.csv'
    dfList[2].to_csv(opfn)
    print('Saved')


# saveTempOutputs(dfList, riverName, year)







#*****************************************************************************#
# Next river

#%% VAR hard code
# riverName = 'Danube'
# driver = 'D:'
# locations = r"D:\RT_temperaturePrivate\Data\imagery\Planet\centerPixels\Danube_2022-07-18_2022-08-25.csv"

# satellites = ['Landsat8', 'Landsat9']#, 'Aster'] 

# #%%
# st = time.time()


# dfList2, outSat = ProcessWST(driver, riverName, locations, satellites, save=False, op='')
# et = time.time()
# #%%
# print(f'Completed temperature extraction for {riverName}')
# print(f'it took a total time of {et-st}: \n starting at {st} and ending at {et} for a total of {len(dfList[0])} dates')
# opfn = r'D:\RT_temperaturePrivate\Data\temperaturePoints\DanubeLS8_2022.csv'
# dfList2[0].to_csv(opfn)

# opfn = r'D:\RT_temperaturePrivate\Data\temperaturePoints\DanubeLS9_2022.csv'
# dfList2[1].to_csv(opfn)


