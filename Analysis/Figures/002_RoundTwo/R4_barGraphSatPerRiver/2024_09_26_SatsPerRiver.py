# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 11:54:48 2024

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
import glob

os.chdir(r'D:\RT_temperaturePrivate\Analysis\Figures')
from genericFigureFuncs import organiseMultipleDfs, smoothData, postProcessingErrorRemovalIMPORTANT, getSetVars
#%%
def countStuff(fp, n, y, driver):
    
    df = pd.read_csv(fp)
    df = df.iloc[:, 1:]
    df = df.set_index('date')
    df = df[df>0]
    df = postProcessingErrorRemovalIMPORTANT(df, n, y, driver='D:', verbose =False)
    val = df.notna().sum().sum()
    return val

def fig5Bars(driver):
    
    base, rivers, years = getSetVars(driver)
    
    
    # plot params
    barWidth = 0.25
    labels = ['Landsat 8', 'Landsat 9', 'Aster', 'Ecostress']
    colors = ['Blue', 'Orange', 'Green', 'Yellow']    
    
    plt.ylim(0, 3500)
    
    
    
    fig, ax = plt.subplots()
    
    # get bar_positions for x ticks
    barPositions = []
    
    # run through years and rivers but saves enumerating through them
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

            try:
                ES = countStuff(ES, rn, yr, driver) # for plotting
            except:
                print('no ES for this year')
                ES = 0
            L8, L9, As = countStuff(L8, rn, yr, driver),countStuff(L9,rn, yr, driver),countStuff(As, rn, yr, driver)
            
            # get bar position based on river and year - saves enumerating through them
            barPosition = (rn_pos) + (yr_pos*(barWidth+0.01)) #rn_pos * 3 + yr_pos * (barWidth + 0.05) 
            barPositions.append(barPosition)
            
            # get one set of labels for legend
            if rn_pos ==2 and yr_pos == 2:
                labels = ['Landsat 8', 'Landsat 9', 'Aster', 'Ecostress']
            else:
                labels = [None, None, None, None]
            
            ax.bar(barPosition, L8,  width=barWidth, color=colors[0], label=labels[0])
            ax.bar(barPosition, L9, bottom=L8, width=barWidth, color=colors[1], label=labels[1])
            ax.bar(barPosition, As, bottom=L8 + L9, width=barWidth, color=colors[2], label=labels[2])
            ax.bar(barPosition, ES, bottom=L8 + L9+As, width=barWidth, color=colors[3], label=labels[3])

    
    # over complicated x ticks
    # Custom x-tick positions for year labels
    # year_positions = [(r * 3 + 1) * (barWidth + 0.05) for r in range(len(rivers))]
    year_positions = [p + (barWidth / 2) for p in range(len(rivers))]  # Midpoint per river group

    year_labels = years * len(rivers)
    river_labels = ['', 'Rhône', '', '', 'Nile', '', '', 'Yangtze', '']
    # Set x-axis ticks and combine year + river labels
    combined_labels = [f"{yr}\n{river}" for yr, river in zip(year_labels, river_labels)]
    ax.set_xticks(barPositions)
    ax.set_xticklabels(combined_labels, rotation=0, ha='center')  # Combined labels
    
    ## Set x-axis ticks
    # ax.set_xticks(barPositions)
    # ax.set_xticklabels(year_labels, rotation=90)
    
    # ax2 = ax.twiny()  # Create a twin x-axis
    # ax2.set_xlim(ax.get_xlim())  # Match the limits with the main axis
    # ax2.set_xticks(year_positions)  # Add ticks for rivers
    # ax2.set_xticklabels(river_labels)  # Set river names as labels
    # ax2.tick_params(axis='x', rotation=0, pad=10)
    
    plt.ylabel('River centre points with temperature collected')
    
    plt.legend()

    plt.tight_layout()
    plt.show()
        




#%%
plt.close('all')
fig5Bars('D:')


#%%


