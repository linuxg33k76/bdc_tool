# bdc_tool
FCC BDC Comparison Tool (WGS84)

This tool compares Lat/Lon FCC Fabric compiled repport data to VertiGIS M4 ServicesManager data.
Data files need to be in csv format.

FCC Active BSL Headers:

"location_id","address_primary","city","state","zip","zip_suffix","unit_count","bsl_flag","building_type_code","land_use_code","address_confidence_code","county_geoid","block_geoid","h3_9","latitude","longitude"

  "location_id", \
  "address_primary", \
  "city", \
  "state", \
  "zip", \
  "zip_suffix", \
  "unit_count", \
  "bsl_flag", \
  "building_type_code", \
  "land_use_code", \
  "address_confidence_code", \
  "county_geoid", \
  "block_geoid", \
  "h3_9", \
  "latitude", \
  "longitude" 


M4 ServicesManager Report Headers:
FullAddress,SID,PID,EXID,Service,Latitude,Longitude,Company,_overlaps

  FullAddress, \
  SID, \
  PID, \
  EXID, \
  Service, \
  Latitude, \
  Longitude, \
  Company, \
  \_overlaps 

**Note** FullAddress will need all "," commas removed from the addresses in that column for proper data alignment.

Dependencies:

PySimpleGUI: *pip3 install PySimpleGui*\
TQDM: *pip3 install tqdm*\
Pandas:  *pip3 install pandas*

**Note**  This may require python-tk package to work (Linux or WSL applications).  Mac OS will require brew to be installed and the package python-tk@<Python version> to be installed first!  I have not tested on Windows 10/11 ... yet!

Follow GUI prompts to configure input files, output file, and distance values.

<img width="299" alt="image" src="https://user-images.githubusercontent.com/19679817/219900039-b235bcb0-a50e-4d9f-baeb-eb9dd86cabb5.png">

Progress will be written to the terminal (GUI input was an add-on feature).  Processing can take time, but progress is presented via a progress bar in the CLI.

6/3/2023:  Added command line argument parser:

./bdc.py -h\
usage: bdc.py [-h] [-c] [-v] [-t]\

options:
  -h, --help     show this help message and exit\
  -c, --cli      CLI Interface for Data Input\
  -v, --verbose  Display output traps\
  -t, --test     Turn on test features\

2/25/2024:  Added install and uninstall commands!\

install.py - installs the virtual environment and required packages.\
uninstall.py - removes the virtual environment.

