#! /usr/bin/env python3

import os
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


def main():

    print_with_header('Welcome to the BDC Fabric Comparison Tool')

    # Get Processed File from BDC Fabric/ShapeFile compare

    # bdc_csv_filepath = input('Please enter path of BDC_Active_BSL CSV file: ')
    # bdc_csv_file = input ('Please provide name of BDC_Active_BSL CSV file: ')

    # Hardcode for testing
    bdc_csv_filepath = '/home/bcalvert/Data'
    bdc_csv_file = 'FCC_Active_BSL.csv'

    bdc_file = FHC.FileHandler(bdc_csv_filepath, bdc_csv_file)

    bdc_headers = bdc_file.get_csv_headers()
    bdc_data = bdc_file.read_file()
    
    # Get VertiGIS M4 ServicesManager data file

    # sm_csv_filepath = input('Please enter path and filename of ServicesManager CSV: ')
    # sm_csv_file = input ('Please provide name of BDC_Active_BSL CSV file: ')

    # Hardcode for testing
    sm_csv_filepath = '/home/bcalvert/Data'
    sm_csv_file = 'Dubois_SM.csv'

    sm_file = FHC.FileHandler(sm_csv_filepath, sm_csv_file)

    sm_headers = sm_file.get_csv_headers()
    sm_data = sm_file.read_file()


    # Get user input of radius from Lat/Lon point to find a match

    user_feet = input('What is your search radius in feet? ')

    exception_counter = 0

    # Read BDC CSV file point by point

    bdc_items = bdc_data[1:]
    for bdc_item in tqdm(bdc_items):

   
        bdc_array = bdc_item.strip('\n').replace('"','').split(',')

        bdc_record = dict(zip(bdc_headers, bdc_array))
        
        # print(bdc_record)

        center_point = [{'lat': bdc_record['latitude'], 'lng': bdc_record['longitude']}]

        # Loop through SM data to find a point within the range

        sm_items = sm_data[1:]
        for sm_item in sm_items:

                sm_array = sm_item.strip('\n').replace('"','').split(',')

                sm_record = dict(zip(sm_headers, sm_array))

                # print(sm_record)

                test_point = [{'lat': sm_record['GIS LAT'], 'lng': sm_record['GIS LON']}]
                radius = float(user_feet) # in feet

                center_point_tuple = tuple(center_point[0].values())
                test_point_tuple = tuple(test_point[0].values())

                try:
                    dis = distance.great_circle(center_point_tuple, test_point_tuple).feet #WGS 84 Earth Radius
                except:
                    exception_counter =+ 1



                if dis <= radius:
                    print(f'Distance: {dis:0.2f} ft')
                    print(f'{test_point_tuple} point is inside the {user_feet} ft radius from {center_point_tuple} coordinate')

                else:
                    # print(f'{test_point_tuple} point is outside the {user_feet} ft radius from {center_point_tuple} coordinate')
                    pass

    print(f'We had this number of exceptions: {exception_counter}')               

if __name__ == '__main__':
    main()
