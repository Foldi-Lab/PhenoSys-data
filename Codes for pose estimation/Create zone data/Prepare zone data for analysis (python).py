import pandas as pd
import os
from glob import glob
from tqdm import tqdm
import numpy as np

def modify_frames_CPL_below_05(locaiton):
    
    # location = '//storage.erc.monash.edu.au/shares/DeepLabCut-rodent-vid/Catherine PhenoSys/*/*/Cut videos/*MW5.csv'
    paths = glob(location)
    
    for path in tqdm(paths, ncols=70):
        
        df = pd.read_csv(path, header=[0,1,2])
        
        missing_data = df.index[df[('DLC_resnet50_Catherine_2VDLRFeb23shuffle1_200000',
                                    'Centre_point','likelihood')] <= 0.05]
        columns_to_wipe = df.columns[1:] # Exclude the column with the frame numbers.
        df.loc[missing_data, columns_to_wipe] = np.nan
        df.to_csv(os.path.dirname(path) + "\\" +
                  os.path.basename(path)[:-4] + '_EMD.csv', index=False)
        
def add_zone_data_DLC_excel_files(DLC_paths, zone_coordinates_path):
    
    # DLC_paths = '//storage.erc.monash.edu.au/shares/DeepLabCut-rodent-vid/Catherine PhenoSys/*/*/Cut videos/*_EMD2M.csv'
    # zone_location = r"C:\Users\DLC\Desktop\Coordinates for drawing zone polygons.csv"
    
    paths = glob(zone_coordinates_path)
    
    remaining_files = [(path, path[:-4]+'_AZ.csv') for path in paths]
    remaining_files = [tuple1[0] for tuple1 in remaining_files if os.path.isfile(tuple1[1])==False]
    
    zone_info = pd.read_csv(zone_coordinates_path, index_col=0, header=[0,1,2])
    
    for path in tqdm(remaining_files, ncols=70):
        
        video = os.path.basename(path)
        video = video[:-14]
        video = video.split(' ')
        video = [video[0]] + video[4:]
        video = ' '.join(video)
        
        df = pd.read_csv(path, header=[0,1,2])
        
        column_names = zone_info.columns
        video_coords = zone_info.loc[video].tolist()
        zone_values  = [video_coords for i in range(len(df))]
        zone_dataframe = pd.DataFrame(zone_values, columns=column_names)
        
        df_with_zones = pd.concat([df, zone_dataframe], axis=1)
        
        export_name = path[:-4] + '_AZ.csv'
        df_with_zones.to_csv(export_name, index=False)
        
def create_ordered_list_zone_vertices(paths): 

    #paths = '//storage.erc.monash.edu.au/shares/DeepLabCut-rodent-vid/Catherine PhenoSys/*/*/Cut videos/*_AZ.csv'
    paths = glob(paths)
    
    def add_corner(corner_name, csv_file):
        if np.isnan(csv_file.at[0,('DLC_resnet50_Catherine_2VDLRFeb23shuffle1_200000',
                                   corner_name, 'x')]) == True:
            return([])
        else:
            return([corner_name])
    # Define the number of rows in the longest column, so other columns can be
    # filled with nans.
    no_rows = 8
    
    for path in tqdm(paths, ncols=70):
        
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
        zones.to_csv(path[:-20]+'_Zones.csv', index=False)
        