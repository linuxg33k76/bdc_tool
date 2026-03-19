#! /usr/bin/env python3

'''
BDC Fabric Comparison Tool.
This tool compares the FCC Active BSL fabric csv (file subjected to licensing through CostQuest)
and VertiGIS M4 compiled Services Manager report.

FCC_Active_BSL.csv headers:
"location_id","address_primary","city","state","zip","zip_suffix","unit_count","bsl_flag","building_type_code","land_use_code","address_confidence_code","county_geoid","block_geoid","h3_9","latitude","longitude"

Target Data headers (e.g. HUBB):
'Fund name', 'SAC*', 'Latitude*', 'Longitude*', 'Date of Deployment*', 'Download/Upload Speed Tier*', 'Address*', 'City*', 'State*', 'Zip Code*', '# of Units*', 'Carrier Location ID', 'Technology', 'Other Technology', 'Latency', 'HUBB Location ID'
Program Created by Ben Calvert (and ChatGPT3 & Gemini 3.1 Pro)
Date: 2/4/2023
Refactored: 12/15/2025
Updated: 3/19/2026

Apache 2.0 License
'''

import csv
import logging
import math
import multiprocessing
import os
from functools import partial
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path
from typing import Dict, List, Optional, Any

import pandas as pd
from tqdm import tqdm

from library import FileHandlerClass as FHC
from library import BDCGuiClass as BGC
from library import ArgsClass as AC

# Configuration
EARTH_RADIUS_FEET = 20_902_766

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Class Instances
args = AC.CLIParser().get_args()
if args.verbose:
    logger.setLevel(logging.DEBUG)

# Function Definitions

def print_with_header(text: str) -> None:
    '''
    Header template for program to print data in a visually pleasing format.
    '''
    term_width = FHC.MiscTools().get_terminal_width()
    columns = min(term_width, 120)
    padding = int((columns - len(text)) / 2)
    print('\n' + '*' * columns + '\n' + ' ' * padding + text + '\n' + '*' * columns + '\n')


def find_closest_point(data_array: List[Dict[str, Any]], max_dist: float) -> Optional[str]:
    '''
    Sort records to find the closest point.
    '''
    val_to_return = None
    current_min_dist = max_dist

    logger.debug(f'Array size: {len(data_array)}')

    for item in data_array:
        distance = item['distance']
        logger.debug(f'Distance Value: {distance}')
        # We want the smallest distance that is still within the max_dist (which is already filtered, but good to check)
        if distance <= current_min_dist:
            val_to_return = item['record']
            current_min_dist = distance
            logger.debug(f'New Max Distance (Closer Found): {current_min_dist}')

    logger.debug(f'String to return: {val_to_return}')
    
    if val_to_return is None:
        # Should technically not happen if data_array is populated correctly based on threshold
        return None
        
    return val_to_return


