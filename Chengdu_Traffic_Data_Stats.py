#!/usr/bin/env python
# coding: utf-8

# In[7]:


# imports for system basis
import datetime
import csv
import sys
from math import radians, cos, sin, asin, sqrt, degrees
import time
from time import gmtime
from time import strftime
import random
import threading

# imports for web cralwers
import requests
from selenium import webdriver
import requests
from bs4 import BeautifulSoup

# imports for data proccessing
import numpy as np
import pandas as pd
import json


# #### Change Longitude and Latitude Functions
# inputs:
#         `dist = distance bettwen to points, coord_0 = (lng_0, lat_0)`
# 
# outputs:
#         `coord_1 = (lng_1, lat_1)`

# In[37]:


# Radius of Earth
R = 6371 * 1000
# dist = distance bettwen to points
# coord_0 = (lng_0, lat_0)
# return = coord_1
def lng_coord(dist, coord_0):
    lng_0, lat_0 = map(radians, [float(coord_0[0]), float(coord_0[1])])
    dist = dist * 1000
    a = sin(dist / (2*R))**2
    dlng = asin( sqrt( a / cos(lat_0)**2 ) ) * 2
    # Convert from radians to carticien 
    dlng = round(degrees(dlng), 3)
    coord_1 = (coord_0[0] + dlng, coord_0[1])
    return coord_1


def lat_coord(dist, coord_0):
    lng_0, lat_0 = map(radians, [float(coord_0[0]), float(coord_0[1])])
    dist = dist * 1000
    a = sin(dist / (2*R))**2
    dlat = asin( sqrt(a) ) * 2
    # Convert from radians to carticien 
    dlat = round (degrees(dlat), 3)
    coord_1 = (coord_0[0], coord_0[1] - dlat)
    return coord_1


# ### Divides Chengdu as Different Cells
# chengdu's total area is aproximates to 1.4w km^2, however, the center area (those worth to Investigate) is about 17(7km) * 12(7km) = 204 cells to be the input to gaode for road traffic data.
# 
# The start coord is (103.488，31.058).

# #### Extract road
# `print(res[0]['trafficinfo']['roads'][0]['name'])`
# #### Extract sstart and end points of a road
# `print(res[0]['trafficinfo']['roads'][0]['polyline'][:21])`
# `print(res[0]['trafficinfo']['roads'][0]['polyline'][-21:])`
# #### Extract direction
# `print(res[0]['trafficinfo']['roads'][0]['direction'])`
# #### Extract direaction
# `print(res[0]['trafficinfo']['roads'][0]['angle'])`
# #### Flow amount
# `print(res[0]['trafficinfo']['roads'][0]['status'])`
# #### Speed
# `print(res[0]['trafficinfo']['roads'][0]['speed'])`

# In[36]:


# Store all the coordinates of the vertices of points to search
coords =[[(103.488, 31.058)]]

coords[0][0][1]


# In[160]:


# Change of rows (langitude)
for i in range(14):
    # Change of columns (latitude)
    for j in range(17):
        coords_right = lat_coord(7.0, coords[i][j])
        coords[i].append(coords_right)
    if i == 13:
        break
    coords_down = lng_coord(7.0, coords[i][0])
    coords.append([coords_down])
url_param = str(coords[0][0][0]) + ',' + str(coords[0][0][1]) + ';' + str(coords[0+1][0+1][0]) + ',' + str(coords[0+1][0+1][1])
print(url_param)


# In[191]:


# send request to Gaode API
url_pre = 'https://restapi.amap.com/v3/traffic/status/rectangle?key=634048389d7229b18f1cf1973378d207&rectangle='
url_end = '&extensions=all'
res = []
counter = 0
success_counter = 0
for i in range(13):
    for j in range(16):
        print('attempts: ' + str(counter), end='\r')
        url_param = str(coords[i][j][0]) + ',' + str(coords[i][j][1]) + ';' + str(coords[i+1][j+1][0]) + ',' + str(coords[i+1][j+1][1])
        #print(url_param)
        url = url_pre + url_param + url_end
        data = requests.get(url)
        data_json = data.json()
        counter += 1
        if data_json['status'] == '1':
            success_counter += 1
            res.append({'data': data_json, 
                        'time': time.strftime("%Y-%m-%d %a %H:%M:%S"), 
                        'start_lng': coords[i][j][0], 
                        'start_lat': coords[i][j][1],
                        'end_lng': coords[i+1][j+1][0],
                        'end_lat': coords[i+1][j+1][1]})
            print('get area: ' + str(success_counter), end='\r')
            
            
        #try:
            #status.append(data_json['evaluation']['status'])
            #status_desc.append(data_json['evaluation']['status_desc'])
            #times.append(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
            #roads.append(road)

        #except:
          #  print('road: ' + str(road) + ' not found')
