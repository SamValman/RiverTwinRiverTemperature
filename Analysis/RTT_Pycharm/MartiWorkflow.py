# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 12:16:08 2024

@author: lgxsv2
"""
from scipy import ndimage  
import numpy as np
import skimage.io as IO

def pureLandsatPixels(ThrW=0.005, rr=0.005):
    

    
    # find water masks that corrospond to Ls images
    # path to watermasks. 
    
    # radiance path - e.g. actual landsat. 
    
    wm = IO.imread()
    ls = IO.imread()
    
    outputMask = CubicUnmix(wm, ls)
    
    return outputMask
    

def CubicUnmix(wm, ls):
    
    '''Not strictly cubic unmixing'''
    
    Mask30m = 'resize wm to 30m?' # not sure if I want to do this or not
    
    Mask10m = 'resize from 30m to 10m.' # MNDWI10mMask = imresize(MNDWI30mMask, 30/10, 'nearest')


    ###########################################################################
    # Maybe section 2?
    ###########################################################################
    # create 11*11 object to be moved over image, 
    structuringElement = np.ones((11, 11), dtype=bool)
    
    
    erodedBy11 = ndimage.binary_erosion(image, structure=structuringElement)
    
    # not sure why but we do this again with 9*9
    structuringElement = np.ones((9, 9), dtype=bool)

    dilatedby9 = imdilate(erodedBy11, structuringElement) # still matlab version(SMV)

    PureTIR30m = imresize(dilatedby9, 10/30, 'nearest') # SMV
    
    ###########################################################################
    # Cubic convolution?
    ###########################################################################
    ## Creating Variables 
    # these first two are used in incremental implementing things. 
    tot = 100 # total number of itterations to carry out
    dic = 0.4 / tot # distance between each implementation. 
    count = 0
    
    
    H = np.zeros(13) # again same lack of understanding. 
    MaxCond = np.zeros((nrows, ncols)) # lots of vars..
    ErrMaxCond = np.zeros(nrows, ncols);
    

    
    nrows, ncols = Mask30m.shape # get sizes of "original" 30mMask

    Bcubic_30m_N = np.zeros(zeros(nrows, ncols, tot)) # Not sure what the n stands for? maybe empty?
    
    ## E comments: We calculate the maximum contrast between each water pixel and its surroundings
    ##             Of 13 x 13 pixels, only if this surrounding area touches non-water pixels.

    # uses these to make steps, unsure what ic stands for. 
    # increments 100 times through -0.2 to 0.2
    for ic in np.arange(-0.2, 0.2 + dic, dic):
        
        # iteration number
        count+=1
        TIRcontrast = 1 + ic
        
        
        B_10m = Mask10m + TIRcontrast * (Mask10m == 0) # adds this contrast..

        B_100m = imresize(B_10m, 10/100, 'box') 
        
        Bcubic_30m = imresize(B_100m, 100/30, 'bicubic', 'Outputsize', [nrows, ncols])
    
        Bcubic_30m = Mask30m * Bcubic_30m # element wise multiplication

        Bcubic_30m_N[:, :, count] = Bcubic_30m # seems to be making a 3d array for all count options. 
    ###########################################################################
    # the same again for 0.8 to 1.2
    ###########################################################################
    for xic in np.arange(0.8, 1.2 + dic, dic):
        
        yic = zeros(size(xic)) # erm?
        
        # iterate through the rows and columns I'm guessing always 7 from the edges
        for i1 in range(7, nrows - 6 + 1):

            for j1 in range(7, nrows - 6 + 1):
                           
                # Check if the condition holds
                condition1 = Mask30m[i1, j1] == 1
                surrounding_area = Mask30m[i1 - 6:i1 + 7, j1 - 6:j1 + 7]
                condition2 = np.min(surrounding_area) == 0
        
                if condition1 and condition2:
                    # normalise and seperate 13*13 array
                    H = ls[i1 - 6:i1 + 7, j1 - 6:j1 + 7] / ls[i1, j1]
                    # get the max value of this and put it into the larger array
                    maxValue = np.max(H)
                    MaxCond[i1, j1] = maxValue
                    
                    ###########################################################
                    # error from max contrast
                    ###########################################################
                    yic[:] = Bcubic_30m_N[i1, j1, :len(xic)]
                    
                    # linear interpolation
                    ErrMaxCond[i1, j1] =  np.interp(maxValue, xic, yic)
                
                
                else:
                    condition1 = Mask30m[i1, j1] == 1
                    surrounding_area = Mask30m[i1 - 6:i1 + 7, j1 - 6:j1 + 7]
                    condition2 = np.min(surrounding_area) == 1
                    
                    if condition1 and condition2:
                            ErrMaxCond[i1, j1] = 1
    uncorruptedPixels = (ErrMaxCond > 1-rr) & (ErrMaxCond < 1+rr)
    
    return uncorruptedPixels

    # ThrW is probably threshold ater mndwi
    
    
    
#%%
# Matlab functions
 

            # for i1 = 7:nrows - 6 

            #     for j1 = 7:ncols - 6

            #         if and(MNDWI30mMask(i1, j1) == 1, min(min(MNDWI30mMask(i1 - 6:i1 + 6, j1 - 6:j1 + 6))) == 0)

            #             H(1:13, 1:13) = RAD_IMG(i1 - 6:i1 + 6, j1 - 6:j1 + 6) / RAD_IMG(i1, j1);

            #             MaxCond(i1, j1) = max(max(H));

            #             % Error asociado al maximo contraste:

 

                        # yic(1:length(xic)) = Bcubic_30m_N(i1, j1, 1:length(xic));

                        # ErrMaxCond(i1, j1) = interp1(xic, yic, MaxCond(i1, j1), 'linear');

            #         else

 

            #             if and(MNDWI30mMask(i1, j1) == 1, min(min(MNDWI30mMask(i1 - 6:i1 + 6, j1 - 6:j1 + 6))) == 1)

            #                 ErrMaxCond(i1, j1) = 1;

            #             end

 

            #         end

 

            #     end

 

            # end

 

#             PixelsNoCorruptos = and(ErrMaxCond > 1 - rr, ErrMaxCond < 1 + rr);



 

#             PixelsCorrectos = PixelsNoCorruptos .* Mask30mPureTIR;

#             imshow(PixelsCorrectos);

 

#             %                 sum_pixels = sum(sum(PixelsCorrectos));

 

#             % Save files here

#             %             geotiffwrite(fullfile(MASK_path, landsat{1, i}, MNDWI_files{j}), PixelsCorrectos, R, 'GeoKeyDirectoryTag', info.GeoTIFFTags.GeoKeyDirectoryTag);

 

#             geotiffwrite(fullfile(MASK_path, RAD_files{j}), PixelsCorrectos, R, 'GeoKeyDirectoryTag', geoTags);

#             % else

#             %     fprintf("file RAD = %s does not exist \n", MNDWI_files{j})

#             % end

#         end

 

#     end

 

# end