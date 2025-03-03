# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 10:58:14 2024

@author: lgxsv2
"""
import ee
import pandas as pd
import os
import numpy as np
ee.Initialize()






def selectRiver(riverName):
    '''
    takes river name and gives a GEE geometry feature for further analysis 
    Remember capitals and no spaces
    '''
    string = 'projects/ee-samuelvalman/assets/P3RT/' + riverName
    
    geom = ee.FeatureCollection(string)
    return geom 



def getGeometry(geometry):
    if type(geometry) == str:
        # GEO is a riverName 
        filePath = 'projects/ee-samuelvalman/assets/P3RT/' + geometry
        
        geom = ee.FeatureCollection(filePath).geometry()
    else:
        # if used independently this will need to change to geometry.geometry()
        geom = geometry
        
    return geom 

def clip_image(image, geometry):
    return image.clip(geometry)

#%% Cloud
    # filter for cloud - not included atm not sure it's best method
    # ic = ic.map(lambda x: x.updateMask(x.select('cloud').eq(0)))

def removeCloudyPolygons(ic, maxCloud, varName):
    '''
    Removes polygon cloud

    Parameters
    ----------
    ic : GEE ic
    maxCloud : int
    varName : str
        ic distinct GEEmap.

    Returns
    -------
    output_ic 
    '''
    # if varName == 'cloud':
    #     mask = ic.map(lambda x:x.select(['cloud']).lte(maxCloud))
        
        
    ic_withMean = ic.map(lambda im: calAvgCloud(im, varName))

    # Filter out images where the mean value exceeds the maximum cloud value
    output_ic = ic_withMean.filter(ee.Filter.lte('mean', maxCloud))


    return output_ic

def calAvgCloud(im, varName):
    mean = im.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=im.geometry(),
        scale=30, 
        maxPixels=1e9
        # Adjust the scale according to your needs
    )
    # Get the mean value of the band
    return im.set('mean', mean.get('cloud'))

#%% EXPORT SECTION

def extractPointValue(ic, p):
    '''
    extracts point value for GEE dataset
    
        Parameters
    ----------
    ic : GEE image collection
        needs wst as a band.
    p : str that looks like tuple
        lat long co-ords of point to be extracted.

    Returns
    -------
    value : float
        wst at that point.

    '''
    # converts the str to two seperate strs in list
    p = p.strip('()').split(',')

    # format point into ee format 
    # first the list map float makes it a list of two floats
    point = ee.Geometry.Point(list(map(float,p)))
    
    # get ic to just be wst
    wstIC = ic.select('wst')
    # make ic into single image (probably already in a similar format)
    im = wstIC.median()
    
    # reduce region of individual point
    # else return 0
    try:
        value = im.reduceRegion(
        reducer=ee.Reducer.first(),
        geometry=point,
        scale=30).get('wst').getInfo()
        
    except:
        # where no image or point 
        value = 0
    
    return value

        
        
        
        
        
        
        
def printOutDates(ic, year=False, op=False, riverName=False):
    '''
    extracts a df of dates and times from an image collection in GEE
    Should already have cloud etc accounted for 

    Parameters
    ----------
    ic : GEE image collection
        this is built to be within the LandsatGEE functions.
        
    A saving function has been left in but will not be used in the main processing algorithm for the paper
    year : str, optional
        The default is False.
    op : str, optional
        The default is False.
    riverName : str, optional
         The default is False.

    Returns
    -------
    df : TYPE
        DESCRIPTION.

    '''
    dates = []
    times = []
    try:
        icList = ic.toList(ic.size())
        icInfo = icList.getInfo()

    except:
        # print('Ic empty')
        # print(ic.size().getInfo())
        # returning an empty dataframe enables generate dates to run and just not include this satellite
        return pd.DataFrame({})

    for im in icInfo:
        
        dt = pd.to_datetime(im['properties']['system:time_start'], unit='ms')
        
        date = dt.date()
        time = dt.time()
        
        dates.append(date)
        times.append(time)
    df = pd.DataFrame({'date':dates, 'time':times})
    
    ## effectively removed due to processing functioning running without - to save duplicate saving of dates
    if op != False:
        # check path for river exists
        op = os.path.join(op, (riverName+str(year)+'.csv'))
        df.to_csv(op)
        
    return df

#%% TEMPERATURE
def get_lookup_table(fc, prop_1, prop_2):
     reducer = ee.Reducer.toList().repeat(2)
     lookup = fc.reduceColumns(reducer, [prop_1, prop_2])
     return ee.List(lookup.get('list'))

# this one doesnt work
# def matrixNotationToLookUp(matrixValues=[]):
#     '''
#     Uses a solved linear equation from Jimen..
#     converts it to a look up table that can be used in a single channel algorithm with water vapour
    
#     matrixValues in format =     [x11, x12, x13, x21, x22, x23, x31, x32, x33]
    
#     returns df for wv values and a,b,c values 
#     '''


#     # Given matrix values (replace with actual values)
#     X = np.array(matrixValues).reshape(3,3)

#     # Water vapor percentages from 0% to 100% in steps of 10%
#     w_values = np.linspace(0, 1, 11)

#     # Create an empty list to store results
#     results = []

#     # Compute a, b, c for each water vapor percentage
#     for w in w_values:
#         W = np.array([1, w, w**2])
#         # abc = X.dot(W)
#         # abc = np.matmul( X, W)
#         abc = X @ W
#         results.append([w*10, *abc])

#     # Create a Dictorary to be called from
#     df = pd.DataFrame(results, columns=['Water Vapour', 'a', 'b', 'c'])

#     # return the lookup table
#     return df



### temporary to try new option - only seems to work if values in format x11, x21, x31.
def matrixNotationToLookUp(matrixValues=[]):
    '''
    Uses a solved linear equation from Jimen..
    converts it to a look up table that can be used in a single channel algorithm with water vapour
    
    matrixValues in format =     [x11, x21, x31, x12, x22, x32, x13, x33, x33]
    
    returns df for wv values and a,b,c values 
    '''


    # Given matrix values (replace with actual values)
    coefficients = np.array(matrixValues).reshape(3,3)
    # Water vapor percentages from 0% to 100% in steps of 10%
    w_values = np.linspace(0, 1, 11)
    
    # Function to compute the atmospheric function value
    def compute_function(coeffs, x):
        return coeffs[0] * x**2 + coeffs[1] * x + coeffs[2]
    
    # Initialize an empty DataFrame for the lookup table
    lookup_table = pd.DataFrame({'Water Vapour': w_values})
    
    # Compute the atmospheric functions and add them to the lookup table
    for i in range(coefficients.shape[1]):
        coeffs = coefficients[:, i]
        function_values = [compute_function(coeffs, x) for x in w_values]
        diction = {1:'a', 2:'b', 3:'c'}
        lookup_table[f'{diction[i+1]}'] = function_values



    # Create a Dictorary to be called from
    df = lookup_table

    # return the lookup table
    return df





    
def planckInversion(BT_image,band='BT', wavelength=10.659, rho=0.01438, emissivity=0.991):
        '''
        Returns a WST without atmospheric correction 
        shown to actually be less significantly different that you might expect
        requires satellite specific wavelength and rho

        Parameters
        ----------
        BT_image : Brightness temperature at black body: ee Image 
        band: str
        wavelength : float
            effective wavelength of tir band.
        rho : float
            (h  c/).
        emissivity : float
        

        Returns
        # wst = BT/((1+(wavelength/rho))*ln(emissivity)) # make ee

        -------
        WST
        '''
        wavelength = ee.Number(wavelength) 
        rho = ee.Number(rho*1000000) 
        emissivity = ee.Number(np.log(emissivity))

        image = BT_image.expression(
            'BT/(1+(((wavelength*BT)/rho)*emissivity))',
         {'BT': BT_image.select(band),
          'wavelength': wavelength,
          'rho': rho, 
          'emissivity':emissivity
         }).rename('wst')
        
        # turn to celcius
        image = image.expression('lst - 273.15', {'lst':image.select('wst')}).rename('wst')

        returnable = BT_image.addBands(image)
        
        return returnable # return wst
