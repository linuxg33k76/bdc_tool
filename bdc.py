#! /usr/bin/env python3

'''
BDC Fabric Comparison Tool.
This tool compares the FCC Active BSL fabric csv (file subjected to licensing through CostQuest)
and VertiGIS M4 compiled Services Manager report.

FCC_Active_BSL.csv headers:
"location_id","address_primary","city","state","zip","zip_suffix","unit_count","bsl"location_id","address_primary","city","state","zip","zip_suffix","unit_count","bsl_flag","building_type_code","land_use_code","address_confidence_code","county_geoid","block_geoid","h3_9","latitude","longitude","fcc_rel"_flag","building_type_code","land_use_code","address_confidence_code","county_geoid","block_geoid","h3_9","latitude","longitude"

M4 Services Manager headers:
FullAddress,SID,PID,EXID,Service,Latitude,Longitude,Company,_overlaps

Program Created by Ben Calvert (and ChatGPT3)
Date: 2/4/2023

Apache 2.0 License

'''


import math
import multiprocessing
import os
import pandas as pd
# from timeit import default_timer as Timer
from datetime import datetime
# from multiprocessing import Process
from multiprocessing import Pool
from tqdm import tqdm
from library import FileHandlerClass as FHC
from library import BDCGuiClass as BGC
from library import ArgsClass as AC

# Class Instances

args = AC.CLIParser().get_args()

# Function Definitions

def verbose_print(text):

    '''
        Checks for verbose mode and if True, prints test for debugging.

        text: string

        return: none
    '''

    if args.verbose is True:
        print(f'---> {text}')


def print_with_header(text):

    '''
        Header template for program to print data in an visually pleasing format.

        text: string

        return: None
    '''

    term_width = FHC.MiscTools().get_terminal_width()

    if term_width > 120:
        columns = 120
    else:
        columns = term_width

    padding = int((columns - len(text))/2)

    print('*'*columns + '\n' + ' '*padding + text + '\n' + '*'*columns + '\n')

def find_closest_point(data_array, max_dist):

    '''
        Sort records to find the closest point

        data_array: array of dictionary data
        max_dist: float

        return: array of 1 value

    '''

    return_val = []

    verbose_print(f'Array size: {len(data_array)}')

    # loop thru the values in the array
    for i in data_array:
        distance = i['distance']
        verbose_print(f'Distance Value: {distance}')
        if distance <= max_dist:
            val_to_return = i['record']
            max_dist = distance
            verbose_print(f'Max Distance: {max_dist}')

    # Format as an arraw for writing - written this way for consistency
    verbose_print(f'String to return: {val_to_return}')
    return_val.append(val_to_return)
    return return_val

def write_record(data, ofile):

    '''
        Appends Data to specified output file

        data: array

        return: None
    '''

    # Iterate through data array and write line(s) 
    for item in data:
        ofile.write_append_to_file(item)


