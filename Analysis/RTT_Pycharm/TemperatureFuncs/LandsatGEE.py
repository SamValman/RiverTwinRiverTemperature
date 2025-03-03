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
from GEE_GenericFuncs import get_lookup_table
ee.Initialize()


def extractLS9(geometry, 
               task, 
                     points=None,
                     maxCloud=20, 
                     date_start='2021-10-31', 
                     date_end='2024-06-01',
                     emissivity=0.991, 
                     ):
    """
    Calculates Water Surface temperature using Landsat 8
    
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
    sat = 'L9'
    ic, satDictionary = getLSIC(sat, date_start,date_end, emissivity, geometry)



    ###########################################################################
    # Quality control
    ###########################################################################
    
    
    # clip to just polygon
    ic = ic.map(lambda im: GEE_GenericFuncs.clip_image(im, geometry))
    

    
    # remove cloud below the maxCloud avg in just polygon. 
    ic = GEE_GenericFuncs.removeCloudyPolygons(ic, maxCloud, varName='cloud')
    
    
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

        # temperature options 
        if task == 'extractValues_atmosphericallyCorrected':
            
            ic = ic.map(lambda x:getTemperature(x, geometry, sat, satDictionary))
            
            # return ic 
        elif task == 'extractValues_uncorrected':
            
            # using LS8 effective wavelength for now 
            ic = ic.map(lambda x:GEE_GenericFuncs.planckInversion(x, band='B10', wavelength=10.904, emissivity=emissivity))
            

        
        
        for p in points:
            # if we can extract a value then do 
            try:
                v = GEE_GenericFuncs.extractPointValue(ic, p)
                listOfOutputPoints.append(v)
            # if extracting a value fails we need to add na
            except:
                listOfOutputPoints.append(None)
        return listOfOutputPoints
        
        
        
        
        
        

    
    
    
def extractLS8(geometry, 
               task, 
                     points=None,
                     maxCloud=20, 
                     date_start='2013-03-18', 
                     date_end='2024-06-01',
                     emissivity=0.991, 
                     ):
    """
    Calculates Water Surface temperature using Landsat 8
    
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
    either getDates, extractValues_atmosphericallyCorrected, extractValues_uncorrected        controls the use of GEE function
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
    sat = 'L8'
    ic, satDictionary = getLSIC(sat, date_start,date_end, emissivity, geometry)
    # clip to just polygon
    ic = ic.map(lambda im: GEE_GenericFuncs.clip_image(im, geometry))
    
    # remove cloud below the maxCloud avg in just polygon. 
    ic = GEE_GenericFuncs.removeCloudyPolygons(ic, maxCloud, varName='cloud')
    
    
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

        # temperature options 
        if task == 'extractValues_atmosphericallyCorrected':
            # atmospherically corrected with ermida code:
            ic = ic.map(lambda x:getTemperature(x, geometry, sat, satDictionary))
            # return ic
        elif task == 'extractValues_uncorrected':
            
            ic = ic.map(lambda x:GEE_GenericFuncs.planckInversion(x,'B10',  wavelength=10.904, emissivity=emissivity))

        
        
        for p in points:
            # if we can extract a value then do 
            try:
                v = GEE_GenericFuncs.extractPointValue(ic, p)
                listOfOutputPoints.append(v)
            # if extracting a value fails we need to add na
            except:
                listOfOutputPoints.append(None)
        return listOfOutputPoints


