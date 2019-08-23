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
# from selenium import webdriver
from bs4 import BeautifulSoup

# imports for data proccessing
import numpy as np
import pandas as pd
import json

# Radius of Earth
R = 6371 * 1000

class Chengdu_Traffic_Data_Spider:

    def __init__(self):
        self.R = 6371 * 1000

    # Functionalities:
    #   Given the distance between two points, calculate the coordinates of the next 
    #   point given the distance either moving east by longitude or south by latitude 
    # Inputs:
    #   dist = distance bettwen to points
    #   coord_0 = (lng_0, lat_0)
    # Outputs:
    #   return = coord_1
    def lng_coord(self, dist, coord_0):
        lng_0, lat_0 = map(radians, [float(coord_0[0]), float(coord_0[1])])
        dist = dist * 1000
        a = sin(dist / (2*self.R))**2
        dlng = asin( sqrt( a / cos(lat_0)**2 ) ) * 2
        # Convert from radians to carticien 
        dlng = round(degrees(dlng), 3)
        coord_1 = (coord_0[0] + dlng, coord_0[1])
        return coord_1


    def lat_coord(self, dist, coord_0):
        lng_0, lat_0 = map(radians, [float(coord_0[0]), float(coord_0[1])])
        dist = dist * 1000
        a = sin(dist / (2*self.R))**2
        dlat = asin( sqrt(a) ) * 2
        # Convert from radians to carticien 
        dlat = round (degrees(dlat), 3)
        coord_1 = (coord_0[0], coord_0[1] - dlat)
        return coord_1
    
    # Functionalities:
    #    Extract data from the dataframe.
    # Inputs:
    #    pandas DataFrame that contains the information of roads in each block.
    # Outputs:
    #    A pandas DataFrame that contains information of each point in a specific area 
    #    with its status and angle and road name.
    def coords_to_dict(self, df):
        # Create an empty data_frame
        result_df = pd.DataFrame(columns=['lng', 'lat', 'road_name', 'status', 'angle'])
        size = df.shape[0]
        print('The totol rows is: ' + str(size))
        counter = 0
        for row in df.iterrows():
            print('attempting:' + str(round((counter / size) * 100, 2)) + '%', end = '\r')

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

    # Functionalities:
    #   Generate the coordinates for seperating districts in Chengdu and stored as an 
    #   instance variable
    def coords_generator(self):
        # Store all the coordinates of the vertices of points to search
        coords =[[(103.488, 31.058)]]
        # Change of rows (langitude)
        for i in range(14):
            # Change of columns (latitude)
            for j in range(17):
                coords_right = self.lat_coord(7.0, coords[i][j])
                coords[i].append(coords_right)
            if i == 13:
                break
            coords_down = self.lng_coord(7.0, coords[i][0])
            coords.append([coords_down])
        self.coords = coords

    # Functionalities:
    #   Send request to Gaode API via the points that have been calculated before. 
    #   Store the requested data into csv file with pre-determined location
    def gather_data(self):
        print('Start Gathering Data From API')
        coords = self.coords
        # send request to Gaode API
        url_pre = 'https://restapi.amap.com/v3/traffic/status/rectangle?key=634048389d7229b18f1cf1973378d207&rectangle='
        url_end = '&extensions=all'
        res = []
        counter = 0
        success_counter = 0
        for i in range(13):
            for j in range(16):
                print('attempts: ' + str(round((counter / (13*16)) * 100, 2)) + '%', end='\r')
                url_param = str(coords[i][j][0]) + ',' + str(coords[i][j][1]) + ';' + str(coords[i+1][j+1][0]) + ',' + str(coords[i+1][j+1][1])
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
                    
                #try:
                    #status.append(data_json['evaluation']['status'])
                    #status_desc.append(data_json['evaluation']['status_desc'])
                    #times.append(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
                    #roads.append(road)

                #except:
                #  print('road: ' + str(road) + ' not found')
        print('Successfully got areas: ' + str(counter))
        print('Finish Requesting Data From API')            
        
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
        #data_attrs = [road_name,road_coords,road_dir,road_angle,road_status,road_speed,start_lng,start_lat,end_lng,end_lat,times,]

        # Area storage
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

        df_area.to_csv('Data/Area_Info.csv', mode = 'a', index = False, header=False, encoding = 'utf-8-sig')
        df.to_csv('Raw_Data/Api_Return_Data.csv', mode = 'a', index = False, header=False, encoding = 'utf-8-sig')
        print('Finish Storing Data From API')   

    # Functionalities:
    #   Drop the duplicates via the description and road name attributes.
    #   Drop the data that does not provides traffic information about a road.
    #   Store the resulted data in csv with pre-determined directories
    def road_data_proccess(self):
        print('Start Proccessing Road Data')
        df_data = pd.read_csv('Raw_Data/Api_Return_Data.csv')

        df_data['identifier'] = df_data['name'] + df_data['dir']
        df_road_ori = df_data.drop_duplicates(subset = 'identifier')

        # Drop the rows where no traffic status is gathered
        indexNames = df_data[ df_data['status'] == 0 ].index
        df_data.drop(indexNames , inplace=True)
        self.df_road_ori = df_road_ori
        df_road_ori.to_csv('Data/Road_Ori_Traffic_Data.csv', mode = 'a', header=False, encoding = 'utf-8-sig', index = False)
        print('Finish Proccessing Road Data')
    # Functionalities:
    #   Through the road data, found the coordinates within the block and its corresponding status.
    #   Store the resulted data in csv with pre-determined directories
    def coords_data_proccess(self):
        # coords_result = pd.DataFrame(columns=['lng', 'lat', 'road_name', 'status', 'angle'])
        print('Start Proccessing Coords Data')
        coords_df = self.coords_to_dict(self.df_road_ori)
        print(coords_df.shape)
        print('Finish Proccessing Coords Data')
        coords_df.to_csv('Data/Coords_Ori_Traffic_Data.csv', mode = 'a', header = False, index = False, encoding = 'utf-8-sig')
    
    
    # Functionalities:
    #   Execute the methods accordingly
    def run(self):
        self.coords_generator()
        self.gather_data()
        self.road_data_proccess()
        self.coords_data_proccess()

if __name__ == '__main__':
    spider = Chengdu_Traffic_Data_Spider()
    spider.run()