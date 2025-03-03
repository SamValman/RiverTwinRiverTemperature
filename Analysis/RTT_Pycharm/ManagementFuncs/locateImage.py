# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 00:00:59 2024

@author: lgxsv2
"""

from osgeo import gdal
import rasterio as rio


#%%

def locateImage(fn_wm, fn_raw='x', out='x',count=1, verbose=False):
    '''
    For some reason returns water as 1 and land as 0
    Adds geolocation data to P3 imagery 
    
    Parameters
    ----------
    fn_wm : Str fn or im
        water mask p3 from River Twin Water Mask.
    fn_raw : Str fn
        raw tiff image used for the water mask.
    out : Str fn
        fn to save new located image. 

    Returns
    -------
    saves located image.

    '''
    if type(fn_wm)==str:
    
        with rio.open(fn_wm) as m:
            im = m.read()
            profile_old = m.profile
        if verbose:
            print('old profile:')
            print(profile_old)
    else:
        im = fn_wm # doesnt currently work
    
    with rio.open(fn_raw) as i:
        profile = i.profile
        profile['count']= 1#im.shape[count]
        # profile['count'] = im.shape[0]  # Set count based on the number of bands in the im array
        # profile['width'] = im.shape[1]  # Set width based on the third dimension of the im array
        # profile['height'] = im.shape[0]
    if verbose:
        print('new profile:')
        print(profile)
    
    # return profile

    # save file with new/old profile
    with rio.open(out, 'w', **profile) as l:
        l.write(im)
    if verbose:
        print('complete')


#%%
