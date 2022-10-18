import pandas as pd
import numpy as np
import os
from glob import glob
from tqdm import tqdm

def find_time_spent_doing_behaviours(import_location, import_row_info, export_location):
    
    # import_location = r"Y:/Catherine PhenoSys/B-SOiD/B-SOiD ordered videos 3/All data 2/BSOID/Jul-04-2022bout_lengths*"
    # import_row_info = r"C:\Users\hazza\Desktop\DeepLabCut\Codes\DeepLabCut zone and behavioural results\Row labels (no TB).xlsx"
    # export_location = r"C:\Users\hazza\Desktop\PhenoSys_results_330922"
    
    paths = glob(import_location)
    
    # behav_to_num = {'Grooming':[1, 2, 4, 5, 19], 'Rotate body':[25, 28], 'Locomote':[30],
    #                 'Rearing':[29], 'Huddled':[16], 'Investigating':[11, 22, 26, 27, 31, 32, 33],
    #                 'Inactive':[0, 3, 6, 7, 8, 9, 10, 12, 13, 14, 15, 17, 18, 20, 21, 23, 24]}
    behav_to_num = {'Grooming':[1, 2, 4, 5, 19], 'Rotate body':[25, 28], 'Locomote':[30],
                    'Rearing':[29], 'Investigating':[11, 22, 26, 27, 31, 32, 33],
                    'Inactive':[0, 3, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 20, 21, 23, 24]}
    num_to_behav = {}
    for behav in behav_to_num.keys():
        for num in behav_to_num[behav]:
            num_to_behav[num] = behav
    def find_behav(num):
        return(num_to_behav[num])
    
    # Create a master dataframe with all the results for each file in the 'location' folder.
    cols = ['Grooming (total duration in secs)','Inactive (total duration in secs)',	
            'Investigating (total duration in secs)','Locomote (total duration in secs)',
            'Rearing (total duration in secs)',	'Rotate body (total duration in secs)',	
            'Grooming (bout frequency)','Inactive (bout frequency)',	
            'Investigating (bout frequency)','Locomote (bout frequency)',
            'Rearing (bout frequency)',	'Rotate body (bout frequency)']
    master = pd.DataFrame(columns=cols)
    
    for path in tqdm(paths, ncols=70):
        
        # Import the data.
        # This data shows the duration of behavioural bouts, over time in the videos.
        # I will redefine these behaviours using my own grouping in num_to_behav.
        df = pd.read_csv(path)
        df = df.drop(columns=['Unnamed: 0', 'Start time (frames)'])
        df['Behaviour']   = df['B-SOiD labels'].apply(find_behav)
        df['Time (secs)'] = df['Run lengths']*(1/30)
        
        def combine_consecutive(df):
            # Combine the rows with consecutive behaviours.
            # https://stackoverflow.com/questions/63853639/conditionally-merge-consecutive-rows-of-a-pandas-dataframe
            df['Behaviour shifted'] = df['Behaviour'].shift()
            # Create a column with unique values for separate events and identical values
            # for consecutive behaviours.
            df['Consecutive rows'] = (df['Behaviour'] != df['Behaviour shifted']).cumsum()
            # Combine the consecutive rows and sum the time (secs) values together.
            df_filtered = df.groupby(['Behaviour', 'Consecutive rows'], sort=False)['Time (secs)'].agg(sum)
            df_filtered = df_filtered.reset_index().drop(columns=['Consecutive rows'])
            return(df_filtered)
        df_filtered = combine_consecutive(df)
        
        # Forward fill the behavioural bouts that last <= 0.3 secs.
        df_filtered = df_filtered.rename(columns={"Behaviour": "Behaviour without cutoff duration"})
        df_filtered['Behaviour'] = df_filtered['Behaviour without cutoff duration']
        df_filtered.at[(df_filtered['Time (secs)']<=0.3), 'Behaviour'] = np.nan
        df_filtered['Behaviour'] = df_filtered['Behaviour'].fillna(method='ffill')
        df_filtered['Behaviour'] = df_filtered['Behaviour'].fillna(df_filtered['Behaviour without cutoff duration'].iloc[0])
        
        # Recombine the rows, after consecutive behaviours were created again.
        df_cleaned = combine_consecutive(df_filtered)
        
        # Analyse these results.
        df_results = df_cleaned.groupby(['Behaviour']).agg(list)
        df_results['total duration in secs'] = df_results['Time (secs)'].apply(sum)
        #total_duration = sum(df_results['Time (secs)'].apply(sum))
        #df_results['Total duration/total time (%)'] = (df_results['Time (secs)'].apply(sum))*100*(1/total_duration)
        df_results['bout frequency']  = df_results['Time (secs)'].apply(len)
        df_results = df_results.drop(columns=['Time (secs)'])
        
        # Take out only the '[Colour] [Number] Session [Number] ([Date])' from the filename.
        # For example, 'Jul-04-2022bout_lengths_30HzBlack 0 Session 1 (2021-08-13) (576x432)_RMD.csv'
        # becomes 'Black 0 Session 1 (2021-08-13)'.
        # This is the unique identifier for each video.
        filename = os.path.basename(path)
        filename = filename[28:]
        filename = ' '.join(filename.split(' ')[:5])
        
        # Reformat the data.
        df_reformatted = pd.DataFrame(columns=cols)
        for stat in df_results.columns:
            for behav in df_results.index:
                df_reformatted[behav+' ('+stat+')'] = [df_results.at[behav, stat]]
        df_reformatted.index = [filename]
        
        # Append this data to the master dataframe.
        master = pd.concat([master, df_reformatted])
    
    # Add the row info.
    row_info = pd.read_excel(import_row_info)
    row_info.index = row_info['Full name']
    master = master.fillna(0)
    master_export = pd.concat([row_info, master], axis=1)
    
    # Export the master dataframe.
    export_name = 'Video time results.csv'
    export_destination = os.path.join(export_location, export_name)
    master_export.to_csv(export_destination, index=False)

