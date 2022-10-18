import pandas as pd
import os
from glob import glob
from tqdm import tqdm
from random import shuffle

def remove_frames_CPL_below_05(location):
    
    # location = '//storage.erc.monash.edu.au/shares/DeepLabCut-rodent-vid/Catherine PhenoSys/*/*/Cut videos/*DLC_resnet50_Catherine_2VDLRFeb23shuffle1_200000.csv'
    paths = glob(location)
    
    for path in tqdm(paths, ncols=70):
        
        df = pd.read_csv(path, header=[0,1,2])
        df = df[df[('DLC_resnet50_Catherine_2VDLRFeb23shuffle1_200000',
                    'Centre_point','likelihood')] > 0.05]
        df.to_csv(os.path.dirname(path) + "\\" +
                  os.path.basename(path)[:-4] + '_RMD.csv', index=False)
        
def check_which_DLC_files_empty(location)

    # location = '//storage.erc.monash.edu.au/shares/DeepLabCut-rodent-vid/Catherine PhenoSys/*/*/Cut videos/*RMD.csv'
    paths = glob(location)
    no_frames = {}
    
    for path in tqdm(paths, ncols=70):
        
        df = pd.read_csv(path, header=[0,1,2])
        no_frames[path] = [len(df)]
    
    results = pd.DataFrame(no_frames).T
    results.columns = ['Number of frames in video']
    results.index.name = 'Paths of videos'
    results.to_csv('C:/Users/DLC/Desktop/No_frames.csv')
        
def reset_frame_numbers(home, dest):
    
    # home  = '//storage.erc.monash.edu.au/shares/DeepLabCut-rodent-vid/Catherine PhenoSys/B-SOiD/B-SOiD ordered videos 3/All data'
    # dest  = '//storage.erc.monash.edu.au/shares/DeepLabCut-rodent-vid/Catherine PhenoSys/B-SOiD/B-SOiD ordered videos 3/All data 2'
    files = os.listdir(home)
    paths = [os.path.join(home, file) for file in files]
    
    for path in tqdm(paths, ncols=70):
        
        df = pd.read_csv(path, header=[0,1,2])
        
        df.index = range(len(df))
        df[('scorer','bodyparts','coords')] = df.index
        df.to_csv(os.path.join(dest, os.path.basename(path)), index=False)

def combine_csvs_so_importable_in_bsoid(csv_locations):
    
    # csv_locations = '//storage.erc.monash.edu.au/shares/DeepLabCut-rodent-vid/Catherine PhenoSys/*/*/Cut videos/*)_RMD.csv'
    csv_locations = glob(csv_locations)
    # Randomise the order of csv files.
    shuffle(csv_locations) 
    print(len(csv_locations))
    
    indices1 = list(range(0,len(csv_locations),25))
    indices2 = indices1[1:] + [len(csv_locations)]
    indices  = list(zip(indices1, indices2))
    
    csv_groups = [csv_locations[indices[i][0]:indices[i][1]] for i in range(len(indices))]
    group_nums = []
    for group in indices:
        for i in range(group[1]-group[0]):
            group_nums += [str(group)]
    home = '//storage.erc.monash.edu.au/shares/DeepLabCut-rodent-vid/Catherine PhenoSys/B-SOiD/B-SOiD ordered videos 3'
    
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
        