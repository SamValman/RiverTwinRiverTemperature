# -*- coding: utf-8 -*-
"""
Created on Fri May 24 11:26:43 2024
Two funcs here, (might become more with checking ready to download): PSSearch, PSDownload
@author: lgxsv2
"""
class SessionError(Exception):
    def __init__(self, message):
        super().__init__(message)
        
import os
import requests
import json
from planet import Auth, reporting
from planet import Session, DataClient, OrdersClient
import asyncio
#%%
##
def PSSearch(geom, dateStart, dateEnd,API_KEY):
    '''
    searches the PS archive based on a start and end date, and a geom.
    Params
    ----------
    geom : [[]]
        Reach
    dateStart : 'yyyy-mm-dd'
    dateEnd : 'yyyy-mm-dd'
    API_KEY : str 
        Account str

    Returns
    -------
    list of dates. just a list 'yyyymmdd' not formatted so it can be used however desired.

    '''
    #### set up the api session
    session, URL = openSession(API_KEY)
   
    # search url
    quick_url = "{}/quick-search".format(URL)

    # just planetscope
    item_types = ["PSScene"]
 
    #### Variables
    # from the reach buffer we make geometry to search
    geom = {
    "type": "Polygon",
    "coordinates": geom
        }
    
    DS = dateStart+"T00:00:00.000Z"
    DE = dateEnd+"T00:00:00.000Z"
    
    #### filters for vars
    # ignoreing cloud until I can do some big brain thinking about the method. 
    geometry_filter = {
    "type": "GeometryFilter",
    "field_name": "geometry",
    "config": geom
                        }
    date_filter = {
    "type": "DateRangeFilter", # Type of filter -> Date Range
    "field_name": "acquired", # The field to filter on: "acquired" -> Date on which the "image was taken"
    "config": {"gte": DS, "lte":DE }
                       }
    
    # cloud just set to less 20 for now
    cloud_filter = {
  "type": "RangeFilter",
  "field_name": "cloud_cover",
  "config": {"lt": 0.2}
                  }


    #combine with an and filter
    and_filter = {
    "type": "AndFilter",
    "config": [geometry_filter, date_filter, cloud_filter]
                }
    #### Post request
    request = {
    "item_types" : item_types,
    "filter" : and_filter
        }
    
    itemsFound = []
    
    ## one normal search first
    res = session.post(quick_url, json=request)

    
    
    # goes through the available pages with url search to get max number of images
   
    while True:
        if res.status_code==200:
            res_json = res.json()
            itemsInThisPage = res_json['features']
            if not itemsInThisPage:
                break
            itemsFound.extend(itemsInThisPage)
            
            # checks if another page and if so changes url to the next
            if "_links" in res_json and "_next" in res_json['_links']:
                quick_url = res_json["_links"]["_next"]
                res = session.get(quick_url)

            else:
                break
        
        else: 
            # print(res.json())
            raise SessionError(f'There is a problem with the search: {res.status_code}')
    

        
        

    # get a list of dates out 
    print(f'Search successful! {len(itemsFound)} items found')

    listOfDates = [i['id'][:8] for i in itemsFound] 
    outputIds = [i['id'] for i in itemsFound]
    
    session.close()
    return listOfDates, outputIds

#%%

async def PSDownload(geom, dates, AllIds, key):
    '''
    Takes the PS dates and activates the images
    might soon just be downloads the images..

    '''
    ###########################################################################
    ## Session control ##
    ###########################################################################
    #  orders URL
    URL = 'https://api.planet.com/compute/ops/orders/v2' 
    headers = {'content-type': 'application/json'}


    ###########################################################################
    ## Sets up the tools for the download ##
    ###########################################################################
    
    # clip to the reach. 
    clip_aoi = {"type":"Polygon", 
                "coordinates": geom}
    # define the clip tool 
    clip = {"clip": {"aoi":clip_aoi}}
    
    # composite - to be used if more than one image per date - safest way to have full coverage
    composite = {"composite":{  }}

    tools = [clip, composite]
    


    ###########################################################################
    ## downloadable ids ##
    ###########################################################################
    ## replaced with ids direct from search
    # # go through the result and collect all image ids 
    # searchResults = res.json()
    # AllIds = [feature['id'] for feature in searchResults['features']]
    
    ###########################################################################
    ## run with asynch? 
    ###########################################################################
    download = await CreateAndDownloadOrders(dates, AllIds, tools, key)

    return download
#%%

    
#%%
## shared funcs ##############################################################
def openSession(API_KEY):
    URL = "https://api.planet.com/data/v1"
    session = requests.Session()
    # Authenticate
    session.auth = (API_KEY, "")
    # check functioning
    res = session.get(URL)
    if res.status_code==200:
        print('Session begun')
    else: 
        raise SessionError(f'There is a problem starting the session: {res.status_code}')
    return session, URL

