# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 14:50:30 2024

@author: lgxsv2
"""

import os 
import glob
os.chdir(r"D:\RT_temperaturePrivate\Analysis\RTT_Pycharm\ManagementFuncs")
from ExtractAoI import ExtractAoI

folder = r"D:\RT_temperaturePrivate\Data\AoI\GEEDownloads\*.geojson"
out_folder = r"D:\RT_temperaturePrivate\Data\AoI\FinalPoints"

for i in glob.glob(folder)[:]: 
    print(os.path.splitext(os.path.basename(i))[0])
    try:
        ExtractAoI(i,out_folder=out_folder, buffer=3000, verbose=True, names=os.path.splitext(os.path.basename(i))[0],  save='NO')#'points_shp')
        # ExtractAoI(i,out_folder=out_folder, save='shp', buffer=3000,
        #            verbose=True, names=os.path.splitext(os.path.basename(i))[0])
        
    except :   
        print(i)
        
#%%
print(1+3)


     