# #%% Landsat 7    
def extractLS7(geometry, 
               task, 
                     points=None,
                     maxCloud=20, 
                     date_start='1999-05-28', 
                     date_end='2024-01-19',
                     emissivity=0.991, 
                     ):
    """
    Calculates Water Surface temperature using Landsat 8
    
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
    sat = 'L7'
    ic, satDictionary = getLSIC(sat, date_start,date_end, emissivity, geometry)

    # clip to just polygon
    ic = ic.map(lambda im: GEE_GenericFuncs.clip_image(im, geometry))
    
    # remove cloud below the maxCloud avg in just polygon. 
    ic = GEE_GenericFuncs.removeCloudyPolygons(ic, maxCloud, varName='cloud')
    
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

        # temperature options 
        if task == 'extractValues_atmosphericallyCorrected':
            ic = ic.map(lambda x:getTemperature(x, geometry, sat, satDictionary))
            
            
        elif task == 'extractValues_uncorrected':
            ic = ic.map(lambda x:GEE_GenericFuncs.planckInversion(x, wavelength=11.269, emissivity=emissivity))
            
  
        
        
        
        for p in points:
            # if we can extract a value then do 
            try:
                v = GEE_GenericFuncs.extractPointValue(ic, p)
                listOfOutputPoints.append(v)
            # if extracting a value fails we need to add na
            except:
                listOfOutputPoints.append(None)
        return listOfOutputPoints

def extractLS5(geometry, 
               task, 
                    points=None,
                    maxCloud=20, 
                    date_start='1984-04-19', 
                     date_end='2011-11-0',
                     emissivity=0.991, 
                     ):
    """
    Calculates Water Surface temperature using Landsat 8
    
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
    sat = 'L5'
    ic, satDictionary = getLSIC(sat, date_start,date_end, emissivity, geometry)

    # clip to just polygon
    ic = ic.map(lambda im: GEE_GenericFuncs.clip_image(im, geometry))
    
    # remove cloud below the maxCloud avg in just polygon. 
    ic = GEE_GenericFuncs.removeCloudyPolygons(ic, maxCloud, varName='cloud')

    
    
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

        # temperature options 
        if task == 'extractValues_atmosphericallyCorrected':
            ic = ic.map(lambda x:getTemperature(x, geometry, sat, satDictionary))
            
        elif task == 'extractValues_uncorrected':
            ic = ic.map(lambda x:GEE_GenericFuncs.planckInversion(x, wavelength=11.457 , emissivity=emissivity))
            

        
        
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
        "value = (TPW>0 && TPW<=6) ? 0" + \
        ": (TPW>6 && TPW<=12) ? 1" + \
        ": (TPW>12 && TPW<=18) ? 2" + \
        ": (TPW>18 && TPW<=24) ? 3" + \
        ": (TPW>24 && TPW<=30) ? 4" + \
        ": (TPW>30 && TPW<=36) ? 5" + \
        ": (TPW>36 && TPW<=42) ? 6" + \
        ": (TPW>42 && TPW<=48) ? 7" + \
        ": (TPW>48 && TPW<=54) ? 8" + \
        ": (TPW>54) ? 9" + \
        ": 0",{'TPW': tpw}) \
        .clip(image.geometry())

        # add tpw to image as a band
        withTPW = (image.addBands(tpw.rename('TPW'),['TPW'])).addBands(pos.rename('TPWpos'),['TPWpos'])

        return withTPW
def getLSIC(sat, date_start, date_end, emissivity, geometry, maxCloud=20):
    
    constellationDictionary = {
        'L5':{'TOA':ee.ImageCollection('LANDSAT/LT05/C02/T1_TOA'), 
              'SR':ee.ImageCollection('LANDSAT/LT05/C02/T1_L2'), 
              'TIR': ['B6']},
        'L7':{'TOA':ee.ImageCollection('LANDSAT/LE07/C02/T1_TOA'), 
              'SR':ee.ImageCollection('LANDSAT/LE07/C02/T1_L2'), 
              'TIR': ['B6_VCID_2']},
        'L8':{'TOA':ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA'), 
              'SR':ee.ImageCollection('LANDSAT/LC08/C02/T1_L2'), 
              'TIR': ['B10']},
        'L9':{'TOA':ee.ImageCollection('LANDSAT/LC09/C02/T1_TOA'), 
              'SR':ee.ImageCollection('LANDSAT/LC09/C02/T1_L2'), 
              'TIR': ['B10']}
        }
    
    satDictionary = constellationDictionary[sat]
    
    landsatTOA = ee.ImageCollection(satDictionary['TOA'])\
    .filterDate(date_start, date_end)\
    .filterBounds(geometry)\
    .filter(ee.Filter.lt('CLOUD_COVER', maxCloud))
    
    landsatTOA = landsatTOA.map(lambda x :ee.Algorithms.Landsat.simpleCloudScore(x))
    
    landsatSR = ee.ImageCollection(satDictionary['SR'])\
    .filterBounds(geometry)\
    .filterDate(date_start, date_end)\
    .filter(ee.Filter.lt('CLOUD_COVER', maxCloud))\
    .map(addNCEPband)
    
    landsatALL = (landsatSR.combine(landsatTOA.select(satDictionary['TIR']), True)) # true means overwrite bands with the same name
    landsatALL = (landsatALL.combine(landsatTOA.select('cloud'), True)) # true means overwrite bands with the same name

    em_image = ee.Image.constant(emissivity).rename('EM')
    
    landsatALL = landsatALL.map(lambda x: x.addBands(em_image))
    
    return landsatALL, satDictionary
    
