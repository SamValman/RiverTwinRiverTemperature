# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 14:56:23 2024

@author: lgxsv2
BASEMAP FUNCTIONS 
- GENERIC SAVING ETC FUNCTIONS
"""


# %%
import geopandas as gpd
import cv2

import os
import zipfile
import glob
import numpy as np
import skimage.io as io

from scipy.ndimage import distance_transform_edt, convolve


import pandas as pd

from datetime import datetime, timedelta

# %%
def readShp_points(filepath):
    '''

    Parameters
    ----------
    filepath : str

    Returns
    -------
    points_list : list of points - in format for buffer

    '''
    # open with geopandas
    gdf = gpd.read_file(filepath)

    # Extract the points from the GeoDataFrame
    points_list = [(point.x, point.y) for point in gdf.geometry]
    
    return points_list

#%% Processing utilities 


def collectPrecomputedDatasets(driver, riverName):
    '''
    Sorts the path and then calls a generic shp point file reader to open the original 100 points per site

    '''
    path = driver + '\RT_temperaturePrivate\Data\AoI\FinalPoints' 
    
    riverName = riverName +'.shp' 
    
    Og_CP = readShp_points(os.path.join(path, riverName))
    return Og_CP
    


def changeStrDate(date, days, direction):
    '''
    Expects date in format 'YYYY-MM-DD' and returns it in the same format 
    
    direction is either 'add' or subtract
    
    '''
    # make datetime
    d = datetime.strptime(date, "%Y-%m-%d")
    
    # add or remove days
    if direction =='add':
        newDate = d + timedelta(days=days)
    else:
        newDate = d - timedelta(days=days)
    
    # return to original format 
    newDate = newDate.strftime("%Y-%m-%d")
    
    return newDate



def findClosestDate(date, PSDates):
    '''
    Specific function for the inputs in processing.py 
    - could do with a warning for excessive differences
    '''
    date = datetime.strptime(date, '%Y-%m-%d')
    PSDates = [datetime.strptime(d, '%Y%m%d') for d in PSDates]
    closestDate = min(PSDates, key=lambda x: abs(x - date))
    daysDiff = abs((closestDate - date).days)

    return closestDate.strftime('%Y%m%d'), daysDiff

#%% additionalDateFuncs for Temperature 

def changeExtractionDate(extractions):
    '''
    Inputs: FP extractions pandas df  from ProcessWST. This is dates and point locations.
    it changes the date into GEE format yyyy-mm-dd
    it also creates a dates column to be iterated through in ProcessWST
    '''
    if type(extractions)==str:
        df = pd.read_csv(extractions)
        df = df.set_index('date')
        df = df.copy() # seperates the set index..

    else:
        df = extractions
        df = df.copy() # seperates the set index..

    
    try:
        df.index = pd.to_datetime(df.index, format='%Y%m%d').strftime('%Y-%m-%d')
    except: 
        pass
    
    dates = df.index.tolist()



    # sort 
    dates = sorted(dates)
    df = df.sort_index()
        
    
    
    return df, dates

def formatPoints(points):
    print('not sure when or why this was created')
    df = None
    return df
# %% BASEMAP FUNCTIONS
######### wrapper function for organising downloaded imagery

def organisePSImagery(driver, riverName, reachid):
    
    rawFolderPath = driver+f'\\RT_temperaturePrivate\\Data\\imagery\\Planet\\zip\\{riverName}_{reachid}'

    # finds all the folders within rawFolders and checks they are directorys of files
    rawFolders = [name for name in os.listdir(rawFolderPath) if os.path.isdir(os.path.join(rawFolderPath, name))]
    
    for date in rawFolders:
        
        # create/check output folder        
        outputFolder = driver+f'\\RT_temperaturePrivate\\Data\\imagery\\Planet\\raw\\{riverName}_{reachid}'
        # if folder doesn't exist then make it 
        if not os.path.isdir(outputFolder):
            os.makedirs(outputFolder)
        
        # deal with the multi-file problem
        ifp = os.path.join(rawFolderPath, date)
        
        # try and deal with the problem of not having access to some images
        try:
            ifp = os.path.join(ifp, os.listdir(ifp)[0])
        except:
            continue
        # composite check first     
        composite_path = os.path.join(ifp, "composite.tif")
        if os.path.isfile(composite_path):
            # get this image we want 
            im = io.imread(composite_path)
            
            # find the file date
            datePath = os.path.join(ifp, "*.xml") 
            # all xmls start with the date
            # but some don't work..
            # try:
            #     date = os.path.basename(glob.glob(datePath)[0])[:8]
            # except:
            
        else: 
            im_path = os.path.join(ifp, 'PSScene')
            
            for tifs in glob.glob(os.path.join(im_path, '*.tif')):
                if 'Analytic' in tifs:
                    im = io.imread(tifs)
                    date = os.path.basename(tifs)[:8]

        
        fn = os.path.join(outputFolder, f'{date}.tif')
        
        #had to add in because it was moving very slowly
        if not os.path.exists(fn):
            io.imsave(fn, im, check_contrast=False)
        
    correctlyNamedAndPlacedFilePaths = glob.glob(os.path.join(outputFolder, '*tif'))
    
    return correctlyNamedAndPlacedFilePaths

# organisePSImagery('D:', 'Rhone', 'reach_2')


#%% internal basemap funcs


def unzipPS(riverName='Danube', date='20230101', zipfolder=r'D:\RT_temperaturePrivate\Data\imagery\Planet\zip',
            verbose=False, destination=r'D:\RT_temperaturePrivate\Data\imagery\Planet\raw'):
    '''


    Parameters
    ----------
    riverName : TYPE, str
        DESCRIPTION. The default is 'Danube'.
    dare : TYPE, str
        # DESCRIPTION. The default is '20230101'.
    zipfolder : path
        DESCRIPTION. The default is r'F:\GeomorphologyPaper\DataFolder\zips'.
    verbose : binary, 
        DESCRIPTION. The default is False.
    destination : path, optional
        DESCRIPTION. The default is r'F:\GeomorphologyPaper\DataFolder\rawImages'.

    Returns
    -------
    opens zip renames files and saves them in corrosponding folder,
    hide folders you do not want extracted.

    '''
    ziplist = findZips(riverName, date, zipfolder, verbose)

    for i in ziplist:
        extraction(i, riverName, destination, verbose)
        if verbose:
            print('zip file done: ', str(i))
    print('Complete')


# %%
def findZips(riverName, date, zipfolder, verbose):
    # folder structure:
    # zipfolder->
    # This lists them for later use
    if type(date) == str:
        search_path = os.path.join(zipfolder,  f"{riverName}_{date}*.zip")
    else:
        search_path = os.path.join(zipfolder,  f"{riverName}_*.zip")

    list_of_files = glob.glob(search_path)
    if verbose:
        print(len(list_of_files))
    return list_of_files


# %%
def extraction(path, riverName, destination, verbose):

    with zipfile.ZipFile(path, "r") as zf:
        # lists all tifs that aren't udm2
        tifs = [file for file in zf.namelist(
        ) if file.lower().endswith("composite.tif")]

        for i in tifs:
            rename(i, riverName, destination, zf)
            if verbose:
                print(str(i) + ' done')


# %%

def rename(i, riverName, destination, zf):

    fn = riverName+'_'+i.split('_')[0].replace("-", "")+'.tif'
    if i.split('_')[0] == 'composite.tif':
        fn = os.path.basename(zf.filename)[:(
            len(riverName)+9)]+'.tif'  # zf is a input vat

    path = os.path.join(destination, riverName)
    if not os.path.exists(path):
        os.makedirs(path)

    output = os.path.join(path, fn)

    with open(output, "wb") as otf:
        otf.write(zf.read(i))

# %% poor performance don't use


def divideImage(im, nParts=40):
    im = io.imread(im)
    tiledSize = im.shape[0] // nParts
    parts = [im[i * tiledSize:(i + 1) * tiledSize] for i in range(nParts)]
    return parts


def reformImage(parts):
    return np.concatenate(parts, axis=0)


# %% Skeleton

def skeletonise(riverName, date, path, verbose=True):
    if type(date) == str:
        fp = os.path.join(os.path.join(path, riverName),
                          (f'{riverName}_{date}*.tif'))
    else:
        fp = os.path.join(os.path.join(path, riverName), (f'{riverName}*.tif'))

    for i in glob.glob(fp):
        newPath = os.path.join(os.path.dirname(path), 'm20Masks')
        newPath = os.path.join(newPath, os.path.basename(i))
        if os.path.exists(newPath):
            continue
        else:
            im = io.imread(newPath)
            rasterCentreline = calculateCenterline(im)
            opPath = os.path.join(os.path.dirname(path), 'centerLines')
            opPath = os.path.join(newPath, os.path.basename(i))
            io.imsave(opPath, rasterCentreline, check_contrast=False)

    # this requires the following functions beneath it


def calculateCenterline(im, logical=False):
    # uses riv cloud width method to calculate centreline based on a gradient map
    dist = CalcDistanceMap(im)
    grad = CalcGradientMap(dist, 2)
    cl = CalcOnePixelWidthCenterline(im, grad, 0.9, dist, logical)
    # cl1Cleaned1 = CleanCenterline(cl1, 300, True)
    # cl1px = CleanCenterline(cl1Cleaned1, 300, False)
    return cl, dist

    # Internal functions of above


def CalcDistanceMap(im, neighborhoodSize=1000, scale=3):
    binary_im = np.where(im > 0, 1, 0)

    # Calculate the Euclidean distance transform
    dpixel = distance_transform_edt(binary_im)

    # Convert distance to meters based on the given scale
    dmeters = dpixel * scale

    # # Apply a mask to keep distances only for river pixels within the specified neighborhood size
    # mask = (dpixel <= neighborhoodSize) & (im > 0)
    # DM = np.where(mask, dmeters, 0)

    return dmeters  # DM


def CalcGradientMap(im, scale=3):

    # Define convolution kernels for x and y gradients
    k_dx = np.array([[-0.5, 0.0, 0.5]])
    k_dy = np.array([[0.5], [0.0], [-0.5]])

    # Convolve the image with the x and y kernels
    dx = convolve(im, k_dx)
    dy = convolve(im, k_dy)

    # Calculate the gradient magnitude
    g = np.sqrt(dx**2 + dy**2) / scale

    return g


def CalcOnePixelWidthCenterline(im, GM, hGrad, dist, logical):
    # Fast distance transform of the river banks
    img_d2 = cv2.dilate(im, None, iterations=2)

    # Mask areas where gradient is less than or equal to the threshold hGrad
    cl = np.logical_and(GM <= hGrad, img_d2 > 0)
    if logical:
        # getting errors where too close to bank 30m would be as close as we could have regardless
        cl = np.logical_and(dist >= 60, cl > 0)

    # Apply skeletonization twice to get a 1px centerline
    cl1px = skeletonize(cl, 2, 1)

    return cl1px


def skeletonize(image, num_iterations, kernel_size):
    # Apply skeletonization num_iterations times
    for _ in range(num_iterations):
        # Use a kernel for erosion
        kernel = cv2.getStructuringElement(
            cv2.MORPH_CROSS, (kernel_size, kernel_size))
        image = cv2.erode(image.astype(np.uint8), kernel)

    return image.astype(bool)


#%%

def foo(df, method):
    
    # opens and also sorts index
    df, dates = changeExtractionDate(df)
   
    
    # create seperate output df 
    output = df.copy()


    # iterate through dates
    for idx in range(len(df)):
        
        # make row per date
        row = df.iloc[idx]

    
        for col in range(1, len(row)):
            # If the current value is the same as the previous one = won't change the first 
            if row[col] == row[col - 1]:
                
                
                
                # Replace the current value with 'stringx'
                if method == 'previous':
                    if idx>0:
                        output.iat[idx, col] = df.iat[idx-1, col] # replaces value with that for the previous date

                    else:
                        output.iat[idx, col] = df.iat[idx+1, col] # replaces value with that for the next date, not ideal but only option other than 0s
        
    return output

# changeExtractionDate


# df = foo(r"D:\RT_temperaturePrivate\Data\imagery\Planet\centerPixels\Rhone_2022-02-05_2022-11-26.csv",'previous')



#%%
def saveProcessingOutputs(driver, riverName, dates,  outputs):
    '''
    

    Parameters
    ----------
    driver : str
        DESCRIPTION.
    riverName : str
        DESCRIPTION.
    dates : list
        list from processing function of first to last date.
    outputs : output object from processing
        pixel locations and metadata list.

    Returns
    -------
    saves all files.

    '''
    
    # format dates
    start, end = dates[0], dates[-1] 
    
    # general filename
    gfn = f'{riverName}_ES{start}_{end}'
    # gfn = f'{riverName}_ES'
    
    
    # location for pixel location outputs
    mainOuput = driver + '\\RT_temperaturePrivate\\Data\\imagery\\Planet\\centerPixels'
    
    mainOuput = os.path.join(mainOuput, (gfn+'.csv'))
    # this is the df output
    outputs[0].to_csv(mainOuput)
    
    # metadata
    mList = ['Distance', 'DayDif', 'DateTimes']
    
    mpath = driver + '\\RT_temperaturePrivate\\Data\\metadata'
    for i in range(3):
        fp = os.path.join(mpath, (gfn + '_' + mList[i]+'.csv'))
        outputs[1][i].to_csv(fp)
    print('files saved')
    
    
    
    
    
    
    
    
    