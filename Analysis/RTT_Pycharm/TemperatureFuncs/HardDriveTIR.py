# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 22:22:48 2024

@author: lgxsv2
"""
import rasterio
from rasterio.plot import show
from shapely.geometry import Point
import geopandas as gpd
import os 
import glob
import pandas as pd
import math

#%%






def extractEcoStress(geometry='Rhone', 
                      task='extractValues_atmosphericallyCorrected', 
                      points=None,
                      maxCloud=20, 
                      date_start='2018-06-29', 
                      date_end='2024-12-31',
                      driver='D:'
                      ):
    """
    Extracts LST from the ECOSTRESS LST product for a list of points.
    
    Carried out in on the harddrive
    
    see         https://github.com/nasa/VITALS/blob/main/python/01_Finding_Concurrent_Data.ipynb
    for more information on ECOSTRESS processing, 
    Parameters
    ----------
    geometry : TYPE str riverName
        unneeded just to keep in line with other extractions
    task: str
       again unneeded as no processing
    date_start :  String
        Earliest possible image. The default is '2018-06-29'.
    date_end :  String
        latest possible image. The default is '2024-12-31'.
    emissivity :  float
        Emissivity value, limited impact on resulting temperature.
        The default is 0.991.

    """
    
    # first get the image for the date in question
    # date start is the date in question 

    # find if the file path on own works 
    folderP = driver+'/RT_temperaturePrivate/Data/imagery/ECOSTRESS/'+geometry
    if not os.path.exists(folderP):
        print('The driver for ecostress is wrong. Go into the HardDriveTIR.py file and change it on line 25')
        raise SystemExit()
    
    # Only given one date each time this runs
    # make impath

    
    # make output list to fill 
    listOfOutputPoints = []

##############################################################################    
##********** Could remove but will probably speed code up? ******************
    
    # check existance
    # if not return empty list for the df
    if not os.path.exists(folderP):
        return listOfOutputPoints
###############################################################################    
    

    if task == 'getDates':
            # download just the required dates 

            df = printOutDates(folderP)
            df = dateLimit(df, date_start, date_end)
            return df
    else:
        for p in points:        
            try:
                imPath = os.path.join(folderP, (date_start.replace("-", "")+'.tif'))
                if not os.path.exists(imPath):
                    return listOfOutputPoints
                # this function should be generic to any tiffs
                v = HardDriveExtractPointValue(imPath, p)
                listOfOutputPoints.append(v)
                # if extracting a value fails we need to add na
            except:
                listOfOutputPoints.append(None)
    
    # return the image values to be tabulated
    return listOfOutputPoints

    
    
    
    
def HardDriveExtractPointValue(imPath, p):
        '''
        extracts point value from tif dataset
        
            Parameters
        ----------
        imPath : tif path - LST already calculated 
        
        p : point_coords = '(lat , long)'
            lat long co-ords of point to be extracted.

        Returns
        -------
        value : float
            wst at that point.

        '''

        # converts the str to two seperate strs in list
        long, lat = p.strip('()').split(',') # check correct way around fucking check me ***************************

        pointGdf = gpd.GeoDataFrame(
            {'geometry':[Point(long, lat)]}, crs="EPSG:4326")

          # try in case cloud or etc 
        try:
        # Open Tif(f) file 
            with rasterio.open(imPath) as src:  
            #     # reproject gdf if necessary
                if pointGdf.crs != src.crs:
                    pointGdf = pointGdf.to_crs(src.crs)
    
                for point in pointGdf.geometry:
                    row, col = src.index(point.x, point.y)  # Get row and col in tif
                    value = src.read(1)[row, col]
                    # turn to celsius 
                    value = value - 273.15
                
                
                # cloud etc in the tif 
                if value >= 40 or value <=1:
                    value = None
        except:
            # where no image or point 
            value = None
        

        
        return value
#%%
def printOutDates(folder):
    p  = os.path.join(folder, '*.tif')
    
    dates = []
    for i in glob.glob(p):
        date = i.split('\\')[-1][:-4]
        dates.append(date)
    
    return dates

def dateLimit(df, ds, de):
    
    ds = int(ds.replace("-", ""))
    de = int(de.replace("-", ""))
    
    out = []
    for i in df:
        if int(i)>ds and int(i)<de:
            out.append(i)
    out = pd.DataFrame({'date':out})
    return out