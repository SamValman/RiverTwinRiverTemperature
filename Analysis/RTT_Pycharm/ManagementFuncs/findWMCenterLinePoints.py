# -*- coding: utf-8 -*-
"""
Created on Fri May 31 10:07:07 2024

@author: lgxsv2
"""

import skimage.io as IO
import os
from scipy.spatial import cKDTree
import rasterio
import numpy as np
import pandas as pd
from pyproj import  Transformer
from skimage.util import img_as_ubyte


def potentialCentrePoints(driver, wmPaths, rawPaths, distanceMin=100):
    '''
   opens every water mask in wmPaths,
   skeletonise these to provide a centerline and a distance map,
   creates 100m CPs along this cl
   gets width at each centerpoint 
   logic statement for width >100m

    '''
    os.chdir(driver+ '\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\ManagementFuncs')
    import fileUtils as fu  
    import WaterMasking 

    clPaths = [] # these will later be put in closestPoints
    # iterate through images - each image is a time stamp at a location. Therefore the points need to be seperate
    for path in wmPaths:
        im = IO.imread(path)
        
        root = driver + r'\RT_temperaturePrivate\Data\imagery\Planet\centerLines'
        clPath = os.path.join(root, os.path.basename(path))
        

        # checks existance to save time. 
        if not os.path.exists(clPath):
            # calc centerline and distance map
            cl, dist = fu.calculateCenterline(im, distanceMin)
            
            # puts in different binary format to silence warning. 
            cl = img_as_ubyte(cl)
    
            IO.imsave(clPath, cl, check_contrast=False)

        #addLoc regardless to be sure 
        errList = WaterMasking.addLocationToWm(driver, rawPaths, [clPath])
        if errList != []:
            if path in errList[0]:
                print('errList')
                continue
        else:
            clPaths.append(clPath)
            
    return clPaths
        # get points every 100m on this center line, put their date, width, x and y coords into csv a
        
        # remove those that are too short


# #%% testrunning this file is now COMPLETE
# wmPaths = ["D:\\RT_temperaturePrivate\\Data\\imagery\\Planet\\m20Masks\\TestRiver_20221002.tif"]
# rawImageFilePaths = ["D:/RT_temperaturePrivate/Data/imagery/Planet/raw/TestRiver/TestRiver_20221002.tif"]
# # probably neeed to make this a full path 
# # might need to add the location data. 
# driver = 'D:'
# # os.chdir(driver+'\RT_temperaturePrivate\\Analysis\\ManagementFuncs')
# # import WaterMasking 

# # WaterMasking.addLocationToWm(driver, rawImageFilePaths, wmPaths) # might need to be moved ot after the skeletonisation
# cl = potentialCentrePoints(driver, wmPaths, rawImageFilePaths)




#%%        


def findClosestPoints(driver, clPaths, centralPoints):
    '''
    inputs:
        driver
        clPaths == paths to saved tif centerlines 
        centralPoints as a list 
        
    find the closest acceptable tif location to the centerpoints supplied 
    
    returns pd.df of date, point xy and new loc xy. 
    also returns metadata: distance between new location and old location same format as above 
    
    '''


    ###########################################################################
    # output metadata 
    listOfTimestepDfs = []
    listOfMetadataDfs = []

    for path in clPaths:   
        # get path with driver
        # print(path)
        # path = driver + path
        
        
        
        
        #######################################################################
        # collect cl information
        #######################################################################
        
        # read tif centerline
        cl = IO.imread(path)
        
        # get geotransform info to find point locs
        with rasterio.open(path) as rio_cl:
            gt = rio_cl.transform
            crs = rio_cl.crs

            
        # get the individual points
        indvClPoints = np.argwhere(cl > 0)
        try: 
            len(indvClPoints)
            if len(indvClPoints) <= 1:
                print(f'There are no points - issue with watermask on {os.path.basename(path)}')
                continue
        except:
            print(f'There are no points - issue with watermask on {os.path.basename(path)}')
            continue
            
        
        #######################################################################
        # Nearest neighbour search 
        #######################################################################
        
        # get individual coords
        ClCoords = [pixel2coord(x, y, gt ) for y, x in indvClPoints]
        
        # build the tree - will check speed improvements
        tree = cKDTree(ClCoords)
    

        
        
        ## # Convert the points to the raster's CRS using pyproj
        transformer = Transformer.from_crs('EPSG:4326', crs.to_string(), always_xy=True)
        points_proj = [transformer.transform(point[0], point[1]) for point in centralPoints]


        
        
        # closest points for time step
        timestepPoints = []
        correspondingOrder = []
        distLists = []
        
        # run through and query tree
        for point, pname  in zip(points_proj, centralPoints): #centralPoints:
            dist, idx = tree.query(point)
            timestepPoints.append(ClCoords[idx])
            distLists.append(dist)
            
            correspondingOrder.append(pname) # could be changed for some kind of id number
        
        # transform to EPSG 4326 - output GEE will want. 
        transformer = Transformer.from_crs(crs.to_string(),'EPSG:4326', always_xy=True) # inverse of previous
        timestepPoints = [transformer.transform(point[0], point[1]) for point in timestepPoints]

    
    
    
    
    
        # get date for df 
        date = os.path.basename(path)[-12:-4] 
        
        # set cols and data
        cols = ['date'] + correspondingOrder
        data = [date] + timestepPoints
        metadata = [date] + distLists
        
        # write df and append to list
        timestepDf = pd.DataFrame([data], columns=cols)
        timestepMetadata =  pd.DataFrame([metadata], columns=cols)
        listOfTimestepDfs.append(timestepDf)
        listOfMetadataDfs.append(timestepMetadata)
    # combine dfs to add to Reach level output
    csv = pd.concat(listOfTimestepDfs, ignore_index=True)
    metaOutput = pd.concat(listOfMetadataDfs, ignore_index=True)
    

    
    return csv, metaOutput






# internal
def pixel2coord(x, y, gt):
    """
    Returns global coordinates from pixel x, y coordinates
    """
    xp, yp = gt * (x, y)
    return (xp, yp)








#%%
# driver = 'D:'
# clPaths = [r"\RT_temperaturePrivate\Data\imagery\Planet\centerLines\TestRiver_20221002.tif"]

# os.chdir(driver+'\RT_temperaturePrivate\\Analysis\\ManagementFuncs')
# import fileUtils 
# centralPoints = fileUtils.collectPrecomputedDatasets(driver, 'TestRiver')
# # import pyproj



# a, b = closestPoints(driver, clPaths, centralPoints)












#%%


def pureLandsatPixels(ThrW=0.005, rr=0.005):
    
    
    # ThrW is probably threshold ater mndwi
    
    print('do some marti work')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    