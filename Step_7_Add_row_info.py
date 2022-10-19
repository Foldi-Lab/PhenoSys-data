#-----------------------------------------------------------------------------#

# FILL IN THESE INPUTS BEFORE RUNNING THIS SCRIPT.
# USE THESE EXAMPLE FILES:
# Zone results.csv
# Row labels.csv

# This the folder that contains the above example files.
import_location = r"C:\Users\hazza\Desktop\DeepLabCut\Codes\All together\Import and export files for codes"
        
#-----------------------------------------------------------------------------#

import pandas as pd
import os

def add_row_info(import_location):
    
    zone_results_path = os.path.join(import_location, 'Zone results.csv')
    row_info_path = os.path.join(import_location, 'Row labels.csv')
    
    zone_results = pd.read_csv(zone_results_path, index_col=0)
    zone_results = zone_results.T
    zone_results.index.name = 'Full name'
    
    row_info = pd.read_csv(row_info_path)
    row_info.index = row_info['Full name']
    shortened_row_info = row_info.loc[zone_results.index]
    
    master = pd.concat([shortened_row_info, zone_results], axis=1)
    export_location = os.path.dirname(zone_results_path)
    export_name     = 'Zones results (with row info).csv'
    export_path     = os.path.join(export_location, export_name)
    master.to_csv(export_path, index=False)

if __name__ == "__main__":
    
    add_row_info(import_location)
    