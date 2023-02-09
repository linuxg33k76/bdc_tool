#! /usr/bin/env python3

'''

!!!DEPRECATED!!!

Note:  This version kept for reference of the evolution of this program.

BDC Fabric Comparison Tool. (Using geopy)
This tool compares the FCC Active BSL fabric csv (file subjected to licensing through CostQuest)
and VertiGIS M4 compiled Services Manager report.

FCC_Active_BSL.csv headers:
"location_id","address_primary","city","state","zip","zip_suffix","unit_count","bsl_flag","building_type_code","land_use_code","address_confidence_code","county_geoid","block_geoid","h3_9","latitude","longitude"

M4 Services Manager headers:
FullAddress,SID,PID,EXID,Service,Latitude,Longitude,Company,_overlaps

Program Created by Ben Calvert
Date: 2/4/2023

Apache 2.0 License

'''


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


def iterate_loop(bdc_item, data):

    
    # bdc_items = data['bdc_items']
    sm_items = data['sm_items']
    bdc_header = data['bdc_header']
    sm_header = data['sm_header']
    search_area = data['search_area']
    out_file = data['output_file']

    match_counter = 0

    bdc_array = bdc_item.strip('\n').replace('"','').split(',')

    bdc_record = dict(zip(bdc_header, bdc_array))
    
    # print(bdc_record)

    center_point = [{'lat': float(bdc_record['latitude']), 'lng': float(bdc_record['longitude'])}]

    # Loop through SM data to find a point within the range (skip the first line which is header info)

    for sm_item in sm_items:

            sm_array = sm_item.strip('\n').replace('"','').split(',')

            sm_record = dict(zip(sm_header, sm_array))

            test_point = [{'lat': float(sm_record['GIS LAT']), 'lng': float(sm_record['GIS LON'])}]
            radius = float(search_area) # in feet

            dis = test_for_match(center_point, test_point)

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
                pass

    return (bdc_item, match_counter)

def test_for_match(center_point, test_point):

    center_point_tuple = tuple(center_point[0].values())
    test_point_tuple = tuple(test_point[0].values())

    try:
        dis = distance.great_circle(center_point_tuple, test_point_tuple).feet #WGS 84 Earth Radius
    except:
        # exception_counter =+ 1
        pass

    return dis

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
    # sm_csv_file = '/home/bcalvert/Data/Dubois_SM.csv'
    # out_csv_file = '/home/bcalvert/Data/output/test.csv'
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
    out_file_header = bdc_data[0].strip('\n') + ',"FullAddress","Service","GIS_LAT","GIS_LON","Distance","Match_Flag"\n'
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

    processes = tqdm([Process(target=iterate_loop, args=(bdc_item, data)) for bdc_item in bdc_items])
   
    for process in processes:
        process.start()
    for process in tqdm(processes):
        process.join()

    stop_time = Timer()

    total_time = (stop_time - start_time)/60
    
    
    print_with_header(f'Complete! Overall Time: {total_time:.2f} minutes.')


if __name__ == '__main__':

    main()
