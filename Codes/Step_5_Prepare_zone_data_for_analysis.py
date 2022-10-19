#-----------------------------------------------------------------------------#

# FILL IN THESE INPUTS BEFORE RUNNING THIS SCRIPT.
# USE THESE EXAMPLE FILES:
# Red 0 Session 1 (2022-02-18) (576x432)_MW5.csv
# Zone coordinates.csv

# Choose a folder containing the filtered tracking data from DeepLabCut.
# This will also be the place that files will be exported.
# It must have '_MW5' at the end, which means a median filter with a window
# duration of 5 frames has been applied.
import_location = r"C:\Users\hazza\Desktop\DeepLabCut\Codes\All together\Import and export files for codes"

#-----------------------------------------------------------------------------#

import pandas as pd
import os
from glob import glob
from tqdm import tqdm
import numpy as np

def modify_frames_CPL_below_05(import_location):
    
    print('Make the data where the centre-point likelihood is below 0.05 blank')
    
    import_paths = os.path.join(import_location, '*_MW5.csv')
    import_paths = glob(import_paths)
    
    for path in tqdm(import_paths, ncols=70):
        
        df = pd.read_csv(path, header=[0,1,2])
        
        missing_data = df.index[df[('DLC_resnet50_Catherine_2VDLRFeb23shuffle1_200000',
                                    'Centre_point','likelihood')] <= 0.05]
        columns_to_wipe = df.columns[1:] # Exclude the column with the frame numbers.
        df.loc[missing_data, columns_to_wipe] = np.nan
        
        export_path = path[:-4] + '_EMD.csv'
        df.to_csv(export_path, index=False)
        
def add_zone_data_DLC_excel_files(import_location):
    
    print('Add the zone vertices to the csv files.')
    
    import_paths = os.path.join(import_location, '*_EMD.csv')
    import_paths = glob(import_paths)
    import_zone_coordinates = os.path.join(import_location, 'Zones coordinates.csv')
    
    zone_info = pd.read_csv(import_zone_coordinates, index_col=0, header=[0,1,2])
    
    for path in tqdm(import_paths, ncols=70):
        
        video = os.path.basename(path)
        video = video[:-12]
        video = video.split(' ')
        video = [video[0]] + video[4:]
        video = ' '.join(video)
        
        df = pd.read_csv(path, header=[0,1,2])
        
        column_names = zone_info.columns
        video_coords = zone_info.loc[video].tolist()
        zone_values  = [video_coords for i in range(len(df))]
        zone_dataframe = pd.DataFrame(zone_values, columns=column_names)
        
        df_with_zones = pd.concat([df, zone_dataframe], axis=1)
        
        export_path = path[:-4] + '_AZ.csv'
        df_with_zones.to_csv(export_path, index=False)
        
def create_ordered_list_zone_vertices(import_location): 
    
    print('Create an ordered list of vertices.')

    import_paths = os.path.join(import_location, '*_EMD_AZ.csv')  
    import_paths = glob(import_paths)
    
    def add_corner(corner_name, csv_file):
        if np.isnan(csv_file.at[0,('DLC_resnet50_Catherine_2VDLRFeb23shuffle1_200000',
                                   corner_name, 'x')]) == True:
            return([])
        else:
            return([corner_name])
    # Define the number of rows in the longest column, so other columns can be
    # filled with nans.
    no_rows = 8
    
    for path in tqdm(import_paths, ncols=70):
        
        csv_file = pd.read_csv(path, header=[0,1,2])
        
        zones = {}
        zones['pellet_dispenser'] = ["Pellet_TL","Pellet_TR","Pellet_BR","Pellet_BL"]
        zones['left_image']       = ["ImageL_TL","ImageL_TR","ImageL_BR","ImageL_BL"]
        zones['right_image']      = ["ImageR_TL","ImageR_TR","ImageR_BR","ImageR_BL"]
        zones['escape_hole']      = ["Hole_top","Hole_TR","Hole_right","Hole_RB","Hole_bottom","Hole_BL","Hole_left","Hole_LT"]
        zones['floor']            = ["PEwall_bottom","ETwall_bottom","TBwall_bottom","BPwall_bottom"]
        zones['pellet_wall']      = ["BPwall_bottom","BPwall_top","PEwall_top","PEwall_bottom"]
        zones['arena']            = ["TL","TR","BR","BL"]
        
        zones['escape_wall']      = (["PEwall_bottom","PEwall_top"] + 
                                     add_corner("Ewall_cornerL",csv_file) +
                                     add_corner("Ewall_cornerR",csv_file) +
                                     ["ETwall_top","ETwall_bottom"])
        
        zones['test_wall']        = (["ETwall_bottom","ETwall_top"] + 
                                     add_corner("Twall_cornerL",csv_file) +
                                     add_corner("Twall_cornerR",csv_file) +
                                     ["TBwall_top","TBwall_bottom"])
        
        zones['blank_wall']       = (["TBwall_bottom","TBwall_top"] + 
                                     add_corner("Bwall_cornerL",csv_file) +
                                     add_corner("Bwall_cornerR",csv_file) +
                                     ["BPwall_top","BPwall_bottom"])
        
        # Make all lists the same length by filling them with nans.
        for key in zones.keys():
            num_nans_to_add = no_rows - len(zones[key])
            zones[key] = zones[key] + num_nans_to_add*[np.nan]
            
        zones = pd.DataFrame(zones)
        
        export_path = path[:-25]+'_Zones.csv'
        zones.to_csv(export_path, index=False)

def create_list_paths_for_zone_analysis(import_location):
    
    print('Create a list of paths for zone analysis.')
    
    paths = {}
    
    paths['Zone data']         = glob(os.path.join(import_location, '*_EMD_AZ.csv'))
    paths['Order of vertices'] = glob(os.path.join(import_location, '*_Zones.csv'))
    paths['Images of zones']   = [path[:-4]+'.png' for path in paths['Zone data']]
    paths['File names']        = [os.path.basename(path)[:-25] for path in paths['Zone data']]      

    df = pd.DataFrame(paths)
    export_path = os.path.join(import_location, 'List paths for zone analysis.csv')
    df.to_csv(export_path, index=False)
    
if __name__ == "__main__":
    
    modify_frames_CPL_below_05(import_location)
    add_zone_data_DLC_excel_files(import_location)
    create_ordered_list_zone_vertices(import_location)
    create_list_paths_for_zone_analysis(import_location)
        