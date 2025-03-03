# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 10:53:17 2024

@author: lgxsv2
"""


import sys

driver = 'D:'

sys.path.append(driver + '\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\ManagementFuncs')
sys.path.append(driver + '\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\TemperatureFuncs')
sys.path.append(driver + '\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\InterfaceFunctions')


import Processing
# from ProcessWST import ProcessWST

#%% VAR hard code
riverName = 'Rhone' #Rhone and Nile defo done
# temperatureDates = r"D:\RT_temperaturePrivate\Data\imagery\Landsat8\Danube2022.csv"
temperatureDates = ('2021-01-01', '2023-12-31')
satellites = ['EcoStress']
# not yet coded sats in.
landsat = 'no'
PSkey = KEYY

# save file is replacing get central points because we've seperated that for now. 

save = False
var = True
# locations, Metadata
# Processing.Processing(driver=driver, riverName=riverName, temperatureDates=temperatureDates, satellites=satellites,
#                       landsat=landsat, PSkey=PSkey, closestPoints=save)
while var == True:
    try:
        Processing.Processing(driver=driver, riverName=riverName, temperatureDates=temperatureDates, satellites=satellites,
                              landsat=landsat, PSkey=PSkey, closestPoints=save)

        # if success then we will break
        print(f'It worked for {riverName}!')
        var = False


    except Exception as e:
        print(f'Temporary failure with e as {e}')





# (driver, riverName, temperatureDates, satellites, landsat, PSkey
# tempCSV = ProcessWST(driver, riverName, locations)
