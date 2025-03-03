# -*- coding: utf-8 -*-
"""
Created on Wed May 29 13:52:46 2024

@author: lgxsv2
"""

''' 
This file uses both GEE and other systems for alternative satellites to get csvs of available dates
'''
import os 
import pandas as pd 


def generateDates(driver, satellites, riverName, dateLimits):
    '''
    Finds all available satellit imagery for different TIR sats, within the specified date ranges. 
    Harddrive TIR still to be developed
    
    driver: str 
    satellites: list of str sat names
    riverName: str or geom. 
    dateLimits: tuple of start and end date 
    
    proccess: 
    1. go through sats
    2. find funcs
    3. combine dates 
    4. return full list of dates
    '''
    # set up sat functions
    os.chdir(driver+'\\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\TemperatureFuncs')
    import LandsatGEE
    import AsterGEE
    import HardDriveTIR
    
    # list all potential satellite options. 
    funcType = {'Landsat5':LandsatGEE.extractLS5,
                'Landsat7':LandsatGEE.extractLS7,
                'Landsat8':LandsatGEE.extractLS8,
                'Landsat9':LandsatGEE.extractLS9,
                'Aster':AsterGEE.extractAster,
                'EcoStress':HardDriveTIR.extractEcoStress }
    
    # list to fill with dates for each satellite
    dfs = []
    
    # iterate through each satellite
    for sat in satellites:
        
        # get the specific sat function
        dateFunc = funcType[sat] 
        
        # get out dataframe of available images - just keeping cloud constant for now
        satDateList = dateFunc(geometry=riverName, task='getDates', maxCloud=20, 
                               date_start=dateLimits[0], date_end=dateLimits[1]
                               )
        # print(satDateList)
        # add satellite name 
        try:
            satDateList.insert(1, 'Sat', sat, True)
        except:
            print(f'No available images in this date range from {sat}')
        #append to list
        dfs.append(satDateList)
    # df3 = pd.DataFrame({
    # 'date': ['2022-05-11', '2023-02-11', '2023-03-14'],
    
    # 'time': ['10:50:35.284000', '10:50:40.983000', '10:51:00.028000']
    # })
    # 'Sat': ['LS11', 'LS11', 'LS11'],
    # dfs.append(df3)
    # combine list for metadata to compare sats etc 
    metaData = pd.concat(dfs)
    # - make exclusive (no duplicates)
    dfs = [df.drop(columns=['Sat']) if 'Sat' in df.columns else df for df in dfs]
    availableDates = pd.concat(dfs, ignore_index=True)
    availableDates = availableDates.drop_duplicates(subset=['date'])

    #convert to string for future use
    availableDates['date'] = pd.to_datetime(availableDates['date']).dt.strftime('%Y-%m-%d')

    return availableDates, metaData
    
    
        
#%% Test
# driver= 'D:'
# satellites=['EcoStress']
# riverName = 'Nile'
# dateLimits = ('2022-04-01', '2023-06-01')

# d, m = generateDates(driver, satellites, riverName, dateLimits)



