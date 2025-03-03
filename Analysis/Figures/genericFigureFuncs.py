# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 11:46:12 2024

@author: lgxsv2
"""
import pandas as pd
import numpy as np 
import os




#%%
def postProcessingErrorRemovalIMPORTANT(df_t, riverName,year, driver='D:', verbose=True):
    '''
    uses manual mask made for each river to mask the riverTemp and remove water temperature errors

    Parameters
    ----------
    df_t : pandas df of river temperatures
    riverName : str
    driver : TYPE, optional
        DESCRIPTION. The default is 'D:'.

    Returns
    -------
    None.

    '''
    startingNAN = df_t.isna().sum().sum()

    
    
    ### open T/F manual file
    fp = driver+'/RT_temperaturePrivate/Data/temperaturePoints/ManualChecks'
    
    riverName = riverName + '_' + str(year)
    
    manualMask = os.path.join(fp , (riverName + '.csv'))
    
    manualMask = pd.read_csv(manualMask)
    
    ## use mannual to remove 
    # manual mask is in a binary format - set date to index
    df_bin = manualMask.set_index('date')
    df_bin.index = pd.to_datetime(df_bin.index, format='%d/%m/%Y', dayfirst=True)

    
    # i for index location.
    rows = range(len(df_t))
    cols = range(len(df_t.columns))

    for i_row in rows:
        for i_col in cols:
            binary = df_bin.iloc[i_row, i_col]
            if binary == 1:
                df_t.iloc[i_row, i_col] = np.nan
    
    endingNAN = df_t.isna().sum().sum()
    
    if verbose:
    
        print(f'{riverName} started with {startingNAN} NaNs, after manual checks there were {endingNAN} \n A change of {endingNAN-startingNAN}')

        print(f'This leaves {df_t.notna().sum().sum()} temperature readings from {year}')
    
    
    
    
    return df_t
    # df_merged = pd.merge(riverTemp, manualMask, on=['date', 'location'])

    # Filter only valid data
    # df_filtered = df_merged[df_merged['is_valid'] == True].drop(columns=['is_valid'])



def organiseMultipleDfs(fps):
    '''
    combines and averages the temperatures so that there is one value per day per river km
        

    Parameters
    ----------
    fps : list
        filepaths for temperature dfs for different sats.

    Returns
    -------
    df : pandas df

    '''
    
    dfList = [pd.read_csv(fp) for fp in fps if os.path.exists(fp)]
    dfs = []
    for df in dfList:
        try:
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')  # Update format if necessary
        except ValueError:            
            df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')  # Update format if necessary

            
        df = df.iloc[:,1:]
        df.set_index('date', inplace=True) 
        dfs.append(df)
        
    # combine the datasets averaging temperature values
    dfs = [df.replace(0, np.nan) for df in dfs]
    df = pd.concat(dfs, axis=0)
    df = df.groupby(df.index).mean()  
    
    df = df.reset_index()
    df = df.set_index('date')
    return df


#%%
def smoothData(df, smoothingFactor=0.5):
    df_clean = df.copy()
    df_dirty = df.copy()
    
    
    # find erronous points and remove
    for index, row in df_clean.iterrows():
        for i in range(1, len(row)-1):
            if (abs(row[i] - row[i-1]) > smoothingFactor or
                abs(row[i] - row[i+1]) > smoothingFactor):
                df_clean.loc[index].iloc[i] = np.nan
    
    # create dirty pd for plotting
    # find erronous points and understand
    for index, row in df_dirty.iterrows():
        for i in range(1, len(row)-1):
            if (abs(row[i] - row[i-1]) < smoothingFactor or
                abs(row[i] - row[i+1]) < smoothingFactor):
                df_dirty.loc[index].iloc[i] = np.nan
    
    
    
    return df_clean, df_dirty


def getSetVars(driver):
    base = driver + '/RT_temperaturePrivate/Data/temperaturePoints'
    
    rivers = ['Rhone', 'Nile', 'Yangtze']
    years = ['2021','2022', '2023']
    return base, rivers, years