print('Successfully got areas: ' + str(counter))            


# ##### Proccess Resulted Data

# In[196]:


# Data storages
road_name = []
road_coords = []
road_dir = []
road_angle = []
road_status = []
road_speed = []
start_lng = []
start_lat = []
end_lng = []
end_lat = []
times = []
data_attrs = [road_name,road_coords,road_dir,road_angle,road_status,road_speed,start_lng,start_lat,end_lng,end_lat,times,]

# area storage
area_status = []
area_start_lng = []
area_start_lat = []
area_end_lng = []
area_end_lat = []
area_time = []
area_number = []
counter = 0

for results in res:
    roads = results['data']['trafficinfo']['roads']
    for road in roads:
        try:
            road_name.append(road['name'])
        except:
            road_name.append('N/A')
        try:
            road_coords.append(road['polyline'])
        except:
            road_coords.append('N/A')
        try:
            road_dir.append(road['direction'])
        except:
            road_dir.append('N/A')
        try:
            road_angle.append(road['angle'])
        except:
            road_angle.append('N/A')
        try:
            road_status.append(road['status'])
        except:
            road_status.append('N/A')
        try:
            road_speed.append(road['speed'])
        except:
            road_speed.append('N/A')
        times.append(results['time'])
        start_lng.append(results['start_lng'])
        start_lat.append(results['start_lat'])
        end_lng.append(results['end_lng'])
        end_lat.append(results['end_lat'])

    area_number.append(counter)
    counter += 1
    area_status.append(results['data']['status'])
    area_start_lng.append(results['start_lng'])
    area_start_lat.append(results['start_lat'])
    area_end_lng.append(results['end_lng'])
    area_end_lat.append(results['end_lat'])
    area_time.append(results['time'])
    

df = pd.DataFrame({
    'name' : road_name,
    'start_lng': start_lng,
    'start_lat': start_lat,
    'end_lng': end_lng,
    'end_lat': end_lat,
    'coords' : road_coords,
    'dir': road_dir,
    'angle': road_angle,
    'status': road_status,
    'speed':road_speed,
    'time': times
})

df_area = pd.DataFrame({
    'area_number': area_number,
    'start_lng': area_start_lng,
    'start_lat': area_start_lat,
    'end_lng': area_end_lng,
    'end_lat': area_end_lat,
    'status': area_status,
    'time' : area_time
})


# In[198]:


df.to_csv('Data/traffic_data.csv', index = False, encoding = 'utf-8-sig')
df_area.to_csv('Data/traffic_area_data.csv', index = False, encoding = 'utf-8-sig')


# ### Drop Duplicates and Merge Road Name
# Dropping those data that does not have a crowdness level and those who has the same road name and direction description.

# In[199]:


df_data = pd.read_csv('traffic_data.csv')

df_data['identifier'] = df_data['name'] + df_data['dir']
df_complete = df_data.drop_duplicates(subset = 'identifier')

# Drop the rows where no traffic status is gathered
indexNames = df_data[ df_data['status'] == 0 ].index
df_data.drop(indexNames , inplace=True)

df_complete.to_csv('Data/traffic_data_without_no_data.csv', encoding = 'utf-8-sig', index = False)


# ## Extract Coordinates of Roads in Block
# The data proccesing proccess requies a lot of calculations that does not requires a lot of memory. Therefore, a multithreading approach is taken
# 
# 
# #### Data Pre-Proccessing
# pre-proccess the data to suffice the mutithreading purpose. 
# 
# Proccess of pre-proccessing:
#  - seperate the rows in dataframe that is sent to different thread
# 
# coords_result = pd.DataFrame(columns=['lng', 'lat', 'road_name', 'status', 'angle'])

# #### Road's Data Points Extraction Method

# In[2]:


def seperate_rows(num_of_thread, data_frame):
    to_op_list = []
    size = data_frame.shape[0]
    op_per_thread = int(size / num_of_thread)
    # Get the first n-1 thread op
    for i in range(num_of_thread - 1):
        df_to_op = data_frame[op_per_thread * i: op_per_thread * (i+1)]
        to_op_list.append(df_to_op)
    # The last thread handles everything
    df_last = data_frame[op_per_thread * (i+1): size]
    to_op_list.append(df_last)
    return to_op_list


# In[3]:


# Inputs:
#    pandas DataFrame that contains the information of roads in each block.
# Functionalities:
#    Extract data from the dataframe.
# Outputs:
#    A pandas DataFrame that contains information of each point in a specific area 
#    with its status and angle and road name.
def coords_to_dict(df):
    # Create an empty data_frame
    result_df = pd.DataFrame(columns=['lng', 'lat', 'road_name', 'status', 'angle'])
    print('The totol rows is: ' + str(df.shape[0]))
    counter = 0
    for row in df.iterrows():
        #print('attempting:' + str (counter), end = '\r')

        road_data = row[1]
        start_lng = road_data['start_lng']
        start_lat = road_data['start_lat']
        end_lng = road_data['end_lng']
        end_lat = road_data['end_lat']
        coords_list = road_data['coords'].split(';')

        for i in range(len(coords_list)):
            lng = float(coords_list[i].split(',')[0])
            lat = float(coords_list[i].split(',')[1])

            # Check if the coord is in the range of its corresponding area
            if ((start_lng < lng < end_lng) and (start_lat > lat > end_lat)):

                result = {'lng': lng, 
                          'lat': lat, 
                          'road_name': road_data['name'], 
                          'status': road_data['status'], 
                          'angle' : road_data['angle']
                         }
                result_df = result_df.append(result, ignore_index = True)
            i += 2
        counter += 1
    return result_df


# In[4]:
'''

# Functionalities:
#    append a dataframe to a dataframe out side in the whole scope which results in coords -> status relationship
class dataProccessThread(threading.Thread):
    # Input: 
    #   counter: the threadID
    #   df:      the whole pandas DataFrame that contains a number of blocks' roads data
    # Functionalities: 
    #   init the thread
    def __init__(self, counter, df, coords_result):
        # super
        threading.Thread.__init__(self)
        # init the thread's id
        self.threadID = counter
        self.data_frame = df
        self.data_coords = df['coords']
        self.start_lngs = df['start_lng']
        self.start_lats = df['start_lat']
        self.end_lngs = df['end_lng']
        self.end_lats = df['end_lat']
        self.coords_result = coords_result
        print('Thread ' + str(self.threadID) + ' start')
        
    def run(self):
        # the original road oriented df to point oriented df
        coords_df = coords_to_dict(self.data_frame)
        threadLock.acquire()
        self.coords_result = self.coords_result.append(coords_df)
        print('Thread ' + str(self.threadID) + ' end')
        threadLock.release()
'''

# In[19]:


coords_result = pd.DataFrame(columns=['lng', 'lat', 'road_name', 'status', 'angle'])
df_road_ori = pd.read_csv('traffic_data_without_no_data.csv')
print(df_road_ori.shape)
result = seperate_rows(16, df_road_ori)
print(len(result))

r_df = coords_to_dict(df_road_ori)
print(r_df.shape)


# In[16]:


r_df.shape
r_df.to_csv('Data/coords_oriented_traffic_data.csv', index = False, encoding = 'utf-8-sig')


# In[20]:


### Attempting Mutithreading Failed (Missing half of the data)
'''
coords_result = pd.DataFrame(columns=['lng', 'lat', 'road_name', 'status', 'angle'])
df_road_ori = pd.read_csv('traffic_data_without_no_data.csv')

print(df_road_ori.shape)
result = seperate_rows(16, df_road_ori)
print(len(result))

# Init the thread list and prepare the threadLock
threads = []
threadLock = threading.Lock()

# Create four threads
for i in range(0, 10):
    thread = dataProccessThread(i, result[i], coords_result)
    threads.append(thread)

# start each thread
for thread in threads:
    thread.start()

# Wait for all threads to complete
for thread in threads:
    coords_result = coords_result.append(thread.coords_result)
    thread.join()

print("\nFinish Proccess All Threads")
print(coords_result.shape)

coords_result.to_csv('coords_oriented_traffic_data.csv', index = False, encoding = 'utf-8-sig')
'''
print('Program Ends')