def write_record(data: List[str], ofile: Any) -> None:
    '''
    Appends Data to specified output file.
    '''
    for item in data:
        ofile.write_append_to_file(item)


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    '''
    Haversine Formula Function - Calculate the distance between two geographic coordinates.
    '''
    try:
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2) + (math.cos(math.radians(lat1)) *
             math.cos(math.radians(lat2)) * (math.sin(dlon / 2) ** 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return EARTH_RADIUS_FEET * c
    except Exception as e:
        logger.error(f"Error calculating haversine distance: {e}")
        return float('inf')


def parse_csv_line(line: str) -> List[str]:
    '''
    Robustly parse a CSV line using the csv module to handle quotes and commas.
    '''
    try:
        # csv.reader expects an iterable of strings, so we pass [line]
        # next() gets the first (and only) row parsed
        return next(csv.reader([line.strip()]))
    except Exception:
        # Fallback to simple split if csv parsing fails
        return line.strip().replace('"', '').split(',')


def find_close_points(data: Dict[str, Any], bdc_item: str) -> str:
    '''
    Find close points - Iterating Function.
    Returns the formatted string to be written to the file.
    '''
    # Unpack data dictionary
    bdc_header = data['bdc_header']
    hubb_header = data['hubb_header']
    locations = data['hubb_items']
    threshold_distance = float(data['search_area'])

    # Create an addressible dictionary record using the bdc file header information
    bdc_array = parse_csv_line(bdc_item)
    
    # Safety check for malformed lines
    if len(bdc_array) != len(bdc_header):
        logger.warning(f"Skipping malformed BDC line: {bdc_item}")
        return f'{bdc_item.strip()},,,,,,,,FALSE\n'

    bdc_record = dict(zip(bdc_header, bdc_array))

    try:
        lat1 = float(bdc_record['latitude'])
        lon1 = float(bdc_record['longitude'])
    except (ValueError, KeyError):
        return f'{bdc_item.strip()},,,,,,,,FALSE\n'

    # Initialize the results array
    matches = []
    
    for location in locations:
        loc_array = parse_csv_line(location)
        if len(loc_array) != len(hubb_header):
            continue
            
        loc_record = dict(zip(hubb_header, loc_array))

        # Test for NULL values
        if (loc_record.get('Latitude*', '').upper() != 'NULL' and 
            loc_record.get('Longitude*', '').upper() != 'NULL'):
            
            try:
                lat2 = float(loc_record['Latitude*'])
                lon2 = float(loc_record['Longitude*'])
                
                distance = haversine(lat1, lon1, lat2, lon2)
                
                if distance <= threshold_distance:
                    # Create the result string matching the new output headers

                    record = (f"{bdc_item.strip()},"
                              f"{loc_record.get('Fund name', '')},"
                              f"{loc_record.get('SAC*', '')},"
                              f"{loc_record.get('Latitude*', '')},"
                              f"{loc_record.get('Longitude*', '')},"
                              f"{loc_record.get('Date of Deployment*', '')},"
                              f"{loc_record.get('Download/Upload Speed Tier*', '')},"
                              f"{loc_record.get('Address*', '')},"
                              f"{loc_record.get('City*', '')},"
                              f"{loc_record.get('State*', '')},"
                              f"{loc_record.get('Zip Code*', '')},"
                              f"{loc_record.get('# of Units*', '')},"
                              f"{loc_record.get('Carrier Location ID', '')},"
                              f"{loc_record.get('Technology', '')},"
                              f"{loc_record.get('Other Technology', '')},"
                              f"{loc_record.get('Latency', '')},"
                              f"{loc_record.get('HUBB Location ID', '')},"
                              f"{distance},"
                              f"TRUE\n")
                              
                    matches.append({'distance': distance, 'record': record})
            
            except ValueError:
                continue
    
    # Find the closest record to the BDC location
    if matches:
        closest_record = find_closest_point(matches, threshold_distance)
        if closest_record:
            return closest_record

    # Default return if no match found
    return f'{bdc_item.strip()},,,,,,,,,,,,,,,,,,FALSE\n'


def post_process(home_dir: str, results_file: str) -> None:
    '''
    Post-process the results file to remove duplicate records.
    '''
    # date_ref = datetime.today().strftime('%d-%b-%Y')
    # output_dir = Path(home_dir) / 'bdc_tool' / 'output'
    output_file = f'{results_file.filename.replace(".csv", "")}_deduped.csv'
    print(f'Output File: {output_file}')
    
    try:
        # Read Results file csv
        df = pd.read_csv(results_file.filename, low_memory=False)

        # Strip literal quotes and leading/trailing whitespace from column names to prevent KeyErrors
        df.columns = df.columns.str.strip(' "')

        if df.empty:
            print_with_header("No results to post-process.")
            return

        # Group by FullAddress and find the minimum distance
        # We need to make sure 'Distance' is numeric
        if 'Distance' in df.columns:
            # Handle cases where Distance might be empty/non-numeric due to FALSE matches
            df['Distance'] = pd.to_numeric(df['Distance'], errors='coerce')
            
            # Filter solely for matches where Distance is present to find best match? 
            # Group by HUBB_ID to get the closest BDC record for each target location
            # print(df.columns)

            idx = df.groupby(['HUBB Location ID'])['Distance'].idxmin()
            df_min = df.loc[idx]
        else:
             df_min = df

        # Write the results to a new file
        df_min.to_csv(output_file, sep=',', encoding='utf-8', index=False)

        print_with_header(f'Output File: {output_file}\nNumber of unique records with a match: {len(df_min)}')

        # Find the median distance
        median_distance = df_min['Distance'].median()
        print_with_header(f'Median Distance: {median_distance} (middle value)')

        # Find the mean distance
        mean_distance = df_min['Distance'].mean()
        print_with_header(f'Mean Distance: {mean_distance} (average distance)')

        # Find the mode distance
        mode_distance = df_min['Distance'].mode()
        print_with_header(f'Mode Distance: {mode_distance} (most common distance)')

        # Pivot table of the data by HUBB Location ID and Download/Upload Speed Tier*
        # if 'Download/Upload Speed Tier*' in df_min.columns and 'HUBB Location ID' in df_min.columns:
     
            # df_pivot_carrier = df_min.pivot_table(index=['Download/Upload Speed Tier*'], columns=['HUBB Location ID'], aggfunc='size', fill_value=0)

            # print_with_header(f'Pivot Table of the data by HUBB Location ID and Download/Upload Speed Tier*:\n\n{df_pivot_carrier}\n')

        # Summary of counts of each Download/Upload Speed Tier*
        df_counts = df_min['Download/Upload Speed Tier*'].value_counts().sort_index()
        print_with_header(f'Summary of counts of each Download/Upload Speed Tier*:\n\n{df_counts}\n')

    except Exception as e:
        logger.error(f"Error in post-processing: {e}")


def main():
    '''
    Main function to run the BDC Tool.
    '''
    # Get User's Home Directory
    home_dir = os.getenv('HOME')
    if not home_dir:
        home_dir = str(Path.home())
        
    date_ref = datetime.today().strftime('%d-%b-%Y')

    cpus = multiprocessing.cpu_count()
    print_with_header(f'Welcome to the BDC Fabric Comparison Tool.  Your system has: {cpus} CPUs for processing.')

    # Default file paths
    bdc_csv_file = ''
    hubb_csv_file = ''
    out_csv_file = ''
    search_area = '500'

    if args.test is True:
        print('TESTING MODE is ACTIVE!  Data is simulated!')
        bdc_csv_file = './SampleData/FCC_Active_BSL.csv'
        hubb_csv_file = './SampleData/All_SM.csv'
        out_csv_file = str(Path(home_dir) / 'bdc_tool' / 'Data' / 'output' / f'Test_FCC_Report_{date_ref}.csv')
        results_file = str(Path(home_dir) / 'bdc_tool' / 'Data' / 'output' / f'Test_FCC_Report_Results_{date_ref}.csv')
        
        if args.verbose:
            logger.debug(f'User\'s Home Directory: {home_dir}')

    else:
        if args.cli is True:
            while True:
                bdc_csv_file = input('Please enter path and filename of BDC_Active_BSL CSV file: ')
                if FHC.MiscTools.file_check(bdc_csv_file) is True:
                    break
            while True:
                hubb_csv_file = input('Please enter path and filename of ServicesManager CSV: ')
                if FHC.MiscTools.file_check(hubb_csv_file) is True:
                    break
            while True:
                out_csv_file = input('Please enter path and filename of Output CSV file: ')
                if FHC.MiscTools.path_check(out_csv_file) is True:
                    break
            while True:
                val = input('What is your search radius in feet? ')
                try:
                    if float(val) > 0:
                        search_area = val
                        break
                except ValueError:
                    pass    
        else:
            # Launch GUI
            gui = BGC.BDCGUI()
            bdc_csv_file = gui.fcc_file
            hubb_csv_file = gui.hubb_file
            out_csv_file = gui.outfile
            search_area = gui.distance

    # Prepare output paths
    output_dir_path = Path(home_dir) / 'bdc_tool' / 'output'
    output_dir_path.mkdir(parents=True, exist_ok=True)
    results_file = str(output_dir_path / f'{out_csv_file}')

    # Initialize File Handlers
    bdc_file = FHC.FileHandler(bdc_csv_file)
    hubb_file = FHC.FileHandler(hubb_csv_file)
    results_file = FHC.FileHandler(results_file)

    # Test
    # Post Processing
    # print(results_file.filename)
    # post_process(home_dir, results_file)
    # exit()

    # Read Data
    bdc_header = bdc_file.get_csv_header()
    bdc_data = bdc_file.read_file()
    hubb_header = hubb_file.get_csv_header()
    hubb_data = hubb_file.read_file()

    # Drop headers from data
    bdc_items = bdc_data[1:]
    hubb_items = hubb_data[1:]

    # Write Headers
    hubb_report_headers = ',"Fund name", "SAC*", "Latitude*", "Longitude*", "Date of Deployment*", "Download/Upload Speed Tier*", "Address*", "City*", "State*", "Zip Code*", "# of Units*", "Carrier Location ID", "Technology", "Other Technology", "Latency", "HUBB Location ID","Distance","Match_Flag"\n'

    out_file_header = bdc_data[0].strip('\n') + hubb_report_headers
    results_file.write_file(out_file_header)

    if args.verbose:
        logger.debug(f'BDC data sample (first record): {bdc_items[0] if bdc_items else "Empty"}')
        logger.debug(f'SM data sample (first record): {hubb_items[0] if hubb_items else "Empty"}')

    # Data package for workers
    # NOTE: NOT passing file handlers to workers prevents pickling errors and race conditions
    data = {
        'bdc_header': bdc_header,
        'hubb_header': hubb_header,
        'hubb_items': hubb_items,
        'search_area': search_area,
    }

    start_time = datetime.now()
    print_with_header(f'\nSearch Area: {search_area} feet\n')

    # Processing Loop
    try:
        if args.test is True:
            # Single Process for Test
            results = []
            for bdc_item in tqdm(bdc_items):
                result = find_close_points(data, bdc_item)
                results.append(result)
            
            # Write all results
            write_record(results, results_file)
        
        else:
            # Parallel Processing
            # Use imap_unordered for better memory efficiency and streaming results
            with Pool() as pool:
                # Create a generator of results
                # Use partial to bind the data argument, making it picklable (unlike lambda)
                process_func = partial(find_close_points, data)
                result_iterator = pool.imap_unordered(
                    process_func,
                    bdc_items,
                    chunksize=10 # Tune chunksize for performance
                )
                
                # Write results as they come in to avoid holding everything in memory
                # Note: FHC write_append_to_file writes a single line/item
                for result in tqdm(result_iterator, total=len(bdc_items)):
                     results_file.write_append_to_file(result)

    except KeyboardInterrupt:
        print("\nProcessing interrupted by user.")
        return
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return

    # Post Processing
    post_process(home_dir, results_file)

    stop_time = datetime.now()
    total_time = (stop_time - start_time).total_seconds() / 60

    print_with_header(f'Complete! Overall Time: {total_time:.2f} minutes.')


if __name__ == '__main__':
    # Added freeze_support for Windows compatibility, though user is on Mac it's good practice
    multiprocessing.freeze_support()
    main()
