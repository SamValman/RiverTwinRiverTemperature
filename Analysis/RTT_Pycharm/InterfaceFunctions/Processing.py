# -*- coding: utf-8 -*-
"""
Created on Fri May 24 09:52:24 2024

@author: lgxsv2
"""
# for some unknown reason these need to be done before anything else
import geopandas as gpd
import cv2

# from osgeo import gdal
# import rasterio as rio


import asyncio
import pandas as pd 
import os 
import numpy as np
import ee
import sys
import glob
ee.Authenticate()
ee.Initialize()

#%%
def Processing(driver, riverName, temperatureDates, satellites, landsat, PSkey, closestPoints=False):
    '''
    This function produces a csv of points and dates to be extracted from thermal imagery. 
    
    requires:
        driver: str e.g., "D:\"
            harddrive so that this function can be moved between systems
        riverName: str 
            assuming the river is on file, this should have the polygons and central points saved
        temperatureDates: csv filename or tuple
            selection of Long wave infrared satellite image dates we want to collect from
            or start and end date if we want to also collect these
        Landsat: binary
            carry out the Marti-Cardona et al. 2019 refining reliable landsat pixels
        PSkey: str
            PlanetScope account key
        
    
    It will do as follows:
        * divide the river into usable "reaches" 
            - the river polygon should have already been made with the RunMe file in the AOI folder
        * search the PS archive for dates
        * compare these dates for closest match
        * download clipped, composite ps images
        * water mask the image
        * if temperature is fromLandsat the Marti-Cardona algorithm will be used
        * skeletonisation, 100m width minimum 
        * the closest of these cp to the original points will be returned with the date
        * additional distance metadata extracted. 
        
        
    '''


    #### get all functions
    # most functions are written out in imports to make it easier to find and read code.
    # os.chdir(driver+'\RT_temperaturePrivate\\Analysis\\ManagementFuncs')
    sys.path.append(driver + '\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\ManagementFuncs')

    from AoIfuncs import bufferRiver
    from PSAPIs import PSSearch, PSDownload
    import WaterMasking
    from findWMCenterLinePoints import potentialCentrePoints, pureLandsatPixels, findClosestPoints
    import fileUtils
    sys.path.append(driver + '\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\TemperatureFuncs')
    from Generate_dates import generateDates

    ###################################################################



    # collected precomputed AOI datasets from device: AOI polygon and associated original center points
    Og_CP = fileUtils.collectPrecomputedDatasets(driver, riverName)
    
    # GEE landsat bit here to get dates just per area 
    # collect dates 
    if type(temperatureDates)==tuple:
        print('Searching for download images')
        temperatureDates, metadataDateTimes = generateDates(driver, satellites, riverName, temperatureDates)
        temperatureDates = list(temperatureDates['date'])
        print(temperatureDates)
    else:
        ### get dates to be aligned
        temperatureDates = list(pd.read_csv(temperatureDates, index_col=0)['date'])
    
    # need to sort first or the dates arn't in order.
    temperatureDates.sort()
    dateStart = fileUtils.changeStrDate(temperatureDates[0], 7, 'subtract') ## make this first -7 days
    dateEnd =  fileUtils.changeStrDate(temperatureDates[-1], 7, 'add') 
    
    
    # get output lists 
    locDfs = [] # new point locations # main output
    metaDfs = [] # distance of point to original
    daysDifDfs = [] # difference between ps and TIR

    
    
    
    # iteration for smaller reaches
    for i in range(10):
        #
        reachid = 'reach_' +str(i+1)
        # if i+1<8:
        #     continue
        print(f'THE REACH WE ARE ON IS {reachid}')
        # divide the Og_CP
        ri = i*10
        Reach = Og_CP[ri:ri+10]
        # print(reachid)
        # print(Reach)
        # raise SystemExit()
        
        ### buffer for new reach level geometry
        # convert Reach points to list of points
        ReachPs = np.array(Reach).reshape(10, 2)

        # buffer to include river and banks for water masking etc. 
        buffered = bufferRiver(ReachPs, 3000, verbose=False)
        
        geom = [buffered.tolist()] # d get coordinates in format for the api call
        
        
        
        ### get dates to be aligned
        if not closestPoints == 'only':

            PSDates, PSIds = PSSearch(geom, dateStart, dateEnd, PSkey) # res can be provided to PSActivate to get ID numbers
            
            # get closest dates
            datesForDownload, daysDif = zip(*[fileUtils.findClosestDate(date, PSDates) for date in temperatureDates])
            
            # output ready 
            daysDif = pd.DataFrame({'TIRDate':temperatureDates, 'daysDif': daysDif})
            daysDifDfs.append(daysDif)
        
        ##   API full session    
        # has to be done in a loop to provide the correct download location. 
        # stop =0
        if not closestPoints == 'only':
            for i in datesForDownload:
                # if stop <1:
                #     if i =='20220324':
                #         stop+=1
                #         continue
                SavePath = driver+f'\\RT_temperaturePrivate\\Data\\imagery\\Planet\\zip\\{riverName}_{reachid}\\{i}'
                if not os.path.exists(SavePath) or not any(os.scandir(SavePath)):
                    if not os.path.exists(SavePath):
                        os.makedirs(SavePath)
                    os.chdir(SavePath)
                    async def minimain():
                        a = await PSDownload(geom,i, PSIds, PSkey) # Downloads to working directory above.
                        return a
                
    
                    a = asyncio.run(minimain())
                else: 
                    print('folder exists therefore we are assuming the image has already been downloaded')

       
        print('Renaming and resaving images')
        rawImageFilePaths = fileUtils.organisePSImagery(driver, riverName, reachid)
        print('Resaving completes')
        #######################################################################
        # EVERYTHING BELOW THIS LINE IS AFTER THE IMAGES HAVE BEEN DOWNLOADED AND UNZIPPED
        # Therefore we are expecting the result of above to be RawImageFilePaths
        #######################################################################
        
        ### Water masking
        
        # collect model
        # model available from https://doi.org/10.1016/j.rse.2023.113932 and associated github
        model = driver + "/BackUp_RM/Code/RiverTwin/ZZ_Models/M20/model" 

        # option for having removed watermasked images. 
        if not closestPoints == 'only':
            # watermask  ** would be good to have some functionalities for failures here - skips if path already exists 
            wmPaths = WaterMasking.extractWaterMasks(driver=driver, riverName=riverName, reach=reachid, dates=datesForDownload, paths=rawImageFilePaths, model=model, verbose=True)
            
        # M-C algorithm needed - put on back burner 
        # if landsat:
            # wm = pureLandsatPixels(wm)
        
        
            
            #######################################################################
            ## closest point (output) dfs ##
            #######################################################################
        if closestPoints:
            if closestPoints == 'only':
                wmPaths = driver+'\\RT_temperaturePrivate\\Data\\imagery\\Planet\\m20Masks\\*.tif'
                wmPaths = [a for a in glob.glob(wmPaths) if riverName in a]
                wmPaths = [a for a in wmPaths if f'_{reachid}_' in a] # makes sure it's only the correct reach
                
                wmPaths = [a for a in wmPaths if f'_{temperatureDates[0][:4]}' in a] # makes sure it's only the correct reach
                
                # create empty day dif for when its not needed
                daysDifDfs = [pd.DataFrame(), pd.DataFrame()]
            # opens wm, skeletonise and dist calcs, logic statement for width>100, adds location, saves
            CLPaths = potentialCentrePoints(driver, wmPaths, rawImageFilePaths, distanceMin=100)
            
            print(CLPaths)
            # finds EPSG closest point location and returns as df 
            # distance outputs are being collected as metadata for the study
            ReachOutputs, ReachdistanceOutputs = findClosestPoints(driver, CLPaths, Reach) # Reach is the original points in this reach
            # add to list for concats
            locDfs.append(ReachOutputs) 
            metaDfs.append(ReachdistanceOutputs)
            
    ###########################################################################
    # combine reach outputs
    ###########################################################################
    
    
    if closestPoints:
        # put in correct format
        locDfs = [df.set_index('date') for df in locDfs]

        extractionLocationPoints = pd.concat(locDfs, axis=1)
        totalMetadataDistance = pd.concat(metaDfs, axis=1)
    
        totalDayDifMetadata = pd.concat(daysDifDfs, axis=1) # double check this one
        
        ### Alter locations for where PS image was too small. - does not fix the metadata at this stage 
        extractionLocationPoints = fileUtils.foo(extractionLocationPoints, 'closest') # closest in time. 
        
        
        outputs = extractionLocationPoints, [totalMetadataDistance, totalDayDifMetadata, metadataDateTimes] 
        
        fileUtils.saveProcessingOutputs(driver, riverName, temperatureDates, outputs) 
        
        return outputs
    else: 
        return False


    
    
    
