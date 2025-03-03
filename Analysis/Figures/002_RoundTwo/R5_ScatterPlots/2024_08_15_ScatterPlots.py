# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 14:33:17 2024

@author: lgxsv2
"""

import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np 

import matplotlib.dates as mdates
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import datetime
import os 

os.chdir(r'D:\RT_temperaturePrivate\Analysis\Figures')
from genericFigureFuncs import organiseMultipleDfs, smoothData, postProcessingErrorRemovalIMPORTANT, getSetVars







#%%




# def singleSiteScatter(fps, riverName, year):
#     '''
#     fps should be a list of file paths
#     riverName should be a string
#     '''
    
#     ## 
#     df = organiseMultipleDfs(fps)
#     df = postProcessingErrorRemovalIMPORTANT(df, riverName, year, driver='D:')
    
#     cmap = cm.get_cmap('viridis')
#     # Define the range of dates from 1st Jan to 1st Dec 2022
#     start_date = datetime.datetime(year, 1, 1)
#     end_date = datetime.datetime(year, 12, 1)
#     norm = mcolors.Normalize(mdates.date2num(start_date), mdates.date2num(end_date))
    
#     plt.figure()
    
#     plt.title(f'{riverName} {year}')



#     for index, row in df.iterrows():
#         try:
#             row = row[row > 0]
#         except:
#             print('i dont rember why this is even here ')
#         x = row.index.astype(int) # Column names as integers (0 to 99)
#         y = row.values  # Temperature values
            
#             # colour
#         date_num = mdates.date2num(index)
#         color = cmap(norm(date_num))
#             # Scatter plot for the row
#         plt.scatter(x, y, color=color)
#     # Add a colorbar
#     sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
#     sm.set_array([])
#     cbar = plt.colorbar(sm, label='Date')
    
#     tick_locs = cbar.get_ticks()
#     tick_labels = [mdates.num2date(tick).strftime('%Y-%m-%d') for tick in tick_locs]
#     cbar.set_ticks(tick_locs)
#     cbar.set_ticklabels(tick_labels)


#     plt.xlabel('Distance downstream (km)')
#     plt.ylabel('Temperature ($^o$c)')

#     plt.show()
    
# def pannelScatter(lfps, riverNames, year):
    
    
    
#     fig, ax = plt.subplots(1, len(riverNames))
    
    
    
#     for i in range(len(riverNames)):
#         ind = (i+1)*3
#         fps = lfps[ind-3: ind-1]
#         riverName = riverNames[i]
#         df = organiseMultipleDfs(fps)
#         df = postProcessingErrorRemovalIMPORTANT(df, riverName, year, driver='D:')
        
#         cmap = cm.get_cmap('viridis')
#         # Define the range of dates from 1st Jan to 1st Dec 2022
#         start_date = datetime.datetime(year, 1, 1)
#         end_date = datetime.datetime(year, 12, 1)
#         norm = mcolors.Normalize(mdates.date2num(start_date), mdates.date2num(end_date))
        
        
#         ax[i].set_title(f'{riverName} {year}')
#         for index, row in df.iterrows():
#             try:
#                 row = row[row > 0]
#             except:
#                 print('i dont rember why this is even here ')
#             x = row.index.astype(int) # Column names as integers (0 to 99)
#             y = row.values  # Temperature values
            
#             # colour
#             date_num = mdates.date2num(index)
#             color = cmap(norm(date_num))
#             # Scatter plot for the row
#             ax[i].scatter(x, y, color=color)
            
#             ax[i].set_xlabel('Distance downstream (km)')
#             ax[i].set_ylabel('Temperature ($^o$c)')
            
            
#             # Add a colorbar
#     sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
#     sm.set_array([])
#     cbar = plt.colorbar(sm, label='Date')
    
#     tick_locs = cbar.get_ticks()
#     tick_labels = [mdates.num2date(tick).strftime('%Y-%m-%d') for tick in tick_locs]
#     cbar.set_ticks(tick_locs)
#     cbar.set_ticklabels(tick_labels)

#     plt.show()
#%%
import matplotlib.gridspec as gridspec


def F7SixPanel(driver):
    
    # fig, ax = plt.subplots(3,3)
    fig = plt.figure()
    spec = gridspec.GridSpec(3, 4, width_ratios=[1, 1, 1, 0.1], wspace=0.4, hspace=0.4)

    # Create subplots
    ax = [[fig.add_subplot(spec[i, j]) for j in range(3)] for i in range(3)]
    
    # plt.ylim(0,40)
    
    base, rivers, years = getSetVars(driver) 
    
    # again use position because easier to find paths
    for rn_pos in [0,1,2]:
        for yr_pos in [0,1,2]:
            
            # get rn and yr
            rn = rivers[rn_pos]
            yr = years[yr_pos]
            
            # get files 
            L8 = os.path.join(base, f"{rn}LS8_{yr}.csv")
            L9 = os.path.join(base, f"{rn}LS9_{yr}.csv")
            As = os.path.join(base, f"{rn}Aster_{yr}.csv")
            ES = os.path.join(base, f"{rn}ES_{yr}.csv")

            
            # put into list to combine
            fps = [L8,L9, As, ES]
    
            # manually post process for removal
            df = organiseMultipleDfs(fps)
            df = postProcessingErrorRemovalIMPORTANT(df, rn, yr, driver)
            if rn_pos == 1:
                print('d')
    
            # get col schemes for each yr
            cmap = cm.get_cmap('viridis')
            # Define the range of dates from 1st Jan to 1st Dec 2022
            start_date = datetime.datetime(int(yr), 1, 1)
            end_date = datetime.datetime(int(yr), 12, 1)
            norm = mcolors.Normalize(mdates.date2num(start_date), mdates.date2num(end_date))
    
    
    
    
    
            # run through rows in this df
            for index, row in df.iterrows():
                try:
                    row = row[row > 0]
                except:
                    print('This was removing errs')
                    
                x = row.index.astype(int) # Column names as integers (0 to 99)
                
                # fix Nile direction
                if rn_pos==1:
                    x = x[::-1] 

                y = row.values  # Temperature values
                
                # colour
                date_num = mdates.date2num(index)
                color = cmap(norm(date_num))
                # Scatter plot for the row
                ax[rn_pos][yr_pos].scatter(x, y, color=color)
            ax[rn_pos][yr_pos].set_ylim(0,40)
            
    ### Labels Manually 
    ax[0][0].set_ylabel('Rhône')
    ax[1][0].set_ylabel('Nile')
    ax[2][0].set_ylabel('Yangtze')
    
    # x labels
    ax[2][0].set_xlabel('2021')
    ax[2][1].set_xlabel('2022')
    ax[2][2].set_xlabel('2023')
    
    
    # overarching labels
    fig.text(0.52, 0.02, 'Distance downstream (km)', ha='center', va='center', fontsize=14)  # x-axis label
    fig.text(0.08, 0.5, 'Temperature ($^o$c)', ha='center', va='center', rotation='vertical', fontsize=14)  # y-axis label
    for a in [0,1]:
        for b in [0,1,2]:
            ax[a][b].set_xticks([])
    
    cbar_ax = fig.add_subplot(spec[:, 3])  # Span the entire height of the figure
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)  # Create a ScalarMappable for the colorbar
    sm.set_array([])  # Required for the ScalarMappable
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='vertical', label='Date')
    cbar.set_ticks([738550, 738700, 738850])# 0.4, 0.6, 0.8, 1.0])  # Example: Custom tick positions
    cbar.set_ticklabels(['January', 'June', 'December'])

    plt.show()
        
  
#%%
plt.close('all')
F7SixPanel(driver='D:')    
    
    
    
    
    
# #%% Actionable section 
# # plt.close('all')
# ls8_Rhone = r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneLS8_2022.csv"
# ls9_Rhone = r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneLS9_2022.csv"
# A_Rhone = r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneAster_2022.csv"

# # df = pd.read_csv(ls8_Rhone)
# # df = df.iloc[:,1:]
# # df.set_index('date', inplace=True)
# riverName = 'Rhone'
# year = 2022
# fps = [ls8_Rhone, ls9_Rhone, A_Rhone]

# # singleSiteScatter(fps, riverName, year)
# # scatterHighlightErrors(fps, riverName)
# #%%

# ls8_Yangtze = r"D:\RT_temperaturePrivate\Data\temperaturePoints\YangtzeLS8_2022.csv"
# ls9_Yangtze = r"D:\RT_temperaturePrivate\Data\temperaturePoints\YangtzeLS9_2022.csv"
# A_Yangtze = r"D:\RT_temperaturePrivate\Data\temperaturePoints\YangtzeAster_2022.csv"
# riverName = 'Yangtze'
# year = 2022
# fps = [ls8_Yangtze, ls9_Yangtze, A_Yangtze]
# # singleSiteScatter(fps, riverName, year)


#%%

# ls8 = r"D:\RT_temperaturePrivate\Data\temperaturePoints\DanubeLS8_2022.csv"
# ls9 = r"D:\RT_temperaturePrivate\Data\temperaturePoints\DanubeLS9_2022.csv"
# riverName = 'Danube'
# fps= [ls8, ls9]
# singleSiteScatter(fps, riverName)

#%%

# ls8_Nile = r"D:\RT_temperaturePrivate\Data\temperaturePoints\NileLS8_2022.csv"
# ls9_Nile = r"D:\RT_temperaturePrivate\Data\temperaturePoints\NileLS9_2022.csv"
# A_Nile = r"D:\RT_temperaturePrivate\Data\temperaturePoints\NileAster_2022.csv"
# riverName = 'Nile'
# year = 2022
# fps = [ls8_Nile, ls9_Nile, A_Nile]
# # singleSiteScatter(fps, riverName, year)

# #%%

# lfps = [ls8_Rhone, ls9_Rhone, A_Rhone, ls8_Yangtze, ls9_Yangtze, A_Yangtze]
# riverNames = ['Rhone', 'Yangtze']

# pannelScatter(lfps, riverNames, year)


























#%%

#%%
def scatterHighlightErrors(fps, riverName):
    
    df = organiseMultipleDfs(fps)
    df_clean, df_dirty = smoothData(df, smoothingFactor=5)

    #### set colors 
    cmap = cm.get_cmap('viridis')
    # Define the range of dates from 1st Jan to 1st Dec 2022
    start_date = datetime.datetime(2022, 1, 1)
    end_date = datetime.datetime(2022, 12, 1)
    norm = mcolors.Normalize(mdates.date2num(start_date), mdates.date2num(end_date))
    plt.figure()
    ## plot points
    for index, row in df_clean.iterrows():
        row = row[row > 0]
        x = row.index.astype(int) # Column names as integers (0 to 99)
        y = row.values  # Temperature values
        
        # colour
        date_num = mdates.date2num(index)
        color = cmap(norm(date_num))
        # Scatter plot for the row
        plt.scatter(x, y, color=color)
        
    ### add eronous points
    for index, row in df_dirty.iterrows():
        row = row[row > 0]
        x = row.index.astype(int) # Column names as integers (0 to 99)
        y = row.values  # Temperature values
        # plt.scatter(x, y, color='red')

   
    
   # Add a colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, label='Date')

    tick_locs = cbar.get_ticks()
    tick_labels = [mdates.num2date(tick).strftime('%Y-%m-%d') for tick in tick_locs]
    cbar.set_ticks(tick_locs)
    cbar.set_ticklabels(tick_labels)
    cbar.set_title('Date')

    plt.xlabel('Distance downstream (km)')
    plt.ylabel('Temperature ($^o$c)')

    plt.show()
# def singleSiteScatterSATS(fps, riverName):
#     '''
#     fps should be a list of file paths
#     riverName should be a string
#     '''
    
#     ## 
#     dfList = [pd.read_csv(x) for x in fps]
    
    
    
    
#     plt.figure()
    
#     plt.title(f'{riverName} {year}')
#     num=0
#     for df in dfList:
#         # temp color 
#         col = ['red', 'blue']
#         label = ['LS8', 'LS9']
#         c = col[num]
#         lab= label[num]
#         num +=1
        
#         df = df.iloc[:,1:]
#         df.set_index('date', inplace=True) 
#         for index, row in df.iterrows():
#             row = row[row > 0]
#             x = row.index.astype(int) # Column names as integers (0 to 99)
#             y = row.values  # Temperature values
    
#             # Scatter plot for the row
#             plt.scatter(x, y, c=c)#, label=lab) # index
#     handles = [plt.Line2D([0], [0], color=color, lw=4) for color in col]

#     # Plot the legend
#     plt.legend(handles, label, loc='best')
#     plt.show()
#         # c = 