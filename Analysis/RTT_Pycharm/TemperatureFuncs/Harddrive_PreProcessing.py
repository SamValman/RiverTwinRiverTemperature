# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 09:55:50 2024

@author: lgxsv2
"""
# working in tifs again
import numpy as np 

# Import required libraries
import os
# import folium
import earthaccess
import warnings
# import folium.plugins
import pandas as pd
import geopandas as gpd
import math

# from branca.element import Figure
from IPython.display import display
from shapely import geometry
from skimage import io
from datetime import timedelta
from shapely.geometry.polygon import orient
from matplotlib import pyplot as plt

#%%
def sortAOIForECOSTRESS(AOI_fp):
    ''' 
    sorts AOI into a square box and makes it the correct format for Earth Access
    '''
    polygon = gpd.read_file(AOI_fp)
    roi_poly = polygon.unary_union.envelope
    roi_poly = orient(roi_poly, sign=1.0)
    # not sure what agu stands for in this context
    df = pd.DataFrame({"Name":["ROI Bounding Box"]})
    agu_bbox = gpd.GeoDataFrame({"Name":["ROI Bounding Box"], "geometry":[roi_poly]},crs="EPSG:4326")

    roi = list(roi_poly.exterior.coords)
    return roi


#%%
# The Query
# this line was only needed to get the concept id 
eco_collection_query = earthaccess.collection_query().keyword('ECOSTRESS L2 Tiled LSTE')

def getAssetList(date_range=('2022-01-01','2022-12-31'), OtherSatDates=[], roi=[]):
    '''
      ----------
    date_range : (startDate, endDate), optional
        DESCRIPTION. The default is ('2022-01-01','2022-12-31').
    dateRange : TYPE, optional
        DESCRIPTION. The default is [].
    roi: use sortAOIForECOSTRESS function. 

    Returns
    -------
    None.

    '''
    # asks for the grid version we want.
    concept_ids = ['C2076090826-LPCLOUD']

    results = earthaccess.search_data(
        concept_id=concept_ids,
        polygon=roi,
        temporal=date_range,
        count=500)
    
    results_df = pd.json_normalize(results)

    # Create a list of columns to keep
    keep_cols = ['meta.concept-id','meta.native-id', 'umm.TemporalExtent.RangeDateTime.BeginningDateTime','umm.TemporalExtent.RangeDateTime.EndingDateTime','umm.CloudCover','umm.DataGranule.DayNightFlag','geometry','browse', 'shortname']
    # Remove unneeded columns
    df = results_df[results_df.columns.intersection(keep_cols)].copy()
    df.rename(columns = {'meta.concept-id':'concept_id','meta.native-id':'granule',
                       'umm.TemporalExtent.RangeDateTime.BeginningDateTime':'start_datetime',
                      'umm.TemporalExtent.RangeDateTime.EndingDateTime':'end_datetime',
                      'umm.CloudCover':'cloud_cover',
                      'umm.DataGranule.DayNightFlag':'day_night'}, inplace=True)
    
    # need to go through datetimes for images between 10 and 2 
    # ECOSTRESS given in UTC therefore conversion to French time is +1 hr 
    df['start_datetime'] = pd.to_datetime(df['start_datetime'])

    filtered_results = df[(df['start_datetime'].dt.hour >= 9) & (df['start_datetime'].dt.hour < 13)].copy()
    
    # sort so only dates that correspond with those in OtherSatDates
    # only run if required
    if len(OtherSatDates) != 0:
        OtherSatDates = pd.to_datetime(OtherSatDates).date  # to datetime date

        filtered_results = filtered_results[filtered_results['start_datetime'].dt.date.isin(OtherSatDates)]
    
    # then use index to get the same values from 'results' - the index of the df doesn't change as it's filtered # awesome python knowledge there..
    originalOutputsSorted = [results[i] for i in filtered_results.index]
    
    #get urls
    results_urls = [granule.data_links() for granule in originalOutputsSorted]
    assetsURLsWanted = []
    # Pick Desired Assets (leave _ on RFL to distinguish from RFLUNC, LST. to distinguish from LST_err)
    desired_assets = ['_RFL_','_MASK_', 'LST.'] # Add more or do individually for reflectance, reflectance uncertainty, or mask
    # Step through each sublist (granule) and filter based on desired assets.
    for n, granule in enumerate(results_urls):
        for url in granule: 
            asset_name = url.split('/')[-1]
            if any(asset in asset_name for asset in desired_assets):
                assetsURLsWanted.append(url)
    
    return assetsURLsWanted, filtered_results

def downloadEcostress(urls, driver, riverName):
    earthaccess.login(persist=True)
    # Get requests https Session using Earthdata Login Info
    fs = earthaccess.get_requests_https_session()
    # # Retrieve granule asset ID from URL (to maintain existing naming convention)
    for url in urls:
        granule_asset_id = url.split('/')[-1]
        # Define Local Filepath
        fp = f'{driver}/RT_temperaturePrivate/Data/imagery/ECOSTRESS/{riverName}/{granule_asset_id}'
        
        
        # Download the Granule Asset if it doesn't exist
        if not os.path.isfile(fp):
            with fs.get(url,stream=True) as src:
                with open(fp,'wb') as dst:
                    for chunk in src.iter_content(chunk_size=64*1024*1024):
                        dst.write(chunk)

#%%
import glob
folderp = 'D:/RT_temperaturePrivate/Data/imagery/ECOSTRESS/test'

####




        
#####
def sortNamingConvention(folderp):
    
    
    allTifs = os.path.join(folderp, 'E*.tif')
    
    # get all the unique dates in the folder by going through each tiff and removing them. 
    uniqueDates = []
    
    for i in glob.glob(allTifs):
        bn = os.path.basename(i)
        date = bn[33:41]
        uniqueDates.append(date)
    
    # make unique
    uniqueDates = list(set(uniqueDates))
        
    # vars ready to be overwritten or filled
    dates = []
    times = []
    add_ons = []
    
    # iterate through each available day
    for day in uniqueDates:
        
        # all ims for that day
        listOfTifs = glob.glob(os.path.join(folderp, f'*{day}*.tif'))
        # set new add on for each day
        add_on = 0
        
        # go through and save/rename
        for i in listOfTifs:

            if len(listOfTifs) == 1:
                d, t = getDT(i)
                os.rename(i, os.path.join(folderp, (d+'.tif')))
            else:
                add_on += 1
                d, t = getDT(i)
                os.rename(i, os.path.join(folderp, (d+'_'+str(add_on)+'.tif')))
           
            
            dates.append(d)
            times.append(t)
            add_ons.append(add_on)
    # make df
    df = pd.DataFrame({'date':dates, 'time':times, 'iteration':add_ons})
    
    # save the df 
    df_fp = os.path.join(folderp, 'metadata.csv')
    df.to_csv(df_fp, index=False)
    
    return df
        
       
        
def getDT(i):
    # get basename
    bn = os.path.basename(i)

    # extract date and time
    date = bn[33:41]
    time = bn[42:46]
    
    return date, time
    
   
        
     

# bn  = sortNamingConvention(folderp)        



        
#%%        

        
        # rename to date
    








#%%

# we can't really do this because the TOA is in a range of 4-8 which i'm not sure what to do with
def planckInversion(BTim, wavelength=10.659, rho=0.01438, emissivity=0.991):
        '''
        Returns a WST without atmospheric correction 
        shown to actually be less significantly different that you might expect
        requires satellite specific wavelength and rho
        This is a hard drive version to work on numpy arrays

        Parameters
        ----------
        BT_image : Brightness temperature at black body: np array 
        wavelength : float
            effective wavelength of tir band.
        rho : float
            (h  c/).
        emissivity : float
        

        Returns
        # wst = BT/((1+(wavelength/rho))*ln(emissivity)) 

        -------
        WST
        '''
        rho = (rho*1000000) # might beed to change this 
        emissivity = np.log(emissivity)
        
        
        #    'BT/(1+(((wavelength*BT)/rho)*emissivity))'

        im = wavelength *BTim
        im = (im/rho)*emissivity
        wst = BTim/(im+1)
        
        
        # may need to convert to celsius 
        wst = wst -273.15
        

        
        return wst # return wst
        
        
#%%  TESTing 