# Created by ChatGPT3 (modified by Ben C.)
def haversine(lat1, lon1, lat2, lon2):

    '''
        Haversine Formula Function - Calculate the distance between two geographic coordinates.
        Original function created by ChatGPT3 and modified to fit ver 1 of this program.

        https://www.geeksforgeeks.org/haversine-formula-to-find-distance-between-two-points-on-a-sphere/

        lat1: string (to be converted to float) - FCC BSL info
        lon1: string (to be converted to float) - FCC BSL info
        lat2: string (to be converted to float) - M4 ServicesManager info
        lon2: string (to be converted to float) - M4 SservicesManager info

        return: distance - Product of the Radius of Earth (in feet) and Haversine Formula
    '''

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

    '''
        Find close points - Iterating Function.
        Function will create a "results" list and pass that to a file write "append" function.

        data: dictionary
        bdc_item: string - single line of the FCC Active BSL data file

        return: None
    '''

    # Unpack data dictionary
    bdc_header = data['bdc_header']
    sm_header = data['sm_header']
    out_file = data['output_file']
    locations = data['sm_items']
    threshold_distance = float(data['search_area'])  # convert to float from string

    # Create an addressible dictionary record using the bdc file header information and the single FCC Active BSL record
    bdc_array = bdc_item.strip('\n').replace('"','').split(',')
    bdc_record = dict(zip(bdc_header, bdc_array))

    # Initialize the results array and start looping through the ServicesManager data
    results = []
    for location in locations:

        # Create an addressible dictionary record using the M4 Services Manager data file and a single M4 Services Manager record
        loc_array = location.strip('\n').replace('"','').split(',')
        loc_record = dict(zip(sm_header, loc_array))

        # Test for NULL values in Latitude and Longitude dictionary items
        if loc_record['Latitude'].upper() != 'NULL' and loc_record['Longitude'].upper() != 'NULL':
            distance = haversine(bdc_record['latitude'], bdc_record['longitude'], loc_record['Latitude'], loc_record['Longitude'])
            if distance <= threshold_distance:
                service = loc_record['Service'].split('_')[0]
                # results.append(bdc_item.strip('\n') + ',' + loc_record['SID'] + ',' + loc_record['FullAddress'] + ',' + service + ',' + loc_record['Latitude'] + ',' + loc_record['Longitude'] + ',' + loc_record['Company'] +',' + str(distance) + ',TRUE\n')
                # Create an array entry with a dict element of distance and string of data to write
                record = bdc_item.strip('\n') + ',' + loc_record['SID'] + ',' + loc_record['FullAddress'] + ',' + service + ',' + loc_record['Latitude'] + ',' + loc_record['Longitude'] + ',' + loc_record['Company'] +',' + str(distance) + ',TRUE\n'
                results.append({'distance' : distance,'record' : record})
    
    # Test to see if we have matches and if so, append those matches to our output file
    if results != []:
        '''
        To Do:  Create an alternate method to find records with the closest distance and write that.
        '''
        data_to_write = find_closest_point(results, threshold_distance)
        verbose_print(f'data to write: {data_to_write}')
        write_record(data_to_write, out_file)

        # return the single record
        return data_to_write[0]

    else:
        # write data w/o a match - single record
        results.append(bdc_item.strip('\n') + ',' + ',' + ',' + ',' + ',' + ',' + ',' ',FALSE\n')
        write_record(results, out_file)

        # return the single record
        return results[0]


def post_process(home_dir, results_file):
    
    # Define Output File
    date_ref = datetime.today().strftime('%d-%b-%Y')
    output_file = f'{home_dir}/bdc_tool/output/Deduped_FCC_Report_{date_ref}.csv'

    # Read Results file csv
    df = pd.read_csv(results_file)

    # Will use FullAddress to find duplicates
    # Will use Distance to locate the closest location match to keep

    # Group by FullAddress and find the minimum distance
    idx = df.groupby(['FullAddress'])['Distance'].idxmin()

    # Create a new dataframe with the minimum distance
    df_min = df.loc[idx]

    # Write the results to a new file
    df_min.to_csv(f'{output_file}', sep=',', encoding='utf-8', index=False)

# End of ChatGPT3 section (modified)

