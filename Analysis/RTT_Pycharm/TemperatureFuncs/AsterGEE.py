# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 12:11:28 2024

@author: lgxsv2
https://github.com/sofiaermida/Landsat_SMW_LST/blob/master/modules/Landsat_LST.js
"""


import ee
# import geemap
import os 
os.chdir(r'D:\RT_temperaturePrivate\Analysis\RTT_Pycharm\TemperatureFuncs')
import GEE_GenericFuncs
import AsterPreprocessing


ee.Initialize()

#%%
def extractAster(geometry, 
               task, 
                     points=None,
                     maxCloud=20, 
                     date_start='2021-10-31', 
                     date_end='2024-06-01',
                     emissivity=0.991, 
                     ):
    """
    Calculates Water Surface temperature using Aster which at time of writing is up to date on GEE
    
    Carried out in Google Earth Engine with desired; geometry, date range,
    emissivity value
    
    Uses Statistical-monowindow method (Ermida et al., 2020) atmospheric_correction 
        
    Parameters
    ----------
    geometry : TYPE ee.geometry() or str riverName
        Preferably GRWL watermask object ids but any earth engine geometry type 
        will do to constrain the study site. 
        Can be replaced with str river name which is linked to hardcoded watershed values
    task: str
        either getDates, extractValues_atmosphericallyCorrected, extractValues_uncorrected
        controls the use of GEE function
    date_start :  String
        Earliest possible image. The default is '2013-04-11'.
    date_end :  String
        latest possible image. The default is '2022-01-01'.
    emissivity :  float
        Emissivity value, limited impact on resulting temperature.
        The default is 0.991.

    """
    
    ###########################################################################
    # Check if geometry is a river name
    ###########################################################################
 
    # get in in gee geom form
    geometry = GEE_GenericFuncs.getGeometry(geometry)
    ###########################################################################
    # Step one get bands
    ###########################################################################
    
    ## will I need different atmospheric correction files. 
    ic = getAsterIC(date_start,date_end, emissivity, geometry)
    
    # clip to just polygon
    ic = ic.map(lambda im: GEE_GenericFuncs.clip_image(im, geometry))    

    # This has to be removed because majority of images beyond 2006 lacking all rgb bands
    # The bands are still available in the image it is only the meta data that acknowledges this
    # therefore we can't server side make alterations.
    
    # ic = GEE_GenericFuncs.removeCloudyPolygons(ic, maxCloud, varName='cloud')


    ###########################################################################
    # Task control - save duplicating some code
    ###########################################################################
    # Get dates
    ###########################################################################
    if task == 'getDates':
        # download just the required dates 
        
        
        df = GEE_GenericFuncs.printOutDates(ic)
        return df
    
    ###########################################################################
    # Extract temperature - atmospherically corrected or not
    ###########################################################################
    else:
        listOfOutputPoints = []
        # print(task)
        # temperature options 
        if task == 'extractValues_atmosphericallyCorrected':
            
            # add coefficient look up table values so they don't need to be repeatedly calculated
            matrixValues = [0.06524, -0.05878, 1.06576,-0.55835, -0.75881, 0.00327, -0.00284, 1.35633, -0.43020]
            # matrixValues = [0.05327, -0.03937, 1.05742, -0.484444, -0.74611, -0.03015, 0.00764, 1.24532, -0.39461]
            matrixValues = [0.05327, -0.484444,0.00764,  -0.03937, -0.74611,  1.24532, 1.05742,  -0.03015,  -0.39461]

            matrixDF = GEE_GenericFuncs.matrixNotationToLookUp(matrixValues)
            # # need to drop the first row because I wrote this one out from what was intended 
            # matrixDF = matrixDF.drop(0)
            # matrixDF = matrixDF.reset_index(drop=True)
            
            ic = ic.map(lambda x:getTemperature(x, geometry, matrixDF, emissivity))
            
            # return ic
        elif task == 'extractValues_uncorrected':
        
            # defualt values were set to B13 aster 
            ic = ic.map(lambda x:GEE_GenericFuncs.planckInversion(x,band='BT',  emissivity=emissivity))
            
      
        
   
            
        
        # remove cloud below the maxCloud avg in just polygon. 
        # ic = GEE_GenericFuncs.removeCloudyPolygons(ic, maxCloud, varName='cloud')
        
        
        for p in points:
            # if we can extract a value then do 
            try:
                v = GEE_GenericFuncs.extractPointValue(ic, p)
                listOfOutputPoints.append(v)
            # if extracting a value fails we need to add na
            except:
                listOfOutputPoints.append(None)
        return listOfOutputPoints   
    
    
    
    
    
    
    
    
 

#%% Internal functions - these will be moved when the other GEE Landsat files are finished.   


def addNCEPband(image):
    
    '''
    THIS IS DIFFERENT TO LANDSAT
    '''
    # first select the day of interest
    date = ee.Date(image.get('system:time_start'))
    year = ee.Number.parse(date.format('yyyy'))
    month = ee.Number.parse(date.format('MM'))
    day = ee.Number.parse(date.format('dd'))
    date1 = ee.Date.fromYMD(year,month,day)
    date2 = date1.advance(1,'days')
# function compute the time difference from landsat image
    def datedist(image):
        return image.set('DateDist', ee.Number(image.get('system:time_start')) \
          .subtract(date.millis()).abs())

    # load atmospheric data collection
    TPWcollection = ee.ImageCollection('NCEP_RE/surface_wv')\
        .filter(ee.Filter.date(date1.format('yyyy-MM-dd'), date2.format('yyyy-MM-dd'))).map(datedist)

    # select the two closest model times

    closest = (TPWcollection.sort('DateDist')).toList(2)
    # check if there is atmospheric data in the wanted day
    # if not creates a TPW image with non-realistic values
    # these are then masked in the SMWalgorithm function (prevents errors)
    tpw1 = ee.Image(ee.Algorithms.If(closest.size().eq(0), ee.Image.constant(-999.0),
                      ee.Image(closest.get(0)).select('pr_wtr') ))
    tpw2 = ee.Image(ee.Algorithms.If(closest.size().eq(0), ee.Image.constant(-999.0),
                        ee.Algorithms.If(closest.size().eq(1), tpw1,
                        ee.Image(closest.get(1)).select('pr_wtr') )))

    time1 = ee.Number(ee.Algorithms.If(closest.size().eq(0), 1.0,
                        ee.Number(tpw1.get('DateDist')).divide(ee.Number(21600000)) ))
    time2 = ee.Number(ee.Algorithms.If(closest.size().lt(2), 0.0,
                        ee.Number(tpw2.get('DateDist')).divide(ee.Number(21600000)) ))

    tpw = tpw1.expression('tpw1*time2+tpw2*time1',
                            {'tpw1':tpw1,
                            'time1':time1,
                            'tpw2':tpw2,
                            'time2':time2
                            }).clip(image.geometry())

    # SMW coefficients are binned by TPW values
    # find the bin of each TPW value
    pos = tpw.expression(
    "value = (TPW>-8 && TPW<=2) ? 0" + \
    ": (TPW>2 && TPW<=12) ? 1" + \
    ": (TPW>12 && TPW<=22) ? 2" + \
    ": (TPW>22 && TPW<=32) ? 3" + \
    ": (TPW>32 && TPW<=42) ? 4" + \
    ": (TPW>42 && TPW<=52) ? 5" + \
    ": (TPW>52 && TPW<=62) ? 6" + \
    ": (TPW>62 && TPW<=72) ? 7" + \
    ": (TPW>72 && TPW<=82) ? 8" + \
    ": (TPW>82) ? 9" + \
    ": 0",{'TPW': tpw}) \
    .clip(image.geometry())
    
    pos = tpw.expression(
    "value = (TPW>0 && TPW<=10) ? 1" + \
    ": (TPW>10 && TPW<=20) ? 2" + \
    ": (TPW>20 && TPW<=30) ? 3" + \
    ": (TPW>30 && TPW<=40) ? 4" + \
    ": (TPW>40 && TPW<=50) ? 5" + \
    ": (TPW>50 && TPW<=60) ? 6" + \
    ": (TPW>60 && TPW<=70) ? 7" + \
    ": (TPW>70 && TPW<=80) ? 8" + \
    ": (TPW>80 && TPW<=90) ? 9" + \
    ": (TPW>90) ? 10" + \
    ": 0",{'TPW': tpw}) \
    .clip(image.geometry())

    # add tpw to image as a band
    withTPW = (image.addBands(tpw.rename('TPW'),['TPW'])).addBands(pos.rename('TPWpos'),['TPWpos'])

    return withTPW
#%% Get ASTER ic with various factors required
def getAsterIC(date_start, date_end, emissivity, geometry, maxCloud=20,  tir=['B13']):
    
    '''
    Collects Aster with the corrections required for temperature extraction
    commented out faster methods/cloud methods due to the band availability and server/client side issues
    '''
    ic = ee.ImageCollection('ASTER/AST_L1T_003').filter(ee.Filter.date(date_start, date_end)).filter(ee.Filter.lt('CLOUDCOVER', maxCloud))
    ic = ic.filterBounds(geometry)
    
    # get TOA using my own code  - (actually better defined as 'at sensor radiance')
    ic =  ic.map(lambda x : OgTOAFunc(x))
    # same for Top of atmosphere brightness temperature
    BT = ic.map(lambda x : BTFunc(x))
    
    # This has been checked and does provide the correct brightness temperature.
    # BT = ic.map(lambda x : AsterPreprocessing.preProcess(x))  
    # BT = BT.map(lambda x:AsterPreprocessing.aster_cloud_mask(x))


    
    # add NCEP bands - uses ermida method
    BT = BT.map(addNCEPband)


    em_image = ee.Image.constant(emissivity).rename('EM')
    
    BT = BT.map(lambda x: x.addBands(em_image))
    
    
    return BT




#******************************************************************************
    # This has been checked and does provide the correct brightness temperature. 

def OgTOAFunc(image):
    
    UCC = ee.Number(0.005693) # does this need to be an ee number
    
    i = image.expression(
  '(im-1)*UCC',
      {'im': image.select('B13'),
      'UCC': UCC,
      }).rename('TOA')
    return image.addBands(i)

#******************************************************************************  
    


 


def BTFunc(image, bands = ['B13']):
  """
  Takes an ASTER image with pixel values in at-sensor radiance.
  Converts TIR bands to at-satellite brightness temperature.
  """
    
  k_vals = {
  'B10':{
    'K1': ee.Number(3040.136402),
    'K2': ee.Number(1735.337945)
  },
  'B11':{
    'K1': ee.Number(2482.375199),
    'K2': ee.Number(1666.398761)
  },
  'B12':{
    'K1': ee.Number(1935.060183),
    'K2': ee.Number(1585.420044)
  },
  'B13':{
    'K1': ee.Number(865.65),
    'K2': ee.Number(1349.82)
  },
  'B14':{
    'K1': ee.Number(641.326517),
    'K2': ee.Number(1271.221673)
  }
  }
  
  K1 = k_vals[bands[0]]['K1']

  K2 = k_vals[bands[0]]['K2']
  

  BT = image.expression(
  'K2/(log((K1/TOA)+1))',
      {'TOA': image.select('TOA'),
      'K1': K1,
      'K2':K2
      }).rename('BT')

  return image.addBands(BT)



###############################################################################
#%% temperature options
###############################################################################

def getTemperature(image, geometry, matrixDF, emissivity, tir='BT'):
    '''
    Single Channel algorithm using matrix values provided by Jimenez-Munoz and Sobrino, 2009
    
    WST = Y[(1/emissivity)*(a*BT + B)+c] + delta
    
    '''
    ###########################################################################
    # Get internal Vars
    ###########################################################################
    K2 = ee.Number(1349.82)

    Y = image.expression('(BT**2)/(K2*TOA)',
                 {'TOA': image.select('TOA'),
                  'BT': image.select(tir),
                  'K2':K2}).rename('Y')
    
    
    delta = image.expression('BT-((BT**2)/K2)',
                 {'BT': image.select(tir),
                  'K2':K2}).rename('delta')
    ###########################################################################
    # Get linear water vapour look ups
    ###########################################################################
    

    a, b, c = GetABC(matrixDF, image)


    ###########################################################################
    # Main Single Channel Algorithm  
    ###########################################################################
    wst = image.expression('Y*((1/e)*((a*BT) + b)+c) + delta', {
                               'Y': Y.select('Y'), 
                               'e': image.select('EM'), 
                               'a': a, 
                               'b': b, 
                               'c': c, 
                               'BT': image.select('TOA'), # tir
                               'delta': delta.select('delta')}).rename('wst')
    wst = wst.expression('lst - 273.15', {'lst':wst.select('wst')}).rename('wst')
    
    ## show your working (because we've had enough of this not working)
    image = image.addBands(Y.select('Y'))
    image = image.addBands(delta.select('delta'))

    return image.addBands(wst.select('wst'))

# https://numpy.org/doc/stable/reference/generated/numpy.matmul.html


def GetABC(matrixDF, image):
    geo = image.geometry()
    # list of features from df
    features = [matrixDFtoEE(index, row, geo) for index, row in matrixDF.iterrows()]
    
    # get into FC
    waterVapourDictionary= ee.FeatureCollection(features)
    

    
    
    ## GEE 
    A_lookup = GEE_GenericFuncs.get_lookup_table(waterVapourDictionary, 'TPWpos', 'A')
    B_lookup = GEE_GenericFuncs.get_lookup_table(waterVapourDictionary, 'TPWpos', 'B')
    C_lookup = GEE_GenericFuncs.get_lookup_table(waterVapourDictionary, 'TPWpos', 'C')

    # Map coefficients to the image using the TPW bin position
    # google ee.remap 
    A = image.remap(A_lookup.get(0), A_lookup.get(1),0.0,'TPWpos').resample('bilinear')
    B = image.remap(B_lookup.get(0), B_lookup.get(1),0.0,'TPWpos').resample('bilinear')
    C = image.remap(C_lookup.get(0), C_lookup.get(1),0.0,'TPWpos').resample('bilinear')
    
    return A,B,C

def matrixDFtoEE(index, row, geometry):
    return ee.Feature(geometry, {'TPWpos':index, 'A': row['a'], 'B':row['b'] , 'C':row['c']})


    

#%% Testing section
# geometry = 'Danube'
# task = 'getDates'
# lists = extractAster(geometry, 
#                 task, 
#                       points=None,
#                       maxCloud=90, 
#                       date_start='2024-06-01', 
#                       date_end='2024-08-01',
#                       emissivity=0.991, 
#                       )
    
