# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 08:37:38 2024

@author: lgxsv2
"""

import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np 
import datetime
import os 

os.chdir(r'D:\RT_temperaturePrivate\Analysis\Figures')
from genericFigureFuncs import organiseMultipleDfs, smoothData, postProcessingErrorRemovalIMPORTANT, getSetVars

#%%# color func        
import matplotlib.dates as mdates
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import datetime
   
## get col schemes for each yr
def viridisCmap(yr):
    
    # ** CAN CHANGE THIS TO WORK WITH INDIVIDUALS - FIND YR From input and then return the actual end color
    
    
    cmap = cm.get_cmap('viridis')
# Define the range of dates from 1st Jan to 1st Dec 2022
    start_date = datetime.datetime(int(yr), 1, 1)
    end_date = datetime.datetime(int(yr), 12, 1)
    norm = mcolors.Normalize(mdates.date2num(start_date), mdates.date2num(end_date))
    
    return cmap, norm

def shortColor(cmap, norm, l):
    asDate = datetime.datetime.strptime(l, '%Y-%m-%d')  
    date_num = mdates.date2num(asDate)
    color = cmap(norm(date_num))
    
    return color


###############################################################################
# Main plot
###############################################################################
import matplotlib.gridspec as gridspec
plt.close('all')
def fig8linePlots(driver, relative=False):
    
    # get ya set vars here
    base, rivers, years = getSetVars(driver)


    
    # fig, ax= plt.subplots(3, 3, sharex=True)
    fig = plt.figure()
    spec = gridspec.GridSpec(3, 4, width_ratios=[1, 1, 1, 0.1], wspace=0.4, hspace=0.4)

    # Create subplots
    ax = [[fig.add_subplot(spec[i, j]) for j in range(3)] for i in range(3)]

    # ax = [[fig.add_subplot(spec[i, j], sharex=fig.add_subplot(spec[2, j])) for j in range(3)] for i in range(3)]


    for rn_pos in [0,1,2]:
        for yr_pos in [0,1,2]:
            

            
            # get rn and yr
            rn = rivers[rn_pos]
            yr = years[yr_pos]
            
            # get color vars 
            cmap, norm = viridisCmap(yr)
            
            
            
            # get best 10% 
            df = getBest10(base, rn, yr, driver)
            print(len(df))
            if rn_pos == 2:
                if yr_pos==2:
                    print('Stop when?')
            #         df.loc['2023-04-25', df.loc['2023-04-25'] < 20] = np.nan
            xs,ys,ls = internalSortDf(df, relative, rn_pos, yr_pos)
            
            
            # for x, y, l in zip(xs,ys,ls):
            #     print(l, ' ', str(y.min()), ', ', str(y.max()))

            ax[rn_pos][yr_pos].set_ylim(-3.5,4.5)

            for x, y, l in zip(xs,ys,ls):
                if rn_pos == 1:
                    x = x[::-1] 
                    
                c = shortColor(cmap, norm, l)

                ax[rn_pos][yr_pos].plot(x,y, label=l, color=c )
                # ax[rn_pos][yr_pos].legend()
    ### Labels Manually 
    ax[0][0].set_ylabel('Rhône')
    ax[1][0].set_ylabel('Nile')
    ax[2][0].set_ylabel('Yangtze')
    
    # x labels
    ax[2][0].set_xlabel('2021')
    ax[2][1].set_xlabel('2022')
    ax[2][2].set_xlabel('2023')
    if relative:
        fig.text(0.04, 0.5, 'Normalised surface water temperature ($^o$c)', va='center', rotation='vertical', fontsize=12)
    else:
        fig.text(0.04, 0.5, 'Surface water temperature ($^o$c)', va='center', rotation='vertical', fontsize=12)
    fig.text(0.52, 0.02, 'Distance downstream (km)', ha='center', va='center', fontsize=14)  # x-axis label
    for a in [0,1]:
        for b in [0,1,2]:
            ax[a][b].set_xticks([])
    
    cbar_ax = fig.add_subplot(spec[:, 3])  # Span the entire height of the figure
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)  # Create a ScalarMappable for the colorbar
    sm.set_array([])  # Required for the ScalarMappable
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='vertical', label='Date')
    cbar.set_ticks([738550, 738700, 738850])# 0.4, 0.6, 0.8, 1.0])  # Example: Custom tick positions
    cbar.set_ticklabels(['January', 'June', 'December']) #, 'Medium-High', 'High']) 
                
    plt.show()











def getBest10(base, riverName, year, driver='D:'):
    
    fp8 = os.path.join(base, riverName+'LS8_'+year+'.csv')
    fp9 = os.path.join(base, riverName+'LS9_'+year+'.csv')
    fpA = os.path.join(base, riverName+'ASTER_'+year+'.csv')
    fpES = os.path.join(base,riverName+'ES_'+year+".csv")

    fps =[fp8, fp9, fpA, fpES]
    df = organiseMultipleDfs(fps)
    df = postProcessingErrorRemovalIMPORTANT(df, riverName, year, driver, False)
    
    
    # getting that D10
    # number of rows
    nrow = df.notna().sum(axis=1)
    # get best sorted out
    nrowSorted = nrow.sort_values(ascending=False)
    #  number of rows top 10%
    topTen = int(len(nrowSorted) * 0.1)
    # Select these
    topTen = nrowSorted.head(topTen)
    
    df10 = df.loc[topTen.index]  
    
    return df10


def internalSortDf(df, relative, rn=0, yrs=0):
    xs, ys, labs = [],[],[]

    for index, row in df.iterrows():

        
        # remove "no" results
        if rn == 1 and yrs == 0:
            row = row[row>15]
        if rn == 1 and yrs ==2:
             # cloud impacted pixels
            row = row[row>20]
        else:
            row = row[row > 0]
        x = row.index.astype(int) # Column names as integers (0 to 99)
        if relative:
            # y = list(row.values-row.mean())
            y = np.array(row.values) - np.mean(row.values)
            # deal with the 2 odd Yangtze values
            mask = y >= -4
            x = x[mask]  # Keep only x values where y >= -4
            y = y[mask]
            mask = y <= 4
            x = x[mask]  # Keep only x values where y >= -4
            y = y[mask]
        else:
            y = row.values
        # get label 
        lab = index.strftime('%Y-%m-%d')
        
        xs.append(x)
        ys.append(y)
        labs.append(lab)
        
    return xs, ys, labs




#%%

fig8linePlots('D:', relative=True)




#%%
# ## will turn this into a 
def ShortPanel(Rhone, Nile, Yangtze, relative='T'):
    
    noYears = len(Rhone)
    
    # sort subplots by number of years we're working on
    fig, ax= plt.subplots(3, noYears)
    
    # get cols
    cmap, norm = viridisCmap(2022)
    
    
    for i in range(noYears):
        R, N, Y  = Rhone[i], Nile[i], Yangtze[i]
        # print(type(r))
        # print(type(y))
        if noYears <2:
            
            # plot the Rhone
            xs,ys,ls = internalSortDf(R, relative)
            for x, y, l in zip(xs,ys,ls):
                c = shortColor(cmap, norm, l)
                
                ax[0].plot(x,y, color=c, label=l)
                ax[0].set_ylabel('Rhône')
                ax[0].legend(loc='upper right')
                ax[0].set_ylim(-2.5,4.5)
            
            # plot the Nile
            xs,ys,ls = internalSortDf(N, relative)
            for x, y, l in zip(xs,ys,ls):
                c = shortColor(cmap, norm, l)

                ax[1].plot(x,y,color=c,label=l)
                ax[1].set_ylabel('Nile')
                ax[1].legend()
                ax[1].set_ylim(-2.5,4.5)

            
            # plot the Yangtze
            xs,ys,ls = internalSortDf(Y, relative)
            for x, y, l in zip(xs,ys,ls):
                c = shortColor(cmap, norm, l)

                ax[2].plot(x,y,color=c,label=l)
                ax[2].set_ylabel('Yangtze')
                ax[2].legend(loc='upper right')
                ax[2].set_ylim(-2.5,4.5)

                
    plt.xlabel('Distance downstream (Km)')
    if len(relative)>3:
        fig.text(0.04, 0.5, 'Normalised surface water temperature ($^o$c)', va='center', rotation='vertical', fontsize=12)
    else:
        fig.text(0.04, 0.5, 'Surface water temperature ($^o$c)', va='center', rotation='vertical', fontsize=12)
            
    plt.show()

            # ax[1]
            # ax[2]
            
            
            
            

# date_num = mdates.date2num(index)
# color = cmap(norm(date_num))




#%% Run this 
# base = 'D:' + '/RT_temperaturePrivate/Data/temperaturePoints'
# Rhone = [getBest10(base, 'Rhone', '2022')]
# Nile = [getBest10(base, 'Nile', '2022')]
# Yangtze = [getBest10(base, 'Yangtze', '2022')]
# #%%

# ShortPanel(Rhone, Nile, Yangtze, relative='Tsdf')