def main():

    # Get User's Home Directory

    home_dir = os.getenv('HOME')
    date_ref = datetime.today().strftime('%d-%b-%Y')

    # Get CPU Count for Processing
    cpus = multiprocessing.cpu_count()
    print_with_header(f'Welcome to the BDC Fabric Comparison Tool.  Your system has: {cpus} CPUs for processing.')

    if args.test is True:

        # (TESTING SECTION)

        print('TESTING MODE is ACTIVE!  Data is simulated!')

        # Simulated Inputs for TESTING PURPOSES
        bdc_csv_file = './SampleData/FCC_Active_BSL.csv'
        sm_csv_file = './SampleData/All_SM.csv'
        out_csv_file = f'{home_dir}/bdc_tool/Data/output/Test_FCC_Report_{date_ref}.csv'
        results_csv_file = f'{home_dir}/bdc_tool/Data/output/Test_FCC_Report_Results_{date_ref}.csv'
        search_area = '5000'

        if args.verbose is True:
            verbose_print(f'User\'s Home Directory: {home_dir}')
            verbose_print(f'BDC File: {bdc_csv_file}')
            verbose_print(f'ServicesManager File: {sm_csv_file}')
            verbose_print(f'Output File: {out_csv_file}')
            verbose_print(f'Results File: {results_csv_file}')
            verbose_print(f'Threshold Distance: {search_area}')

    else:

        if args.cli is True:

    
            # Get user inputs - Data validate
            while True:
                bdc_csv_file = input('Please enter path and filename of BDC_Active_BSL CSV file: ')
                if FHC.MiscTools.file_check(bdc_csv_file) is True:
                    break
            while True:
                sm_csv_file = input('Please enter path and filename of ServicesManager CSV: ')
                if FHC.MiscTools.file_check(sm_csv_file) is True:
                    break
            while True:
                out_csv_file = input('Please enter path and filename of Output CSV file: ')
                if FHC.MiscTools.path_check(out_csv_file) is True:
                    break
            while True:
                search_area = input('What is your search radius in feet? ')
                try:
                    if float(search_area) > 0:
                        break
                except:
                    pass    

        else:

            # Launch GUI (NORMAL OPERATION)
            gui = BGC.BDCGUI()

            # Assign GUI inputs by instance attributes
            bdc_csv_file = gui.fcc_file
            sm_csv_file = gui.sm_file
            out_csv_file = gui.outfile
            search_area = gui.distance

    # Set FHC instances
    bdc_file = FHC.FileHandler(bdc_csv_file)
    sm_file = FHC.FileHandler(sm_csv_file)
    out_file = FHC.FileHandler(out_csv_file)
    results_csv_file = f'{home_dir}/bdc_tool/output/FCC_Report_Results_{date_ref}.csv'
    results_file = FHC.FileHandler(results_csv_file)

    # Get Data
    bdc_header = bdc_file.get_csv_header()
    bdc_data = bdc_file.read_file()
    sm_header = sm_file.get_csv_header()
    sm_data = sm_file.read_file()

    # Set Output Header Data
    services_manager_headers = ',"M4_Structure_ID","FullAddress","Service","SM_LAT","SM_LON","Company","Distance","Match_Flag"\n'
    out_file_header = bdc_data[0].strip('\n') + services_manager_headers
    out_file.write_file(out_file_header)
    results_file.write_file(out_file_header)

    # Read Data Files and drop the fist line (it contains headers)

    bdc_items = bdc_data[1:]
    sm_items = sm_data[1:]

    if args.verbose is True:
        print(f'BDC data sample (first record): {bdc_items[0]}')
        print(f'SM data sample (first record): {sm_items[0]}')

    # Data package definition

    data = {
        'bdc_items' : bdc_items,
        'sm_items' : sm_items,
        'bdc_header' : bdc_header,
        'sm_header' : sm_header,
        'search_area' : search_area,
        'output_file' : out_file
    }

    # Run Iterator - Multiple instances
   
    # Start a timer to get a total run time
    # start_time = Timer()
    start_time = datetime.now()

    if args.test is True:
        # (TESTING SECTION)
        # Single Processor - Testing (uncomment code)
        for bdc_item in tqdm(bdc_items):
            find_close_points(data, bdc_item)

    else:
        # (PARALLEL PROCESSING SECTION)
        # Set progress bar "tqdm" on list of Processes pointing to the find_close_points function. Use FCC Active BSL data.
        
        with Pool() as pool:
            processes = [pool.apply_async(find_close_points, args=(data, bdc_item)) for bdc_item in bdc_items]
            results = [process.get() for process in tqdm(processes)]

        # OLD Parallel Processing Code (pre finding the Pool() class) - kept for reference
        # # Set progress bar "tqdm" on list of Processes pointing to the find_close_points function.  Use FCC Active BSL data.

        # processes = tqdm([Process(target=find_close_points, args=(data, bdc_item)) for bdc_item in bdc_items])
    
        # # Start Processes
        # for process in processes:
        #     process.start()
        # for process in processes:
        #     process.join()
    

    # Write results of the find_close_points function to the results file
    # This is an alternative Write Method - write once instead of multiple times as directed by the find_close_points function
    write_record(results, results_file)
    post_process(home_dir, results_csv_file)


    # End timer
    # stop_time = Timer()
    stop_time = datetime.now()

    total_time = (stop_time - start_time)/60

    # Print out total process time
    print_with_header(f'Complete! Overall Time: {total_time}.')


if __name__ == '__main__':
    main()
