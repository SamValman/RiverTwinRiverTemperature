# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 10:51:39 2024

@author: lgxsv2
"""

import os
import pandas as pd 
# ******* concerned we will have a mismatch if I dont keep a lid on which points are checked on which imageyr
driver = 'D:'
os.chdir(driver + '\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\ManagementFuncs')


def ProcessWST(driver, riverName, extractions, satellites, save=False, op=''):
    '''
    driver: str hardDrive
    riverName: str - could be replaced with geom theoretically
    extractions: df 
        result of processing function - closest points to centerline to be extracted with dates
    satellites: list of satellites to extract TIR
    save: True/False
    op: folder to save to
    
    '''
    ###########################################################################
    # Get all required packages
    ###########################################################################
    
    os.chdir(driver + '\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\ManagementFuncs')
    import fileUtils
    os.chdir(driver+'\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\TemperatureFuncs')
    import LandsatGEE 
    import AsterGEE
    import HardDriveTIR
    # set up functionTypes
    funcType = {'Landsat5':LandsatGEE.extractLS5,
                'Landsat7':LandsatGEE.extractLS7,
                'Landsat8':LandsatGEE.extractLS8,
                'Landsat9':LandsatGEE.extractLS9,
                'Aster': AsterGEE.extractAster,
                'EcoStress':HardDriveTIR.extractEcoStress } # maybe add cbers
    
    ###########################################################################
    # sort inputs 
    ###########################################################################
    extraction, dates = fileUtils.changeExtractionDate(extractions)

    
    # create list of vars to fill
    varLists = {sat: [] for sat in satellites}

    
    
    ###########################################################################
    # extraction 
    ###########################################################################
    
    for date in dates:
        # get just the points for this date
        points = extraction.loc[date]
        
        if len(points)!= 100:
            print('Error in number of points - check and remove this when error is solved')
            raise SystemExit()
           
        # extractionPoints = not sure this is needed. unless we need to swap the x and y around
        for sat in satellites:
            
            extractionFunc = funcType[sat] 
            
            
            # required for GEE functions:
            dateEnd = fileUtils.changeStrDate(date, 1, 'add')

            # all these need the same things as inputs 
            try:
                vals = extractionFunc(geometry=riverName, 
                                      task='extractValues_atmosphericallyCorrected', 
                                      points=points,
                                      maxCloud=20, 
                                      date_start=date, 
                                      date_end=dateEnd,
                                      ) 
            # needs to return empty list if nothing there
            except:
                # not sure if its needed but empty list in case no date for a particular satellite  
                vals = [None]*len(points)
                
            #adds value lists as     
            varLists[sat].append(vals)    
            print(f'{date} complete for {sat}')
    
    ###########################################################################
    # combine csvs per sat
    ###########################################################################
    
    # combineOutputs 

    
    dfList = []
    # # goes through the values for each satellite
    for sat in satellites:
    #     # satt should be a list of lists 100*dates in length
        tempDF = pd.DataFrame(varLists[sat])
        tempDF.insert(0, 'date', dates)

        dfList.append(tempDF) 
    
    
    # returning both just to confirm order of these - overwrite previous variable
    return dfList, satellites
    
    
    
    
    