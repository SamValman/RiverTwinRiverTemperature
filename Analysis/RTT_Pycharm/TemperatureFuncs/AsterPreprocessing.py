# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 11:03:15 2024

@author: lgxsv2

These are the required parts of The ASTER preprocessing toolbox found here:
    https://github.com/Mining-for-the-Future/ASTER_preprocessing
    
Issues with packages and how they have set up GEE mean that it is easier to rewrite it


"""
import ee



#%%
def preProcess(image, bands=['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B10', 'B11', 'B12', 'B13', 'B14']):
   """
   Converts the specified bands in an image from digital number to 
   at-sensor reflectance (VIS/SWIR) and at-satellite brightness temperature (TIR),
   then applies the specified masks (snow, water, and cloud).
   
   Wrapper function that takes an aster image and converts all pixel values from 
   digital number to radiance and then converts the specified bands from radiance
   to top-of-atmosphere reflectance (bands 1 - 9) and at-satellite brightness temperature (bands 10 - 14).

   """   
   img = __aster_radiance__(image)
   TOAband = img.select('B13').rename('TOA')
   
   img = __call_function_with_bands__(img, bands, ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09'], __aster_reflectance__)
   img = __call_function_with_bands__(img, bands, ['B10', 'B11', 'B12', 'B13', 'B14'], __aster_brightness_temp__)
   
   return ee.Image(img).addBands(TOAband)

#%%
def __aster_radiance__(image):
  """
  Takes an ASTER image with pixel values in DN (as stored by Googel Earth Engine).
  Converts DN to at-sensor radiance across all bands.
  """
  coefficients = ee.ImageCollection(
        image.bandNames().map(lambda band: ee.Image(image.getNumber(ee.String('GAIN_COEFFICIENT_').cat(band))).float())
    ).toBands().rename(image.bandNames())

  radiance = image.subtract(1).multiply(coefficients)

  return ee.Image(image.addBands(radiance, None, True))
#%%
def __call_function_with_bands__(image, user_bands, required_bands, function):
    """
    A function that calls another function with specified bands. 
    
    Args:
        image: The image to operate on.
        user_bands: The bands provided by the user.
        required_bands: The bands required for the operation.
        function: The function to be called with the specified bands.
    
    Returns:
        The result of calling the function on the image with the specified bands.
    """
    if len(user_bands) == 0:
        bands = image.bandNames()
    else:
        bands = ee.List(user_bands)

    bands = bands.filter(ee.Filter.inList('item', required_bands))
    return ee.Image(ee.Algorithms.If(bands.length().eq(0), trueCase = __no_valid_bands_result__(image), falseCase = function(image, bands)))

def __no_valid_bands_result__(image):
    """
    A function that handles the case when no valid bands are found in an image.

    Args:
        image (any): The image for which valid bands are being checked.

    Returns:
        any: The original image if no valid bands are found.

    Raises:
        UserWarning: If no valid bands are found in the image.
    """
    # print(f"No valid bands found in image. Function not run.")
    return image


#%% The work horses


def __aster_reflectance__(image, bands):
  """
  Takes an ASTER image with pixel values in at-sensor radiance.
  Converts VIS/SWIR bands (B01 - B09) to at-sensor reflectance.
  """
  
  dayOfYear = image.date().getRelative('day', 'year')

  earthSunDistance = ee.Image().expression(
        '1 - 0.01672 * cos(0.01720209895 * (dayOfYear - 4))',
        {'dayOfYear': dayOfYear}
    )

  sunElevation = image.getNumber('SOLAR_ELEVATION')

  sunZen = ee.Image().expression(
        '(90 - sunElevation) * pi/180',
        {'sunElevation': sunElevation, 'pi': 3.14159265359}
    )

  reflectanceFactor = ee.Image().expression(
        'pi * pow(earthSunDistance, 2) / cos(sunZen)',
        {'earthSunDistance': earthSunDistance, 'sunZen': sunZen, 'pi': 3.14159265359}
    )

  irradiance_vals = ee.Dictionary(dict(zip(
    ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09'],
    [1845.99, 1555.74, 1119.47, 231.25, 79.81, 74.99, 68.66, 59.74, 56.92]
  )))
    
  irradiance = bands.map(lambda band: irradiance_vals.get(band))
  irradiance = ee.Image.constant(irradiance)

  # The .select() method requires two lists, one for the band selection and one for the new names.
  reflectance = image \
        .select(bands, bands) \
        .multiply(reflectanceFactor) \
        .divide(irradiance)

  return ee.Image(image.addBands(reflectance, None, True))

def __aster_brightness_temp__(image, bands = []):
  """
  Takes an ASTER image with pixel values in at-sensor radiance.
  Converts TIR bands to at-satellite brightness temperature.
  """
    
  k_vals = ee.Dictionary({
  'B10':{
    'K1': 3040.136402,
    'K2': 1735.337945
  },
  'B11':{
    'K1': 2482.375199,
    'K2': 1666.398761
  },
  'B12':{
    'K1': 1935.060183,
    'K2': 1585.420044
  },
  'B13':{
    'K1': 866.468575,
    'K2': 1350.069147
  },
  'B14':{
    'K1': 641.326517,
    'K2': 1271.221673
  }
  })
  
  K1_vals = bands.map(lambda band: ee.Dictionary(k_vals.get(band)).get('K1'))
  K1_vals = ee.Image.constant(K1_vals)

  K2_vals = bands.map(lambda band: ee.Dictionary(k_vals.get(band)).get('K2'))
  K2_vals = ee.Image.constant(K2_vals)
  
  T = image.expression('K2 / (log(K1/L + 1))',
                   {'K1': K1_vals, 'K2': K2_vals, 'L': image.select(bands)}
  )

  return ee.Image(image.addBands(T.rename(bands), None, True))



#%% Cloud coverage from: https://github.com/Mining-for-the-Future/ASTER_preprocessing/blob/main/ASTER_preprocessing/masks.py

def aster_ndsi(image):
  """
  Takes an ASTER image and calculates the Normalized Difference Snow Index.
  Returns an image with a single band.
  """
  if image.bandNames().containsAll(['B01', 'B04']):
    return (image.select('B01').subtract(image.select('B04')).divide((image.select('B01').add(image.select('B04'))))).rename('ndsi')
  else:
    raise ValueError("Image is missing required bands for NDSI calculation ('B01', 'B04')")
    
def ac_filt1(image):
  """
  Takes an ASTER image and applies filter 1 in the first pass of Hulley and Hook's (2008) NACMA.
  Returns a masked image.
  """
  filt1 = image.select('B02').gt(0.08)
  return image.updateMask(filt1)

def ac_filt2(image):
  """
  Takes an ASTER image and applies filter 2 in the first pass of Hulley and Hook's (2008) NACMA.
  Returns a masked image.
  """  
  filt2 = aster_ndsi(image).lt(0.7)
  return image.updateMask(filt2)

def ac_filt3(image):
  """
  Takes an ASTER image and applies filter 3 in the first pass of Hulley and Hook's (2008) NACMA.
  Returns a masked image.
  """
  filt3 = image.select('B13').lt(300)
  return image.updateMask(filt3)

def ac_filt4(image):
  """
  Takes an ASTER image and applies filter 4 in the first pass of Hulley and Hook's (2008) NACMA.
  Returns a masked image.
  """
  filt4 = ((image.select('B04').multiply(-1)).add(1)).multiply(image.select('B13')).lt(240)
  return image.updateMask(filt4)

def ac_filt5(image):
  """
  Takes an ASTER image and applies filter 5 in the first pass of Hulley and Hook's (2008) NACMA.
  Returns a masked image.
  """
  filt5 = image.select('B3N').divide(image.select('B02')).lt(2)
  return image.updateMask(filt5)

def ac_filt6(image):
  """
  Takes an ASTER image and applies filter 6 in the first pass of Hulley and Hook's (2008) NACMA.
  Returns a masked image.
  """
  filt6 = image.select('B3N').divide(image.select('B01')).lt(2.3)
  return image.updateMask(filt6)

def ac_filt7(image):
  """
  Takes an ASTER image and applies filter 7 in the first pass of Hulley and Hook's (2008) NACMA.
  Returns a masked image.
  """
  filt7 = image.select('B3N').divide(image.select('B04')).gt(0.83)
  return image.updateMask(filt7)

def aster_cloud_mask(image):
  """
  Takes an ASTER image and applies the seven filters in the first pass
  of the New Aster Cloud Mask Algorithm (NACMA) proposed by Hulley and Hook (2008).
  Returns a masked image.
  """
  if image.bandNames().containsAll(['B01', 'B02', 'B3N', 'B04', 'B13']):
    img = ac_filt1(image)
    img = ac_filt2(img)
    img = ac_filt3(img)
    img = ac_filt4(img)
    img = ac_filt5(img)
    img = ac_filt6(img)
    img = ac_filt7(img)
    # The seven filters identify pixels that ARE clouds and mask the rest.
    # ee.Image.unmask() replaces the masked pixels of an image with a constant value.
    # The .eq() filter returns a binary mask identifying which pixels match the
    # constant value assigned in the unmask() method, i.e., pixels that ARE NOT clouds.
    mask = img.unmask(ee.Image.constant(-1)).eq(-1).eq(0).select('B01').rename('cloud')

    return image.addBands(mask)

  else:
    print('anything')
    raise ValueError("Image is missing required bands for cloud mask calculation ('B01', 'B02', 'B3N', 'B04', 'B13')")
 
    
