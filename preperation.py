import pandas as pd

# Store the area data:
df_area = pd.DataFrame(columns = ['area_number', 'start_lng', 'start_lat', 'end_lng', 'end_lat', 'status', 'time'])
df_area.to_csv('Data/Area_Info.csv', index = False, encoding = 'utf-8-sig')

# Store the raw data from Gaode API
df_raw_data = pd.DataFrame(columns = ['name','start_lng','start_lat','end_lng','end_lat','coords','dir','angle','status','speed','time'])
df_raw_data.to_csv('Raw_Data/Api_Return_Data.csv', index = False, encoding = 'utf-8-sig')

# Store the optimized road oriented data
df_opt = pd.DataFrame(columns = ['name','start_lng','start_lat','end_lng','end_lat','coords','dir','angle','status','speed','time'])
df_opt.to_csv('Data/Road_Ori_Traffic_Data.csv', index = False, encoding = 'utf-8-sig')

# Store the coord oriented data
df_coords = pd.DataFrame(columns=['lng', 'lat', 'road_name', 'status', 'angle'])
df_coords.to_csv('Data/Coords_Ori_Traffic_Data.csv', index = False, encoding = 'utf-8-sig')