#%%
async def poll_and_download(request, auth):
    async with Session(auth=auth) as sess:
        cl = OrdersClient(sess)

        # Use "reporting" to manage polling for order status
        with reporting.StateBar(state='creating') as bar:
            
            order = await cl.create_order(request)
            
            # Grab the order ID
            bar.update(state='created', order_id=order['id'])

            # poll...poll...poll...
            await cl.wait(order['id'], callback=bar.update_state)

        # if we get here that means the order completed. Yay! Download the files.
        filenames = await cl.download_order(order['id'])
        return filenames
#%%
async def CreateAndDownloadOrders(dates, AllIds, tools, api_key):
    auth = Auth.from_key(api_key)

    clip, composite = tools[0], tools[1]
    if type(dates)!= list:
        dates = [dates]

    for i in dates:
        IdsToDownload = [anId for anId in AllIds if anId[:8] in i]
        if len(IdsToDownload)==0:
            print(IdsToDownload)
            continue
         # put the ids to be downloaded into products to be downloaded PS and
        products = [{"item_ids": IdsToDownload ,
                      "item_type": "PSScene",
                      "product_bundle": "analytic_sr_udm2"}]

        if len(IdsToDownload)>1:
             runComposite = True
        else:
             runComposite = False
     
        if runComposite:
             request = {"name":f'Valman_{i}_rivermasks',
                        "products": products,
                        "tools":[clip, composite]}
        else: 
             request = {"name":'Valman_{i}_rivermasks',
                        "products": products,
                        "tools":[clip]}
        try:
            download =  await poll_and_download(request, auth)
        except Exception as e:
            error_message = str(e)
            if "No access to assets" in error_message and "Unable to accept order" in error_message:
                continue

        return download
    
    # async with Session() as sess:
    #     cl = OrdersClient(sess)
#%% TWO below are old
# async def poll_and_download(order):
#     async with Session() as sess:
#         cl = OrdersClient(sess)

#         # Use "reporting" to manage polling for order status
#         with reporting.StateBar(state='creating') as bar:
#             # Grab the order ID
#             bar.update(state='created', order_id=order['id'])

#             # poll...poll...poll...
#             await cl.wait(order['id'], callback=bar.update_state)

#         # if we get here that means the order completed. Yay! Download the files.
#         filenames = await cl.download_order(order['id'])
#         return filenames
# #%%
# async def CreateAndDownloadOrders(dates, AllIds, tools):
#     async with Session() as sess:
#         cl = OrdersClient(sess)
#         clip, composite = tools[0], tools[1]
#         for i in dates:
#             IdsToDownload = [anId for anId in AllIds if anId[:8] in i]
     
     
#              # put the ids to be downloaded into products to be downloaded PS and 
#             products = [{"item_ids": IdsToDownload ,
#                           "item_type": "PSScene",
#                           "product_bundle": "analytic_sr_udm2"}]
     
#             if len(IdsToDownload)>1:
#                  runComposite = True
#             else:
#                  runComposite = False
         
#             if runComposite:
#                  request = {"name":'some kind of name that needs to be defined somehow', #** I NEED TO FIX THIS 
#                             "products": products,
#                             "tools":[clip, composite]}
#             else: 
#                  request = {"name":'some kind of name that needs to be defined somehow', #** I NEED TO FIX THIS 
#                             "products": products,
#                             "tools":[clip]}

#             order = await cl.create_order(request)
#             download = await poll_and_download(order)
#             return download
                
        
        
        
        
        
        
        
        
#%% *******************************************
### OLD CODE THAT COULD BE HELPFUL IF WE MOVE AWAY FROM PLANET PACKAGE
# def downloadFromURL(url, API_KEY, filename=None):
    
#     # Send a GET request to the provided location url, using your API Key for authentication
#     res = requests.get(url, stream=True, auth=(API_KEY, ""))
#     # If no filename argument is given
#     if not filename:
#         # Construct a filename from the API response
#         if "content-disposition" in res.headers:
#             filename = res.headers["content-disposition"].split("filename=")[-1].strip("'\"")
#         # Construct a filename from the location url
#         else:
#             filename = url.split("=")[1][:10]
#     # Save the file
#     with open('output/' + filename, "wb") as f:
#         for chunk in res.iter_content(chunk_size=1024):
#             if chunk: # filter out keep-alive new chunks
#                 f.write(chunk)
#                 f.flush()

#     return filename
#%%
######## Testing and training tools ######
# API_KEY = 'KEY'

# geom = [-90,40]
# ds, de = "2020-01-01", "2021-01-01"
# a = PSSearch(geom, ds, de, API_KEY)