def add_missing_rodent_data_back(behav_folder, behav_files, zones_folder, export_folder):

    # behav_folder = r"Y:\Catherine PhenoSys\B-SOiD\B-SOiD ordered videos 3\All data 2\Frame by frame"
    # behav_files  = r"Y:\Catherine PhenoSys\B-SOiD\B-SOiD ordered videos 3\All data 2\Frame by frame\*"
    # zones_folder = r"Y:\Catherine PhenoSys\B-SOiD\B-SOiD ordered videos 3\All data"
    # export_folder = r"Y:\Catherine PhenoSys\B-SOiD\B-SOiD ordered videos 3\All data 2\Frame by frame (cleaned)"
    
    import_paths = glob(behav_files)
    
    for path in tqdm(import_paths, ncols=70):
        
        # Create a list of behaviours with the corresponding frame numbers.
        df_behav = pd.read_csv(path, skiprows=[1,2], usecols=[1])
        zones_file_path = os.path.join(zones_folder, os.path.basename(path))
        df_zones = pd.read_csv(zones_file_path, skiprows=[1,2], usecols=[0])
        df_zones = df_zones.rename(columns={"scorer": "Frame numbers of behaviours"})
        df_behav = pd.concat([df_behav, df_zones], axis=1)
        df_behav.index = df_behav['Frame numbers of behaviours']
        
        # Create a list of behaviorus with gaps when the rat leaves.
        last_frame = df_behav['Frame numbers of behaviours'].iloc[-1]+1
        df_results = pd.DataFrame({'Frames':list(range(last_frame))})
        df_results = pd.concat([df_results, df_behav['B-SOiD labels']], axis=1)
        
        # Export the results.
        export_path = os.path.join(export_folder, os.path.basename(path))
        df_results.to_csv(export_path, index=False)