def getTemperature(image, geometry, sat, satDictionary):

            #requires the import of SMW so it can use SMW.lookuptable.get_lookup_table()
       
    ############################## Coefficients ##############################
    coeff_SMW_dictionary = {
    'L5': ee.FeatureCollection([
      ee.Feature(geometry, {'TPWpos': 0, 'A': 0.9765, 'B': -204.6584, 'C': 211.1321}),
      ee.Feature(geometry, {'TPWpos': 1, 'A': 1.0229, 'B': -235.5384, 'C': 230.0619}),
      ee.Feature(geometry, {'TPWpos': 2, 'A': 1.0817, 'B': -261.3886, 'C': 239.5256}),
      ee.Feature(geometry, {'TPWpos': 3, 'A': 1.1738, 'B': -293.6128, 'C': 245.6042}),
      ee.Feature(geometry, {'TPWpos': 4, 'A': 1.2605, 'B': -327.1417, 'C': 254.2301}),
      ee.Feature(geometry, {'TPWpos': 5, 'A': 1.4166, 'B': -377.7741, 'C': 259.9711}),
      ee.Feature(geometry, {'TPWpos': 6, 'A': 1.5727, 'B': -430.0388, 'C': 266.9520}),
      ee.Feature(geometry, {'TPWpos': 7, 'A': 1.7879, 'B': -498.1947, 'C': 272.8413}),
      ee.Feature(geometry, {'TPWpos': 8, 'A': 1.6347, 'B': -457.8183, 'C': 279.6160}),
      ee.Feature(geometry, {'TPWpos': 9, 'A': 2.1168, 'B': -600.7079, 'C': 282.4583})
    ]),
    'L7':ee.FeatureCollection([
      ee.Feature(geometry, {'TPWpos': 0, 'A': 0.9764, 'B': -205.3511, 'C': 211.8507}),
      ee.Feature(geometry, {'TPWpos': 1, 'A': 1.0201, 'B': -235.2416, 'C': 230.5468}),
      ee.Feature(geometry, {'TPWpos': 2, 'A': 1.0750, 'B': -259.6560, 'C': 239.6619}),
      ee.Feature(geometry, {'TPWpos': 3, 'A': 1.1612, 'B': -289.8190, 'C': 245.3286}),
      ee.Feature(geometry, {'TPWpos': 4, 'A': 1.2425, 'B': -321.4658, 'C': 253.6144}),
      ee.Feature(geometry, {'TPWpos': 5, 'A': 1.3864, 'B': -368.4078, 'C': 259.1390}),
      ee.Feature(geometry, {'TPWpos': 6, 'A': 1.5336, 'B': -417.7796, 'C': 265.7486}),
      ee.Feature(geometry, {'TPWpos': 7, 'A': 1.7345, 'B': -481.5714, 'C': 271.3659}),
      ee.Feature(geometry, {'TPWpos': 8, 'A': 1.6066, 'B': -448.5071, 'C': 277.9058}),
      ee.Feature(geometry, {'TPWpos': 9, 'A': 2.0533, 'B': -581.2619, 'C': 280.6800})
    ]),
    'L8': ee.FeatureCollection([
      ee.Feature(geometry, {'TPWpos': 0, 'A': 0.9751, 'B': -205.8929, 'C': 212.7173}),
      ee.Feature(geometry, {'TPWpos': 1, 'A': 1.0090, 'B': -232.2750, 'C': 230.5698}),
      ee.Feature(geometry, {'TPWpos': 2, 'A': 1.0541, 'B': -253.1943, 'C': 238.9548}),
      ee.Feature(geometry, {'TPWpos': 3, 'A': 1.1282, 'B': -279.4212, 'C': 244.0772}),
      ee.Feature(geometry, {'TPWpos': 4, 'A': 1.1987, 'B': -307.4497, 'C': 251.8341}),
      ee.Feature(geometry, {'TPWpos': 5, 'A': 1.3205, 'B': -348.0228, 'C': 257.2740}),
      ee.Feature(geometry, {'TPWpos': 6, 'A': 1.4540, 'B': -393.1718, 'C': 263.5599}),
      ee.Feature(geometry, {'TPWpos': 7, 'A': 1.6350, 'B': -451.0790, 'C': 268.9405}),
      ee.Feature(geometry, {'TPWpos': 8, 'A': 1.5468, 'B': -429.5095, 'C': 275.0895}),
      ee.Feature(geometry, {'TPWpos': 9, 'A': 1.9403, 'B': -547.2681, 'C': 277.9953})
    ]), 
    'L9':ee.FeatureCollection([
      ee.Feature(geometry, {'TPWpos': 0, 'A': 0.9751, 'B': -206.2187, 'C': 213.0526}),
      ee.Feature(geometry, {'TPWpos': 1, 'A': 1.0093, 'B': -232.7408, 'C': 230.9401}),
      ee.Feature(geometry, {'TPWpos': 2, 'A': 1.0539, 'B': -253.4430, 'C': 239.2572}),
      ee.Feature(geometry, {'TPWpos': 3, 'A': 1.1267, 'B': -279.1685, 'C': 244.2379}),
      ee.Feature(geometry, {'TPWpos': 4, 'A': 1.1961, 'B': -306.7961, 'C': 251.8873}),
      ee.Feature(geometry, {'TPWpos': 5, 'A': 1.3155, 'B': -346.5312, 'C': 257.2174}),
      ee.Feature(geometry, {'TPWpos': 6, 'A': 1.4463, 'B': -390.7794, 'C': 263.3479}),
      ee.Feature(geometry, {'TPWpos': 7, 'A': 1.6229, 'B': -447.2745, 'C': 268.5970}),
      ee.Feature(geometry, {'TPWpos': 8, 'A': 1.5396, 'B': -427.0904, 'C': 274.6380}),
      ee.Feature(geometry, {'TPWpos': 9, 'A': 1.9223, 'B': -541.7084, 'C': 277.4964}),
    ])}
       
    
    
    
    # collect the one required here
    coeff_SMW = coeff_SMW_dictionary[sat]

    ######################################################################################
    ######################################################################################
    # Create lookups for the algorithm coefficients
    A_lookup = get_lookup_table(coeff_SMW, 'TPWpos', 'A')
    B_lookup = get_lookup_table(coeff_SMW, 'TPWpos', 'B')
    C_lookup = get_lookup_table(coeff_SMW, 'TPWpos', 'C')

    # Map coefficients to the image using the TPW bin position I DONT KNOW WHAT THIS MEANS 
    # google ee.remap 
    A_img = image.remap(A_lookup.get(0), A_lookup.get(1),0.0,'TPWpos').resample('bilinear')
    B_img = image.remap(B_lookup.get(0), B_lookup.get(1),0.0,'TPWpos').resample('bilinear')
    C_img = image.remap(C_lookup.get(0), C_lookup.get(1),0.0,'TPWpos').resample('bilinear')


    tir = ee.String(satDictionary['TIR'][0])
    # compute the LST
    #image.expression is how you write code which is useful to know 
    #not sure what lt and not do but its based on some mask
    #less than finds all pixels valued negatively and Not makes them positive
    lst = image.expression(
      'A*Tb1/em1 + B/em1 + C',
         {'A': A_img,
          'B': B_img,
          'C': C_img,
          'em1': image.select('EM'),
          'Tb1': image.select(tir)
         }).updateMask(image.select('TPW').lt(0).Not()).rename('remapped')


        # If you want Kelivin uncomment below:
    lst = lst.expression('lst - 273.15', {'lst':lst.select('remapped')})

    path = image.get('WRS_PATH')
    row = image.get('WRS_ROW')
    day = ee.Date(image.get('DATE_ACQUIRED')) # previously SENSING_TIME
    day2 = day.advance(2,'day')
    day = day.format()
    cloud_image = ee.ImageCollection(satDictionary['TOA']).filterDate(day,day2)\
    .filterMetadata('WRS_PATH', "equals", path)\
    .filterMetadata('WRS_ROW', "equals", row).first()
    
    
    cloud_im = ee.Algorithms.Landsat.simpleCloudScore(cloud_image)
    quality = cloud_im.select('cloud')
    
    image = image.addBands(quality)
    
    # bqa = ee.ImageCollection("LANDSAT/LC08/C02/T1_TOA").filterDate(day,day2)\
    # .filterMetadata('WRS_PATH', "equals", path)\
    # .filterMetadata('WRS_ROW', "equals", row).first()
    # bqa = bqa.select('BQA')
    # image = image.addBands(bqa)
    
    
    # returns this LST band 
    
    return image.addBands(lst.rename('wst'))
    
    

    

#%% Testing section
# geometry = 'Danube'
# task = 'getDates'
# lists = extractLS9(geometry, 
#                task, 
#                      points=None,
#                      maxCloud=90, 
#                      date_start='2024-01-01', 
#                      date_end='2024-03-01',
#                      emissivity=0.991, 
#                      )
    
