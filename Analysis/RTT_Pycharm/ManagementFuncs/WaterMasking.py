# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 11:23:44 2023


This file uses the water mask developed in the RSE paper:
    it does this to create water masks of the PS images on the M river.
@author: lgxsv2
"""
# use env tf_3 for this 
import tensorflow as tf
import os
import glob
import pandas as pd
from skimage import io
import gc
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"



#%%
def save(P3,outfp):
    # change path to output model folder

    io.imsave(outfp, P3[2], check_contrast=False)

# %%

def extractWaterMasks(driver, riverName='Danube', reach=1, dates=[], paths=r"D:\GeomorphologyPaper\DataFolder\Imagery\rawImages\x.tif", model=r"D:\BackUp_RM\Code\RiverTwin\ZZ_Models\M20\model", verbose=False):
    os.chdir(driver + '\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\ManagementFuncs')
    from RiverTwinWaterMask import RiverTwinWaterMask
    
    newPaths = []
    for d in dates:
        fp = [a for a in paths if os.path.basename(a)[:8] == d]
        if type(fp)==list:
            try:
                fp = fp[0]
            except:
                continue
            
        # get the imagery directory without reach, file or "raw" so it can be saved in masks    
        newPath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(fp))), 'm20Masks')
        # name each watermask by constituant parts
        newPath = os.path.join(newPath, f'{riverName}_{reach}_{d}.tif')
        
        if os.path.exists(newPath):
            # print(f'{newPath} already water masked')
            emptyvar = 'a'
        else:
            if verbose:
                print(f'Carrying out watermasking on {newPath}')
            P3 = RiverTwinWaterMask(image_fp=fp, tileSize=20, model=model, output='')
            save(P3,newPath)
        newPaths.append(newPath)
    return newPaths

        
#%%
def addLocationToWm(driver, rawPaths, newPaths):
    os.chdir(driver+ '\RT_temperaturePrivate\\Analysis\\RTT_Pycharm\\ManagementFuncs')
    from locateImage import locateImage
    
    count = 0
    errorList = []
    for mask in newPaths:
        
        # need to find this mask in the original setup
        #basename to start
        bn = os.path.basename(mask)
        sections = bn.split('_')
        ifp = driver+f'\\RT_temperaturePrivate\\Data\\imagery\\Planet\\zip\\{sections[0]}_{sections[1]}_{sections[2]}'
        ifp = os.path.join(ifp, sections[-1][:-4])
        # print(ifp)
        # print(type(ifp))
        try:
            ifp = os.path.join(ifp, os.listdir(ifp)[0])
        except:
            count+=1
            print(f'the failure count is {count}')
            errorList.append(mask)
            continue
        
        # composite check first     
        composite_path = os.path.join(ifp, "composite.tif")
        if os.path.isfile(composite_path):
            raw = composite_path
        else: 
            im_path = os.path.join(ifp, 'PSScene')
            
            for tifs in glob.glob(os.path.join(im_path, '*.tif')):
                if 'Analytic' in tifs:
                    raw = tifs
        
        
        # # this will probably change but at the moment one starts with a date the other ends with
        # raw = [a for a in rawPaths if a[-12:-4] == mask[-12:-4]]
        # # just double check
        # if type(raw)==list:
        #     raw = raw[0]
        # overwrite mask with location data included mask
        try:
            locateImage(mask, raw, mask)
        except:
            count+=1
            print(f'the failure count is {count}')
            errorList.append(mask)
    return errorList
        
            

                