def find_time_spent_doing_behaviours_per_time_bin(import_location, import_row_info, export_location):
    
    # import_location = r"Y:\Catherine PhenoSys\B-SOiD\B-SOiD ordered videos 3\All data 2\Frame by frame (cleaned)\*"
    # import_row_info = r"C:\Users\hazza\Desktop\DeepLabCut\Codes\DeepLabCut zone and behavioural results\Row labels.xlsx"
    # export_location = r"C:\Users\hazza\Desktop\PhenoSys_results_330922"
    
    paths = glob(import_location)
    
    # behav_to_num = {'Grooming':[1, 2, 4, 5, 19], 'Rotate body':[25, 28], 'Locomote':[30],
    #                 'Rearing':[29], 'Huddled':[16], 'Investigating':[11, 22, 26, 27, 31, 32, 33],
    #                 'Inactive':[0, 3, 6, 7, 8, 9, 10, 12, 13, 14, 15, 17, 18, 20, 21, 23, 24],
    #                 'Missing': ['Missing']}
    behav_to_num = {'Grooming':[1, 2, 4, 5, 19], 'Rotate body':[25, 28], 'Locomote':[30],
                    'Rearing':[29], 'Investigating':[11, 22, 26, 27, 31, 32, 33],
                    'Inactive':[0, 3, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 20, 21, 23, 24],
                    'Missing': ['Missing']}
    num_to_behav = {}
    for behav in behav_to_num.keys():
        for num in behav_to_num[behav]:
            num_to_behav[num] = behav
    def find_behav(num):
        return(num_to_behav[num])
     
    # Create master dataframes with all the results for each file in the 'location' folder.
    behaviours   = ['Grooming', 'Inactive', 'Investigating', 'Locomote', 'Rearing',
                    'Rotate body', 'Missing']
    # stats_to_use = ['Behaviour time/total time', 'Average bout lengths (secs)', 
    #                 'Total duration (secs)', 'Bout frequency']
    stats_to_use = ['Behaviour time/total time', 'Average bout lengths (secs)']
    headings = []
    for behav in behaviours:
        for i in range(1,31+1):
            headings += [tuple([float(i),behav])]
    master = {}
    for stat in stats_to_use:
        master[stat] = pd.DataFrame(columns=headings)
    
    def combine_consecutive(df):
        # Combine the rows with consecutive behaviours.
        # https://stackoverflow.com/questions/63853639/conditionally-merge-consecutive-rows-of-a-pandas-dataframe
        df['Behaviour shifted'] = df['Behaviour'].shift()
        # Create a column with unique values for separate events and identical values
        # for consecutive behaviours.
        df['Consecutive rows'] = (df['Behaviour'] != df['Behaviour shifted']).cumsum()
        # Combine the consecutive rows and sum the time (secs) values together.
        df_filtered = df.groupby(['Behaviour', 'Consecutive rows'], sort=False)['Frames'].agg(sum)
        df_filtered = df_filtered.reset_index().drop(columns=['Consecutive rows'])
        def find_time(list1):
            return(len(list1)*(1/30))
        df_filtered['Time (secs)'] = df_filtered['Frames'].apply(find_time)
        return(df_filtered)
    def enlist(num):
        return([num])
    def clean_nans(master):
        # Clean the data for missing values.
        # This is very inefficient, but I don't have a better solution yet.
        # nans_to_absent_not_missing_behaviours
        master = master.replace([np.inf, -np.inf], np.nan)
        master.columns = pd.MultiIndex.from_tuples(master.columns)
        master = master[sorted(master.columns)]
        behaviours_no_missing = ['Grooming', 'Inactive', 'Investigating', 'Locomote', 
                                 'Rearing', 'Rotate body']
        
        for i in range(1,31+1):
            i = float(i)
            for filename in master.index:
                if pd.isna(master.loc[filename][i]).sum() in [1,2,3,4,5,6,7]:
                    for behav in behaviours_no_missing:
                        if pd.isna(master.loc[filename,(i,behav)]):
                            master.loc[filename,(i,behav)] = 0
                if (pd.isna(master.loc[filename,(i,'Missing')]) == False and 
                    round(master.loc[filename,(i,'Missing')]) == 60):
                    for behav in behaviours_no_missing:
                        master.loc[filename,(i,behav)] = np.nan
        
        drop_columns = [(float(i),'Missing') for i in range(1,31+1)]
        master = master.drop(columns=drop_columns)
        
        # extend_last_nonnan_values
        for filename in master.index:
            for i in range(31,1-1,-1):
                i = float(i)
                if pd.isna(master.loc[filename][i]).all()==False:
                    non_nan = i
                    break
            for i in range(31,int(i),-1):
                for behav in behaviours_no_missing:
                    master.loc[filename,(i,behav)] = master.loc[filename,(non_nan,behav)]
        return(master)
    
    # For every file in the 'location' folder...
    for path in tqdm(paths, ncols=70):
        
        # Import the data.
        # This data shows the duration of behavioural bouts, over time in the videos.
        # I will redefine these behaviours using my own grouping in num_to_behav.
            
        filename = os.path.basename(path)
        filename = ' '.join(filename.split(' ')[:5])
        df = pd.read_csv(path)
        df['B-SOiD labels'] = df['B-SOiD labels'].fillna('Missing')
        df['Behaviour']     = df['B-SOiD labels'].apply(find_behav)
        df['Time (secs)']   = 1/30
        df['Frames'] = df['Frames'].apply(enlist)
        df_filtered = combine_consecutive(df)
        
        # Forward fill the behavioural bouts that last <= 0.3 secs.
        
        df_filtered = df_filtered.rename(columns={"Behaviour": "Behaviour without cutoff duration"})
        df_filtered['Behaviour'] = df_filtered['Behaviour without cutoff duration']
        # If the behavioural bout is less than 0.3 secs and the behaviour is not 'Missing',
        # set this to nan.
        df_filtered.at[(df_filtered['Time (secs)']<=0.3) & (df_filtered['Behaviour']!='Missing'), 'Behaviour'] = np.nan
        df_filtered['Behaviour'] = df_filtered['Behaviour'].fillna(method='ffill')
        # If behaviours at the start last less than 0.3 seconds, fill these in.
        ## LOOK AT THE SPIDER PLOTS AGAIN FOR THIS.
        df_filtered['Behaviour'] = df_filtered['Behaviour'].fillna(df_filtered['Behaviour without cutoff duration'].iloc[0])
        
        # Recombine the rows, after consecutive behaviours were created again.
        df_cleaned = combine_consecutive(df_filtered)
        # Create results for each frame again.
        df_cleaned = df_cleaned.explode('Frames')
        df_cleaned['Time (secs)'] = 1/30
        df_cleaned['Cumulative time (secs)'] = df_cleaned['Time (secs)'].cumsum()
        df_cleaned['Cumulative time (mins)'] = df_cleaned['Cumulative time (secs)'] * (1/60)
        
        # Calculate the stats for each cumulative time bin.
        for i in range(1,31+1):
    
            # Truncate the data to the cumulative time bin.
            df_TB = df_cleaned[(df_cleaned['Cumulative time (mins)'] >= 0) & 
                               (df_cleaned['Cumulative time (mins)'] <= i)].copy()
            
            # Combine rows into full length behavioural bouts.
            df_TB['Frames'] = df_TB['Frames'].apply(enlist)
            df_TB = combine_consecutive(df_TB)
            
            # Create a summary for each behaviour across the cumulative time bin.
            df_TB['Time bin'] = float(i)
            df_results = df_TB.groupby(['Time bin','Behaviour']).agg(list)
            df_results.index = list(df_results.index)        
            # Find the total times for each behaviour.
            indices_no_missing = [index for index in df_results.index if 'Missing' not in index]
            if len(indices_no_missing) == 0:
                df_results['Total time (secs)'] = 0
            else:
                df_results['Total time (secs)'] = sum(df_results.loc[indices_no_missing,'Time (secs)'].sum())
            
            # Calculate the stats.
            df_results['Total duration (secs)']       =  df_results['Time (secs)'].apply(sum)
            df_results['Behaviour time/total time']   = (df_results['Time (secs)'].apply(sum)/
                                                         df_results['Total time (secs)'])
            df_results['Bout frequency']              =  df_results['Time (secs)'].apply(len)
            df_results['Average bout lengths (secs)'] = (df_results['Time (secs)'].apply(sum)/
                                                         df_results['Time (secs)'].apply(len))
        
            # Prepare the data to be appended to the master files.
            for stat in stats_to_use:
                master[stat].loc[filename, df_results[stat].index] = df_results[stat]
                
    master_export = {}
                
    for stat in stats_to_use:
        
        master[stat] = clean_nans(master[stat])
        
        row_info = pd.read_excel(import_row_info, header=[0,1])
        row_info.index = row_info[('Full name','Blank')]
        master_export[stat] = pd.concat([row_info, master[stat]], axis=1)
        
        # Export the master dataframes.
        export_name = ('Time bins results '+'('+stat+').csv').replace('/','(div)')
        export_destination = os.path.join(export_location, export_name)
        master_export[stat].to_csv(export_destination, index=False)