def barGraphSatsPerRiver(riverNames, years, driver='D:'):
    
    base = driver + '\RT_temperaturePrivate\Data\temperaturePoints'
    
    # organise imagery and errors etc 
    valList = []
    for n in riverNames:
        for y in years:
            
            fp = n+'*'+str(y)+'.csv'
            fp = os.path.join(base, fp)
            fps=[]
            for i in glob.glob(fp):
                df = pd.read_csv(i)
                
            try:
                ndf = postProcessingErrorRemovalIMPORTANT(df, n, y, driver=driver)
            except:
                ndf = df
                print(f'no manual check for {n}')
            
            val = ndf.notna().sum().sum()
            
            valList.append(val)

    


    # make the figure
    
    fig, ax = plt.subplots()
    
    labels = ['sat 1', 'sat 2', 'sat 3']

    ax.set_ylabel('Number of center points collected')



    iloc = 0
    for n in riverNames:
        for y in years:
            
            toPlot = valList[iloc:iloc+2]
            ax.bar(0, toPlot[0], label=labels[0])#, color=colors[0])
            ax.bar(0, toPlot[1], bottom=toPlot[0], label=labels[1])#, color=colors[1])
            ax.bar(0, toPlot[2], bottom=toPlot[0] + toPlot[1], label=labels[2])#, color=colors[2])
            
            
            iloc+=1
    plt.show()
    
def dumbVersion(fp8_r, fp9_r, fpA_r, fp8_y, fp9_y, fpA_y, fp8_n, fp9_n, fpA_n, y=2022, driver='D:'):
    
    r8, r9, rA = countStuff(fp8_r, 'Rhone', y, driver),countStuff(fp9_r,'Rhone', y, driver),countStuff(fpA_r, 'Rhone', y, driver)
    y8, y9, yA = countStuff(fp8_y, 'Yangtze', y, driver),countStuff(fp9_y, 'Yangtze', y, driver),countStuff(fpA_y, 'Yangtze', y, driver)
    n8, n9, nA = countStuff(fp8_n, 'Nile', y, driver),countStuff(fp9_n, 'Nile', y, driver),countStuff(fpA_n, 'Nile', y, driver)

    labels = ['Landsat 8', 'Landsat 9', 'Aster']
    colors = ['Blue', 'Orange', 'Green']
    
    fig, ax = plt.subplots()
    ax.bar(0, r8, label=labels[0], color=colors[0])
    ax.bar(0, r9, bottom=r8, label=labels[1], color=colors[1])
    ax.bar(0, rA, bottom=r8 + r9, label=labels[2], color=colors[2])
    
    ax.bar(1, y8,  color=colors[0])
    ax.bar(1, y9, bottom=y8, color=colors[1])
    ax.bar(1, yA, bottom=y8 + y9,   color=colors[2])
    
    ax.bar(2, n8,  color=colors[0])
    ax.bar(2, n9, bottom=n8, color=colors[1])
    ax.bar(2, nA, bottom=n8 + n9,   color=colors[2])
    
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(['Rhone', 'Yangtze', 'Nile'])
    
    plt.ylabel('River centre points with temperature collected')
    
    plt.legend()
    
    
    
    
    
def countStuff(fp, n, y, driver):
    
    df = pd.read_csv(fp)
    df = df.iloc[:, 1:]
    df = df.set_index('date')
    df = df[df>0]
    df = postProcessingErrorRemovalIMPORTANT(df, n, y, driver='D:', verbose=False)
    val = df.notna().sum().sum()
    return val

#%%
# fp8_y = r"D:\RT_temperaturePrivate\Data\temperaturePoints\YangtzeLS8_2022.csv"
# fp9_y = r"D:\RT_temperaturePrivate\Data\temperaturePoints\YangtzeLS9_2022.csv"
# fpA_y = r"D:\RT_temperaturePrivate\Data\temperaturePoints\YangtzeAster_2022.csv"

# fp8_r = r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneLS8_2022.csv"
# fp9_r = r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneLS9_2022.csv"
# fpA_r = r"D:\RT_temperaturePrivate\Data\temperaturePoints\RhoneAster_2022.csv"

# fp8_n = r"D:\RT_temperaturePrivate\Data\temperaturePoints\NileLS8_2022.csv"
# fp9_n = r"D:\RT_temperaturePrivate\Data\temperaturePoints\NileLS9_2022.csv"
# fpA_n= r"D:\RT_temperaturePrivate\Data\temperaturePoints\NileAster_2022.csv"
# dumbVersion(fp8_r, fp9_r, fpA_r, fp8_y, fp9_y, fpA_y, fp8_n, fp9_n, fpA_n)

# riverNames = ['Rhone']
# years = [2022]
 
# barGraphSatsPerRiver(riverNames, years)
    