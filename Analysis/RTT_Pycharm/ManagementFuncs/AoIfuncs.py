# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 14:48:48 2024

@author: lgxsv2
"""
import numpy as np
import geojson 
from scipy.spatial import distance, ConvexHull

from scipy.interpolate import CubicSpline
import networkx as nx
import matplotlib.pyplot as plt
from pyproj import  Transformer
import pyproj

from shapely.geometry import LineString, Polygon, mapping, shape, Point

import os
import fiona


#%%
class errorClass(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(self.message)

def getOriginalVertices(fp):
    '''
    Just loads json of lines and extracts all available points into lists
    '''
    with open(fp) as f:
        gj = geojson.load(f)
        x = []
        y = []
        for i in gj['features']:
            
            if i['geometry']['type']!= 'LineString':
                print("uh oh at least one of these isn't a line string!")
                continue
            else:
                cList = i['geometry']['coordinates']
                for coordinate in cList:
                    x.append(coordinate[0])
                    y.append(coordinate[1])
        return x, y 


def shufflePoints(x, y, useExample=True):
    '''
    Just a function to mix points to check for errors in organising them

    Parameters
    ----------
    x : TYPE
        DESCRIPTION.
    y : TYPE
        DESCRIPTION.

    Returns: shuffled x and y 
    -------
    None.

    '''
    # Danube points
    if useExample:
        x = [28.034489, 28.033971, 28.013522, 28.012229, 28.012889, 28.017861, 28.02941, 28.03662, 28.041668, 28.042199, 28.04606, 28.06473, 28.076752, 28.089389, 28.093911, 28.098749, 28.109072, 28.110521, 28.110418, 28.104051, 28.083472, 28.053712, 28.028429, 28.020839, 28.02034, 28.015252, 28.01432, 28.011591, 28.003752, 27.996399, 27.980779, 27.976908, 27.955919, 27.952071, 27.937298, 27.92673, 27.912452, 27.883941, 27.863259, 27.849378, 27.818789, 27.799998, 27.783758, 27.765538, 27.742841, 27.736001, 27.725839, 27.686019, 27.671781, 27.649628, 27.637642, 27.604212, 27.590661, 27.572191, 27.568071]
        y = [44.61686, 44.60903, 44.585178, 44.57655, 44.570869, 44.563262, 44.553982, 44.545269, 44.532262, 44.519558, 44.513578, 44.502609, 44.499251, 44.48941, 44.478561, 44.455289, 44.442772, 44.439508, 44.43438, 44.42634, 44.414109, 44.39333, 44.36979, 44.355539, 44.348248, 44.33669, 44.326702, 44.321052, 44.313289, 44.30174, 44.28945, 44.282731, 44.263458, 44.25809, 44.250652, 44.247901, 44.247481, 44.250942, 44.250019, 44.251481, 44.240891, 44.23995, 44.233979, 44.219518, 44.20644, 44.200001, 44.197499, 44.195582, 44.198369, 44.197959, 44.20046, 44.19902, 44.195582, 44.188108, 44.188131]
    # stack together
    points = np.column_stack((x, y))

    # seperate first and last points so rest of code works - otherwise you'd have to select start and end mannually
    first_point = points[0, :]  
    last_point = points[-1, :]
    points = points[1:-1,:]

    # Shuffle the combined array
    np.random.shuffle(points)
    # reorder
    all_points = np.vstack((first_point, points, last_point))

    # Unpack the shuffled array into separate lists
    nx, ny = all_points[:, 0], all_points[:, 1]


    return nx, ny

#%%
def riverCenterlinePointOrder(x, y, plot=True, names='unnamed River' ):
    '''
    

    Parameters
    ----------
    x : list xs
        .
    y : list ys
        .
    startEnd : default False will use first and last points in x,y. 
        otherwise == [[firstx, firsty],[lastx,lasty]]
       
    plot : default True but will be overwritten by verbose or not in wrapl
        prints graphs to show result

    Returns
    -------
    None.

    '''
    # combine x,y
    points = np.column_stack((x,y))
    
    points, first, last = getFirstAndLast(points, names)
    
    

    # Calculate distance matrix from every point to every other
    dist = euclideanDistance(points)

    # Solve TravellingSalesman problem. returns indices 
    newPath = TravellingSalesmanProblem(dist)
    # reorder original list
    orderedPoints = points[newPath[1:]]
    if names == 'Amazon':
        orderedPoints = fixAmazon()
    # Extracting x and y coordinates separately
    u = orderedPoints[:, 0]
    v = orderedPoints[:, 1]
    
    # if plot:
    #     plt.figure(figsize=(8, 6))
    #     plt.scatter(u, v, c=np.arange(len(u)), cmap='viridis', zorder=2)
    #     plt.plot(u, v, color='gray', zorder=1)
    #     plt.scatter(u[0], v[0], color='red', label='Start', zorder=3)
    #     plt.scatter(u[-1], v[-1], color='blue', label='End', zorder=3)
    #     plt.legend()
    #     plt.title(str(names)+': starting with '+str(len(u))+' points')
    #     plt.xlabel('X')
    #     plt.ylabel('Y')
    #     plt.colorbar(label='Step')
    #     plt.grid(True)
    #     plt.show()
    
    return u, v



def getFirstAndLast(points, names):
    if names in ['Danube']:
        
        first = points[0, :]  
        last = points[-1, :] 
    
    # if river defined by lat
    elif names in ['Parana']:
        # sortPoints = sorted(points, key=lambda point: point[1])
        sortPoints = np.sort(points)
        first = sortPoints[0]
        last = sortPoints[-1]
        points = np.vstack((first, points, last))
    elif names in ['Niger']:
        sortPoints = np.sort(points, axis=0)
        first = sortPoints[0]
        last = sortPoints[-1]
        points = sortPoints
        # points = np.vstack((first, points, last))

    #river defined by long
    elif names in ['Amazon']:
        points, first, last = getAmazon()
    #rivers that work with convex hull
    else:
        first, last = find_extrema(points)
        first = points[first, :]
        last = points[last, :]
        points = np.vstack((first, points, last))


        
        
        
    return points, first, last


    
    
def getAmazon():
    '''
Just provides variables because the amazon still doesn't work refardless 
it is not the original points in although if it takes west to east its nearly right

    '''
    points = np.array([[-60.423272, -3.04681 ],
              [-60.41624 , -3.052901],
              [-60.38466 , -3.06177 ]])
             
    first = points[0]
    last = points[-1]
    return points, first, last
def fixAmazon():
    
    orderedPoints = np.array([
       [-59.367241, -3.167558],
       [-59.391788, -3.165881],
       [-59.427951, -3.171759],
       [-59.452499, -3.172521],
       [-59.477042, -3.167308],
       [-59.502369, -3.157209],
       [-59.502641, -3.157079],
       [-59.529851,  -3.141829],
       [-59.546541,  -3.129852],
       [-59.56728 ,  -3.11787 ],
       [-59.58666 ,  -3.101559],
       [-59.604171,  -3.091481],
       [-59.642171,  -3.077698],
       [-59.658612,  -3.073591],
       [-59.683128,  -3.06404 ],
       [-59.69795 ,  -3.061561],
       [-59.70982 ,  -3.062069],
       [-59.721418,  -3.06503 ],
       [-59.732771,  -3.07286 ],
       [-59.755419,  -3.069552],
       [-59.77969 ,  -3.069208],
       [-59.788051,  -3.07055 ],
       [-59.83393 ,  -3.08642 ],
       [-59.85689 ,  -3.100591],
       [-59.883618,  -3.112711],
       [-59.895238,  -3.121629],
       [-59.898088,  -3.126771],
       [-59.89947 ,  -3.138418],
       [-60.000121,  -3.167268],
       [-60.007648,  -3.165262],
       [-60.038719,  -3.144478],
       [-60.056801,  -3.139921],
       [-60.069781,  -3.126949],
       [-60.090039,  -3.113179],
       [-60.105699,  -3.10794 ],
       [-60.112169,  -3.108359],
       [-60.122978,  -3.09891 ],
       [-60.147561,  -3.084338],
       [-60.151882,  -3.079469],
       [-60.15215 ,  -3.07933 ],
       [-60.166998,  -3.074358],
       [-60.16727 ,  -3.07422 ],
       [-60.20235 ,  -3.064009],
       [-60.227981,  -3.059202],
       [-60.237149,  -3.059768],
       [-60.257349,  -3.068499],
       [-60.279992,  -3.073431],
       [-60.290529,  -3.063701],
       [-60.30833 ,  -3.064691],
       [-60.319401,  -3.061329],
       [-60.339601,  -3.069788],
       [-60.34823 ,  -3.06981 ],
       [-60.37226 ,  -3.062011],
       [-60.38466 ,  -3.06177 ],
       [-60.41624 ,  -3.052901],
       [-60.423272,  -3.04681 ]])
    return orderedPoints


def find_extrema(points):
    hull = ConvexHull(points)

    a = points[hull.vertices][:, 0]
    b = points[hull.vertices][:, 1]

    dtab = []
    for n in range(len(hull.vertices)):
        dist = np.sqrt((a - a[n]) ** 2 + (b - b[n]) ** 2)
        m = np.where(dist == np.max(dist))[0][0]
        dtab.append([n, m, np.max(dist)])

    dtab = sorted(dtab, key=lambda x: x[2])
    s = dtab[-1][0]
    e = dtab[-1][1]
    first = hull.vertices[s]
    last = hull.vertices[e]
    # points = np.column_stack((s, e))

    return first, last


def euclideanDistance(points):
    ''' Just gets euclidean distnace between all points'''
    n = len(points)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist_matrix[i, j] = distance.euclidean(points[i], points[j])
    return dist_matrix




def TravellingSalesmanProblem(dist):
    '''
    uses networkx package to find shortest route between first and last that goes through every other point. 
    '''
    G = nx.from_numpy_array(dist)
    tsp_path = nx.approximation.traveling_salesman_problem(G)
    return tsp_path



#%%
def regularPoints(x, y, verbose=True, names='unnamed river'):
    '''
    '''

    
    # find most suited utm
    utm = getUTM(x[0], y[0])

    #original CRS
    # wgs84 = Proj('epsg:4326')
    # utm = Proj('epsg:'+str(utm)) 
    # get in utm for meters
    transformer = Transformer.from_crs(4326, utm, always_xy=True)
    x, y = transformer.transform(x, y) # depreciated needs changing

    # eculidiean distances between all points in order
    dist = (np.diff(x)**2 + np.diff(y)**2)**0.5
    # get cumulative values
    cumulative = np.cumsum(dist)
    cumulative = np.insert(cumulative, 0, 0)  # Inserting a 0 at the beginning to match the length

    # get length of total line
    length = (cumulative[-1]/1000)
    
    # decide on number of points - 1 every km here 
    newPoints = int(length)+1
    # get array for new points
    newPoints = np.linspace(0, length, newPoints)
    
    
    # working here 
    # use splines to interpret new x, ys - create function first
    interpetx = CubicSpline(cumulative, x)
    interpety = CubicSpline(cumulative, y)
    # apply function
    u = interpetx(newPoints * 1000)  # Convert back to meters
    v = interpety(newPoints * 1000)
    
    # put back into wgs
    transformer = Transformer.from_crs(utm, 4326, always_xy=True)

    u, v = transformer.transform(u, v)
    # if  verbose:
    #     plt.figure(figsize=(8, 6))
    #     plt.scatter(u, v, c=np.arange(len(u)), cmap='viridis', zorder=2)
    #     plt.plot(u, v, color='gray', zorder=1)
    #     plt.scatter(u[0], v[0], color='red', label='Start', zorder=3)
    #     plt.scatter(u[-1], v[-1], color='blue', label='End', zorder=3)
    #     plt.legend()
    #     plt.title(str(names)+': '+str(len(u))+' 1km markers')
    #     plt.xlabel('X')
    #     plt.ylabel('Y')
    #     plt.colorbar(label='Step')
    #     plt.grid(True)
    #     plt.show()
    
    return u, v

    
    

def getUTM(x,y):
    '''
    Takes one point and finds best utm value for it 

    Parameters
    ----------
    x : TYPE
        DESCRIPTION.
    y : TYPE
        DESCRIPTION.

    Returns
    -------
    finalEpsg : TYPE
        DESCRIPTION.

    '''
    # Define WGS84 coordinate system
    wgs84 = pyproj.CRS('EPSG:4326')

    #  UTM zones for northern and southern hemispheres
    UTMNorth = [32600 + i for i in range(1, 60)]
    UTMSouth = [32700 + i for i in range(1, 60)]

    # Convert input lat/lon to UTM projection and find the best zone
    finalEpsg = None
    distance = float('inf')
    for epsg in UTMNorth + UTMSouth:
        utm = pyproj.CRS(f'EPSG:{epsg}')
        transformer = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True)
        utm_x, utm_y = transformer.transform(x, y)
        dist = (utm_x - 500000) ** 2 + utm_y ** 2  # Distance from central meridian
        if dist < distance:
            distance = dist
            finalEpsg = epsg

    return finalEpsg



#%%
def trimRiver(u, v, names, verbose):
    
    # find cp for the river in question
    cp = getCP(names)
    
    # make uv a points array
    arr = np.column_stack((u,v))

    # get index of closest midpoint
    cp, cp_index = closestMidPoint(arr, cp)

    # trim to 50km in each direction 
    output = trimDataset(arr, cp_index)
    if verbose:
        plt.figure()
        plt.scatter(u, v, c = 'black')
        plt.scatter(output[:, 0], output[:, 1], c='lightBlue')
        plt.scatter(cp[0], cp[1], c='red')
        plt.show()
    
    return output
    
### internal section 
def getCP(names):
    
    # dictionary of predifined center points (cps) used to download the original centerlines
    cp_dict = {'Amazon':[-60.1, -3.16],
    'Danube':[28.02, 44.35], 
    'Mississippi':[-91.07, 32.02], 
    'Niger':[6.77, 6.17],
    'Nile':[31.2, 27.18],
    'Parana':[-60.78, -32.58],
    'Rhone':[4.75, 45.41],
    'Saint Lawrence':[-72.38, 46.4],
    'Yangtze':[118.95, 32.18],
    'Yellow':[117.94, 32.28]}
    
    # select cp out of dictionary
    cp = cp_dict[names]
    
    return cp 

def closestMidPoint(arr, point):
    # print('internal function for trimRiver')
    # gets the distance between each point - 
    dist = np.linalg.norm(arr-point, axis=1)
    loc = np.argmin(dist)
    
    #loc will be most useful but this can be used to show that middle point stats if needed
    centralPoint = arr[loc]
        
    return centralPoint, loc

def trimDataset(line, cp_loc):
    '''
    Requires line to be in order 
    cp is used to index and then a 101km line is trimmed from the original centreline 
    returns new line 
    '''
    # should produce an array of 100 kms
    start = cp_loc - 50
    end = cp_loc + 50
    
    if start<0 or end > len(line):
        if len(line)>100:
            print('Centre line needs shifting')
            if start<0:
                dif = abs(start-0)
                start = 0
                end = end + dif
            else:
                dif = abs(end-len(line))
                end = len(line)
                start = start - dif
        else:
            raise  errorClass(500, "Centre line is too short") 
    
    output = line[start:end, :]
    
    return output

#%%

def bufferRiver(line, buffer=100, verbose=False):
    
    # convert to metres
    utm = getUTM(line[0,0], line[0,1])
    transformer = Transformer.from_crs(4326, utm, always_xy=True)
    u, v = transformer.transform(line[:,0], line[:,1]) # 
    line = np.column_stack((u,v))

    # buffer line. 
    lines = LineString(line)
    buffered = lines.buffer(buffer)
    
    
    xy = np.array(buffered.exterior.coords.xy)
    xy = xy.T

    # covert back
    transformer = Transformer.from_crs(utm, 4326, always_xy=True)
    u, v = transformer.transform(xy[:,0], xy[:,1])
    output = np.column_stack((u,v))
    
    if verbose:
        plt.plot()
        plt.plot(u, v)
        plt.fill(u, v, alpha=0.3)
        plt.show()
        
    return output


#%%

def savePolygonAsJson(buffered, folder, names):
    polygon = Polygon(buffered)

    # Create a GeoJSON feature
    feature = geojson.Feature(geometry=mapping(polygon), properties={})

    # Create a GeoJSON feature collection
    feature_collection = geojson.FeatureCollection([feature])

    # Save the GeoJSON to a file
    fn = os.path.join(folder, (names+'.geojson'))
    with open(fn, "w") as f:
        geojson.dump(feature_collection, f)
    
    
def savePolygonAsShp(buffered, folder, names):
    
    polygon = Polygon(buffered)

    # Define the schema for the shapefile
    schema = {
        'geometry': 'Polygon',
        'properties': {},
    }

    # Define the filename for the shapefile
    fn = os.path.join(folder, (names + '.shp'))

    # Create the shapefile
    with fiona.open(fn, 'w', 'ESRI Shapefile', schema) as c:
        # Add the polygon to the shapefile
        c.write({
            'geometry': mapping(polygon),
            'properties': {},
        })
        
    
def savePointsAsShp(buffered, folder, names):
    

    # Define the schema for the shapefile
    schema = {
        'geometry': 'Point',
        'properties': {},
    }

    # Define the filename for the shapefile
    fn = os.path.join(folder, (names + '.shp'))

    # Create the shapefile
    with fiona.open(fn, 'w', 'ESRI Shapefile', schema) as c:
        # Add each point to the shapefile
        for point in buffered:
            p = Point(point)
            c.write({
                'geometry': mapping(p),
                'properties': {},
            })
    
    
def savePointsAsJson(buffered, folder, names):
    # Create a GeoJSON feature
    features = [geojson.Feature(geometry=mapping(Point(buffered)), properties={}) for point in buffered]


    # Create a GeoJSON feature collection
    feature_collection = geojson.FeatureCollection(features)

    # Save the GeoJSON to a file
    fn = os.path.join(folder, (names+'.geojson'))
    with open(fn, "w") as f:
        geojson.dump(feature_collection, f)    
    