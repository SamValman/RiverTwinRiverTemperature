# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 09:41:32 2024

@author: lgxsv2
"""
import os
os.chdir(r"D:\RT_temperaturePrivate\Analysis\ManagementFuncs")
import AoIfuncs 
import matplotlib.pyplot as plt 
plt.close('all')
def ExtractAoI(fp,out_folder='',save=False, buffer=100, testPoints=False, verbose=False, names='unnamed River'):
    '''
    Takes vector river orders points 
    then uses splines to find a start and end point in the line
    then returns the river with km points, with the new start and end times. 
    
    Created in conda env: skl
    - requires sklearn and geojson function so should be includable to most available envs
    
    Parameters
    ----------
    fp : currently only works with geojson files
    testPoints : shuffles points to check model is working - can be further coded to use example points
    Returns
    buffer in metres
        default is 100
    -------
    TYPE
        DESCRIPTION.

    '''
    ############## Get vertices from geojson file ################
    x,y = AoIfuncs.getOriginalVertices(fp) # only works with geojson at the moment - quickly fixed if needed 
    # check next func is working by shuffling points
    if testPoints:
        AoIfuncs.shufflePoints(x, y, useExample=False)
        
    ############## Order points downstream ###############################################
    # u, v will be ordered points downstream from start to end. 
    u, v = AoIfuncs.riverCenterlinePointOrder(x, y, plot=verbose, names=names)
    
    # make regular points along the line
    u, v = AoIfuncs.regularPoints(u, v, verbose=verbose, names=names)
    
    if verbose==True:
        print(len(u))

    # cut to distance from midpoint closest to Powerstation (This research only)
    output_line = AoIfuncs.trimRiver(u, v, names, verbose)
    
    output_buffered = AoIfuncs.bufferRiver(output_line, buffer, verbose)
   
    if save == 'buffer_json':
        AoIfuncs.savePolygonAsJson(output_buffered, out_folder, names)
    elif save =='buffer_shp':
        AoIfuncs.savePolygonAsShp(output_buffered, out_folder, names)
    elif save =='points_json':
        AoIfuncs.savePointsAsJson(output_line, out_folder, names)
    elif save =='points_shp':
        AoIfuncs.savePointsAsShp(output_line, out_folder, names)


   