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

    '''
    "location_id","address_primary","city","state","zip","zip_suffix","unit_count","bsl_flag","building_type_code","land_use_code","address_confidence_code","county_geoid","block_geoid","h3_9","latitude","longitude"
    1054709828,"625 COUNTY ROAD 20","CRAIG","CO","81625","7906",1,"True","B",5,"1","08081","080810003001000","89268055417ffff",40.59506191,-107.46012322
    1054709830,"955 COUNTY ROAD 20 BLDG 4","CRAIG","CO","81625","7906",2,"True","R",1,"3","08081","080810003001000","89268055417ffff",40.59495080,-107.45620683
    1054709832,"969 COUNTY ROAD 20","CRAIG","CO","81625","",1,"True","R",1,"3","08081","080810003001000","892680554abffff",40.59444885,-107.45624083
    1054709834,"947 COUNTY ROAD 20","CRAIG","CO","81625","",1,"True","R",1,"3","08081","080810003001000","89268055417ffff",40.59469887,-107.45644085
    '''


    bdc_csv_filepath = input('Please enter path of BDC_Active_BSL CSV file: ')
    bdc_csv_file = input ('Please provide name of BDC_Active_BSL CSV file: ')

    # Hardcode for testing
    # bdc_csv_filepath = '/home/bcalvert/Data'
    # bdc_csv_file = 'FCC_Active_BSL.csv'

    bdc_file = FHC.FileHandler(bdc_csv_filepath, bdc_csv_file)

    bdc_header = bdc_file.get_csv_header()
    bdc_data = bdc_file.read_file()
    
    # Get VertiGIS M4 ServicesManager data file

    '''
    SID,FullAddress,Service,Company,EXID,Latitude,Longitude,GIS LAT,GIS LON
    34623,1616,NO SM Qualifications,Forsyth,30,,,45.80624,-107.017716
    50750," UNKNOWN , SUNDANCE, WY,  Duplicate 36",1000MB/1000MB_Fiber,Forsyth,78,44.40730106,-104.3689933,44.407114,-104.368767
    3718," WHITE BUFFALO LN BROADUS, MT 59317",10MB/1MB_10000,Forsyth,28,45.43841383,-105.4113181,45.438414,-105.411318
    40194,"?? TONGUE RIVER RD MILES CITY, MT 59301",NO SM Qualifications,Forsyth,34,45.91158928,-106.1319806,45.911589,-106.131981
    '''

    sm_csv_filepath = input('Please enter path and filename of ServicesManager CSV: ')
    sm_csv_file = input ('Please provide name of BDC_Active_BSL CSV file: ')

    # Hardcode for testing
    # sm_csv_filepath = '/home/bcalvert/Data'
    # sm_csv_file = 'Forsyth_SM.csv'

    sm_file = FHC.FileHandler(sm_csv_filepath, sm_csv_file)

    sm_header = sm_file.get_csv_header()
    sm_data = sm_file.read_file()

    # Output File

    out_csv_filepath = input('Please enter path of Output CSV file: ')
    out_csv_file = input ('Please provide name of Output CSV file: ')

    # For testing purposes
    # out_csv_filepath = '/home/bcalvert/Data/output'
    # out_csv_file = 'Forsyth_CSV_Output.csv'

    out_file = FHC.FileHandler(out_csv_filepath, out_csv_file)

    out_file_header = bdc_data[0].strip('\n') + ',"FullAddress","Service","GIS_LAT","GIS_LON","Distance","Match_Flag"\n'
    out_file.write_file(out_file_header)

    # Get user input of radius from Lat/Lon point to find a match

    user_feet = input('What is your search radius in feet? ')

    exception_counter = 0
    match_counter = 0
    
    # Read BDC CSV file point by point (skip the first line which is header info)

    bdc_items = bdc_data[1:]
    for bdc_item in tqdm(bdc_items):
   
        bdc_array = bdc_item.strip('\n').replace('"','').split(',')

        bdc_record = dict(zip(bdc_header, bdc_array))
        
        # print(bdc_record)

        center_point = [{'lat': float(bdc_record['latitude']), 'lng': float(bdc_record['longitude'])}]

        # Loop through SM data to find a point within the range (skip the first line which is header info)

        sm_items = sm_data[1:]
        for sm_item in sm_items:

                sm_array = sm_item.strip('\n').replace('"','').split(',')

                sm_record = dict(zip(sm_header, sm_array))

                # print(sm_record)

                test_point = [{'lat': float(sm_record['GIS LAT']), 'lng': float(sm_record['GIS LON'])}]
                radius = float(user_feet) # in feet

                center_point_tuple = tuple(center_point[0].values())
                test_point_tuple = tuple(test_point[0].values())

                try:
                    dis = distance.great_circle(center_point_tuple, test_point_tuple).feet #WGS 84 Earth Radius
                except:
                    exception_counter =+ 1



                if dis <= radius:
                    # print(f'Distance: {dis:0.2f} ft')
                    # print(f'{test_point_tuple} point is inside the {user_feet} ft radius from {center_point_tuple} coordinate')
                    '''
                    Out File Headers
                    "location_id","address_primary","city","state","zip","zip_suffix","unit_count","bsl_flag","building_type_code","land_use_code","address_confidence_code","county_geoid","block_geoid","h3_9","latitude","longitude","FullAddress","Service","GIS_LAT","GIS_LON","Distance","Match_Flag"
                    '''
                    data_to_write = bdc_item.strip('\n') + ',' + sm_record['FullAddress'] + ',' + sm_record['Service'] + ',' + sm_record['GIS LAT'] + ',' + sm_record['GIS LON'] + ',' + str(dis) + ',TRUE\n'
                    out_file.write_append_to_file(data_to_write)
                    match_counter += 1

                else:
                    # print(f'{test_point_tuple} point is outside the {user_feet} ft radius from {center_point_tuple} coordinate')
                    pass
    
    

    print(f'We had this number of exceptions: {exception_counter}')
    print(f'We had this many matches: {match_counter}')               

if __name__ == '__main__':
    main()
