#-----------------------------------------------------------------------------#

# FILL IN THESE INPUTS BEFORE RUNNING THIS SCRIPT.
# USE THIS EXAMPLE FILE.
# Red 0 Session 1 (2022-02-18) (576x432).csv

# Choose a folder containing the non-filtered tracking data from DeepLabCut.
# This will also be the place that files will be exported.
# It must have '(576x432)' at the end.
import_location = r"C:\Users\hazza\Desktop\DeepLabCut\Codes\All together\Import and export files for codes"

#-----------------------------------------------------------------------------#

import pandas as pd
import os
from glob import glob
from tqdm import tqdm
from random import shuffle

def remove_frames_CPL_below_05(import_location):
    
    print('Remove data where the centre-point likelihood is below 0.05.')
    
    import_paths = os.path.join(import_location, '*(576x432).csv')
    import_paths = glob(import_paths)
    
    for path in tqdm(import_paths, ncols=70):
        
        df = pd.read_csv(path, header=[0,1,2])
        df = df[df[('DLC_resnet50_Catherine_2VDLRFeb23shuffle1_200000',
                    'Centre_point','likelihood')] > 0.05]
        
        export_path = path[:-4] + '_RMD.csv'
        df.to_csv(export_path, index=False)
        
def check_which_DLC_files_empty(import_location):

    print('Create a list of empty tracking data files.')
    
    import_paths = os.path.join(import_location, '*_RMD.csv')
    import_paths = glob(import_paths)
    print(import_paths)
    no_frames = {}
    
    for path in tqdm(import_paths, ncols=70):
        
        df = pd.read_csv(path, header=[0,1,2])
        no_frames[path] = [len(df)]
    
    results = pd.DataFrame(no_frames).T
    results.columns = ['Number of frames in video']
    results.index.name = 'Paths of videos'
    
    export_path = os.path.join(import_location, 'No_frames.csv')
    results.to_csv(export_path)
        
def reset_frame_numbers(import_location):
    
    print('Reset frame numbers in these files.')
    
    import_paths = os.path.join(import_location, '*_RMD.csv')
    import_paths = glob(import_paths)
    
    for path in tqdm(import_paths, ncols=70):
        
        df = pd.read_csv(path, header=[0,1,2])
        
        df.index = range(len(df))
        df[('scorer','bodyparts','coords')] = df.index
        
        export_path = path[:-4] + '_RFN.csv'
        df.to_csv(export_path, index=False)

def combine_csvs_so_importable_in_bsoid(import_location):
    
    print('Combine CSV files together.')
    
    import_paths = os.path.join(import_location, '*_RMD_RFN.csv')
    csv_locations = glob(import_paths)    

    # Randomise the order of csv files.
    shuffle(csv_locations) 
    
    indices1 = list(range(0,len(csv_locations),25))
    indices2 = indices1[1:] + [len(csv_locations)]
    indices  = list(zip(indices1, indices2))
    
    csv_groups = [csv_locations[indices[i][0]:indices[i][1]] for i in range(len(indices))]
    group_nums = []
    for group in indices:
        for i in range(group[1]-group[0]):
            group_nums += [str(group)]
    home = import_location
    
    # Comment this section out if you don't want to export this summary info.
    summary_info  = pd.DataFrame({'Paths':csv_locations, 
                                  'File numbers':list(range(len(csv_locations))),
                                  'Group':group_nums})
    summary_info.to_csv(os.path.join(home,'Combined_files_table.csv'), index=False)
    
    for i in tqdm(range(len(csv_groups)), ncols=70):
        
        # Make a folder.
        folder = os.path.join(home,'Sessions '+str(indices[i]))
        os.mkdir(folder)
        
        list_dfs = []
        for path in csv_groups[i]:
            df = pd.read_csv(path, header=[0,1,2])
            list_dfs.append(df)  
        
        master_df = pd.concat(list_dfs)
        master_df.index = range(len(master_df))
        master_df[('scorer','bodyparts','coords')] = master_df.index
        
        export_path = os.path.join(folder, 'Combined file '+str(indices[i])+'.csv')
        master_df.to_csv(export_path, index=False)
        
if __name__ == "__main__":
    
    remove_frames_CPL_below_05(import_location)
    check_which_DLC_files_empty(import_location)
    reset_frame_numbers(import_location)
    combine_csvs_so_importable_in_bsoid(import_location)
        