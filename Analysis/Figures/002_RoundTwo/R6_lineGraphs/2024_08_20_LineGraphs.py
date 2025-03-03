# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 12:08:14 2024

@author: lgxsv2
"""

import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np 

import matplotlib.dates as mdates
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import datetime
from matplotlib.lines import Line2D
import os

os.chdir(r'D:\RT_temperaturePrivate\Analysis\Figures')
from genericFigureFuncs import organiseMultipleDfs, smoothData, postProcessingErrorRemovalIMPORTANT#(df, smoothingFactor=0.5)
#%%
def singleSiteLineGraph(fps, riverName, year,  colorMap=False, smoothFactor=3, summerOnly=False):
    '''
    fps should be a list of file paths
    riverName should be a string
    colorMap relates to what we are coloring the lines by. 
        The options are: winter/summer
                        month 
                        
    '''
    
    ## 
    df = organiseMultipleDfs(fps)
    df = postProcessingErrorRemovalIMPORTANT(df, riverName, year, driver='D:')
    
    if type(smoothFactor)==int:
        df_clean, df_dirty = smoothData(df, smoothingFactor=smoothFactor)
    
        df = df_clean.copy()

    plt.figure()
    
    plt.title(f'{riverName} {year}')
    for index, row in df.iterrows():
        ## colour 
        start_date = pd.Timestamp('2022-05-30')
        end_date = pd.Timestamp('2022-09-30')
        test = row.name
        
        # remove "no" results
        row = row[row > 0]

        # Determine the color based on the condition
        if start_date <= test <= end_date:
            color = 'red'
            if summerOnly:
                print(len(row))
                if len(row)<=50:
                    continue
                x = row.index.astype(int) # Column names as integers (0 to 99)
                y = row.values  # Temperature values
                plt.plot(x,y, c=color)
                
        else:
            color = 'blue'
        
        if not summerOnly:
            x = row.index.astype(int) # Column names as integers (0 to 99)
            y = row.values  # Temperature values
            plt.plot(x,y, c=color)
        

    legend_elements = [Line2D([0], [0], marker='o', color='w', label='Summer (June-September)',
                          markerfacecolor='red', markersize=10),
                       Line2D([0], [0], marker='o', color='w', label='Winter (October-May)',
                          markerfacecolor='blue', markersize=10)]

    # Add the legend to the plot
    plt.legend(handles=legend_elements, loc='upper right')
    

    
    plt.xlabel('Distance downstream (km)')
    plt.ylabel('Temperature ($^o$c)')    
    plt.show()

    return df

#%%

plt.close('all')


ls8_Rhone = r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneLS8_2022.csv"
ls9_Rhone = r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneLS9_2022.csv"
A_Rhone = r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneAster_2022.csv"

riverName = 'Rhone'
year = 2022
fps = [ls8_Rhone, ls9_Rhone, A_Rhone]
x = singleSiteLineGraph(fps, riverName, year, smoothFactor=3, summerOnly=True)
    
# x = singleSiteLineGraph(fps, riverName, year, smoothFactor=None)





































#%% CM additional details
# cmap = cm.get_cmap('viridis')
# # Define the range of dates from 1st Jan to 1st Dec 2022
# start_date = datetime.datetime(2022, 1, 1)
# end_date = datetime.datetime(2022, 12, 1)
# norm = mcolors.Normalize(mdates.date2num(start_date), mdates.date2num(end_date))
            #  # colour
            # date_num = mdates.date2num(index)
            # color = cmap(norm(date_num))
            
            # # Add a colorbar
            # sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            # sm.set_array([])
            # cbar = plt.colorbar(sm, label='Date')
            
            # tick_locs = cbar.get_ticks()
            # tick_labels = [mdates.num2date(tick).strftime('%Y-%m-%d') for tick in tick_locs]
            # cbar.set_ticks(tick_locs)
            # cbar.set_ticklabels(tick_labels)
            
            
            
        # for index, row in df.iterrows():
        #     row = row[row > 0]
        #     x = row.index.astype(int) # Column names as integers (0 to 99)
        #     y = row.values  # Temperature values
            

        #     # Scatter plot for the row
        #     plt.scatter(x, y, color=color)