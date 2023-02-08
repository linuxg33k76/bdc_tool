#! /usr/bin/env python3

import math
from timeit import default_timer as Timer
from multiprocessing import Process
from tqdm import tqdm
from geopy import distance
from library import FileHandlerClass as FHC



def print_with_header(text):
    term_width = FHC.MiscTools().get_terminal_width()

    if term_width > 120:
        columns = 120
    else:
        columns = term_width

    padding = int((columns - len(text))/2)

    print('*'*columns + '\n' + ' '*padding + text + '\n' + '*'*columns + '\n')


# def iterate_loop(bdc_item, data):

    
#     # bdc_items = data['bdc_items']
#     sm_items = data['sm_items']
#     bdc_header = data['bdc_header']
#     sm_header = data['sm_header']
#     search_area = data['search_area']
#     out_file = data['output_file']

#     match_counter = 0

#     bdc_array = bdc_item.strip('\n').replace('"','').split(',')

#     bdc_record = dict(zip(bdc_header, bdc_array))
    
#     # print(bdc_record)

#     center_point = [{'lat': float(bdc_record['latitude']), 'lng': float(bdc_record['longitude'])}]

#     # Loop through SM data to find a point within the range (skip the first line which is header info)

#     for sm_item in sm_items:

#             sm_array = sm_item.strip('\n').replace('"','').split(',')

#             sm_record = dict(zip(sm_header, sm_array))

#             test_point = [{'lat': float(sm_record['GIS LAT']), 'lng': float(sm_record['GIS LON'])}]
#             radius = float(search_area) # in feet

#             dis = test_for_match(center_point, test_point)

#             if dis <= radius:
#                 # print(f'Distance: {dis:0.2f} ft')
#                 # print(f'{test_point_tuple} point is inside the {user_feet} ft radius from {center_point_tuple} coordinate')
#                 '''
#                 Out File Headers
#                 "location_id","address_primary","city","state","zip","zip_suffix","unit_count","bsl_flag","building_type_code","land_use_code","address_confidence_code","county_geoid","block_geoid","h3_9","latitude","longitude","FullAddress","Service","GIS_LAT","GIS_LON","Distance","Match_Flag"
#                 '''
#                 data_to_write = bdc_item.strip('\n') + ',' + sm_record['FullAddress'] + ',' + sm_record['Service'] + ',' + sm_record['GIS LAT'] + ',' + sm_record['GIS LON'] + ',' + str(dis) + ',TRUE\n'
#                 out_file.write_append_to_file(data_to_write)
#                 match_counter += 1

#             else:
#                 pass

#     return (bdc_item, match_counter)

def test_for_match(center_point, test_point):

    center_point_tuple = tuple(center_point[0].values())
    test_point_tuple = tuple(test_point[0].values())

    try:
        dis = distance.great_circle(center_point_tuple, test_point_tuple).feet #WGS 84 Earth Radius
    except:
        # exception_counter =+ 1
        pass

    return dis

def write_record(data, ofile):
    for item in data:
        ofile.write_append_to_file(item)


# Created by ChatGPT3 (modified)
def haversine(lat1, lon1, lat2, lon2):

    # Convert Strings to Floats
    lat1 = float(lat1)
    lat2 = float(lat2)
    lon1 = float(lon1)
    lon2 = float(lon2)

    R = 20_902_766  # radius of Earth in feet
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2) + (math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) * (math.sin(dlon / 2) ** 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def find_close_points(data, bdc_item):

    bdc_header = data['bdc_header']
    sm_header = data['sm_header']
    out_file = data['output_file']
    locations = data['sm_items']
    threshold_distance = float(data['search_area'])

    # Create an addressible dictionary record
    bdc_array = bdc_item.strip('\n').replace('"','').split(',')
    bdc_record = dict(zip(bdc_header, bdc_array))

    results = []
    for location in locations:

        # Create an addressible dictionary record
        loc_array = location.strip('\n').replace('"','').split(',')
        loc_record = dict(zip(sm_header, loc_array))

        # Test for NULL
        if loc_record['Latitude'].upper() != 'NULL' and loc_record['Longitude'].upper() != 'NULL':      
            distance = haversine(bdc_record['latitude'], bdc_record['longitude'], loc_record['Latitude'], loc_record['Longitude'])
            if distance <= threshold_distance:
                results.append(bdc_item.strip('\n') + ',' + loc_record['FullAddress'] + ',' + loc_record['Service'] + ',' + loc_record['Latitude'] + ',' + loc_record['Longitude'] + ',' + loc_record['Company'] +',' + str(distance) + ',TRUE\n')

    if results != []:
        write_record(results, out_file)
    else:
        # write data w/o a match
        results.append(bdc_item.strip('\n') + ',' + ',' + ',' + ',' + ',' + ',' ',FALSE\n')
        write_record(results, out_file)



# End of ChatGPT3 section (modified)

def main():

    print_with_header('Welcome to the BDC Fabric Comparison Tool')

    

    # Get user inputs
    while True:
        bdc_csv_file = input('Please enter path and filename of BDC_Active_BSL CSV file: ')
        if FHC.MiscTools.file_check(bdc_csv_file) is True:
            break
    while True:
        sm_csv_file = input('Please enter path and filename of ServicesManager CSV: ')
        if FHC.MiscTools.file_check(sm_csv_file) is True:
            break
    out_csv_file = input('Please enter path and filename of Output CSV file: ')
    search_area = input('What is your search radius in feet? ')

    # TODO: Sanitize User Inputs

    # Simulated Inputs for TESTING PURPOSES
    # bdc_csv_file = '/home/bcalvert/Data/FCC_Active_BSL.csv'
    # sm_csv_file = '/home/bcalvert/Data/All_SM.csv'
    # out_csv_file = '/home/bcalvert/Data/output/All_SM_FCC_Report.csv'
    # search_area = '50'

    # Set FHC instances
    bdc_file = FHC.FileHandler(bdc_csv_file)
    sm_file = FHC.FileHandler(sm_csv_file)
    out_file = FHC.FileHandler(out_csv_file)

    # Get Data
    bdc_header = bdc_file.get_csv_header()
    bdc_data = bdc_file.read_file()
    sm_header = sm_file.get_csv_header()
    sm_data = sm_file.read_file()

    # Set Output Header Data
    out_file_header = bdc_data[0].strip('\n') + ',"FullAddress","Service","SM_LAT","SM_LON","Company","Distance","Match_Flag"\n'
    out_file.write_file(out_file_header)

    # Read Data Files and drop the fist line (it contains headers)

    bdc_items = bdc_data[1:]
    sm_items = sm_data[1:]

    # Data package definition

    data = {
        'bdc_items' : bdc_items,
        'sm_items' : sm_items,
        'bdc_header' : bdc_header,
        'sm_header' : sm_header,
        'search_area' : search_area,
        'output_file' : out_file
    }

   # Run Iterator
   
    start_time = Timer()

    processes = tqdm([Process(target=find_close_points, args=(data, bdc_item)) for bdc_item in bdc_items])
   
    for process in processes:
        process.start()
    for process in tqdm(processes):
        process.join()

    print(sm_header)
 
    # Single Processor
    # for bdc_item in tqdm(bdc_items):
    #     find_close_points(data, bdc_item)

    stop_time = Timer()

    total_time = (stop_time - start_time)/60
    
    
    print_with_header(f'Complete! Overall Time: {total_time:.2f} minutes.')


if __name__ == '__main__':

    main()