#%% testing the function    

# satellites = ['Landsat5', 'Landsat7', 'Landsat8', 'Landsat9', 'Aster'] 
satellites = ['EcoStress']
unsavedOutputs = Processing('D:', 'Rhone', ('2020-01-01','2021-12-12'), satellites, False, '3c0d358130ef45dcaf5a3336911958fd', closestPoints='only')

#%%
























# import asyncio
# temperatureDates = r"D:\RT_temperaturePrivate\Data\imagery\Landsat8\Danube2022.csv"
# fileUtils.saveProcessingOutputs('D:', 'Danube', ['2022-01-01','2022-12-12'],  unsavedOutputs) 
    
# temperatureDates= ['2022-01-19', '2022-02-04', '2022-03-24', '2022-04-09', '2022-05-11', '2022-07-14', '2022-07-30', '2022-09-16', '2022-10-18', '2022-01-19', '2022-02-04', '2022-03-24', '2022-04-09', '2022-05-27', '2022-07-14', '2022-07-30', '2022-09-16', '2022-10-18', '2022-11-19', '2022-02-11', '2022-03-15', '2022-04-16', '2022-05-02', '2022-06-19', '2022-07-05', '2022-07-21', '2022-09-07', '2022-09-23', '2022-10-09', '2022-11-10']

    
# PSDates = ['20220505', '20220505', '20220502', '20220502', '20220425', '20220425', '20220425', '20220423', '20220423', '20220419', '20220419', '20220418', '20220418', '20220418', '20220418', '20220410', '20220410', '20220411', '20220411', '20220411', '20220411', '20220218', '20220320', '20220320', '20220320', '20220313', '20220305', '20220305', '20220316', '20220316', '20220307', '20220123', '20220123', '20220124', '20220124', '20220121', '20220121', '20220126', '20220126', '20220527', '20220518', '20220516', '20220516', '20220516', '20220228', '20220228', '20220227', '20220208', '20220208', '20220208', '20220201', '20220201', '20220201', '20220201', '20220201', '20220130', '20220121', '20220121', '20220724', '20220724', '20220519', '20220519', '20220331', '20220331', '20220402', '20220402', '20220331', '20220331', '20220331', '20220331', '20220301', '20220530', '20220530', '20220316', '20220406', '20220406', '20220407', '20220407', '20221116', '20221116', '20221116', '20221116', '20221115', '20221114', '20221114', '20221112', '20221112', '20221111', '20221111', '20221111', '20221111', '20221110', '20221110', '20221109', '20221109', '20221108', '20221108', '20221108', '20221108', '20221108', '20221107', '20221107', '20221107', '20221107', '20221106', '20221105', '20221105', '20221104', '20221104', '20221103', '20221103', '20221102', '20221102', '20221102', '20221102', '20221102', '20221102', '20221101', '20221101', '20221101', '20221101', '20221031', '20221031', '20221031', '20221031', '20221030', '20221030', '20221029', '20221029', '20221029', '20221029', '20221028', '20221028', '20221027', '20221027', '20221027', '20221027', '20221026', '20221026', '20221025', '20221025', '20221024', '20221024', '20221024', '20221024', '20221024', '20221024', '20221023', '20221023', '20221023', '20221023', '20221022', '20221022', '20221022', '20221022', '20221021', '20221021', '20221021', '20221021', '20221021', '20221021', '20221020', '20221020', '20221019', '20221019', '20221019', '20221019', '20221019', '20221019', '20221016', '20221016', '20221018', '20221018', '20221018', '20221018', '20221017', '20221017', '20221017', '20221017', '20221016', '20221016', '20221015', '20221015', '20221013', '20220129', '20220130', '20221013', '20221013', '20221013', '20220128', '20220121', '20220121', '20220126', '20220121', '20220121', '20220124', '20220124', '20220127', '20221012', '20221012', '20220228', '20220220', '20220220', '20220220', '20220220', '20220218', '20220209', '20220209', '20220209', '20220209', '20220201', '20220207', '20220207', '20221011', '20221011', '20221011', '20221011', '20221010', '20221010', '20221010', '20221010', '20221009', '20221009', '20221009', '20221009', '20221009', '20221009', '20221008', '20221008', '20221008', '20221008', '20221007', '20221007', '20221006', '20221006', '20221006', '20221005', '20221005', '20221004', '20221004', '20221003', '20221003', '20221001', '20221001', '20220930', '20220929', '20220929', '20220929', '20220929', '20220928']
    
    
    
    
    
    
    