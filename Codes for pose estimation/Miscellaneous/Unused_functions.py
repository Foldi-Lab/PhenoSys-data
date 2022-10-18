from glob import glob
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys
from tqdm import tqdm
from numpy.linalg import norm

def create_ffmpeg_command_to_snip_out_rats_missing_in_videos(location):
    
    # location = '//storage.erc.monash.edu.au/shares/DeepLabCut-rodent-vid/Catherine PhenoSys/*/*/Cut videos/*RMD.csv'
    paths = glob(location)
    
    input1 = []
    
    # Import the frames to include.
    for path in tqdm(paths, ncols=70):
    
        frames = pd.read_csv(path, usecols=[0], skiprows=[0,1,2], header=None)
        frames = frames[0].tolist()
        start_times = []
        end_times   = []    
            
        for i in range(len(frames)):
            
            if i == 0:
                start_times.append(frames[i])
                
            if i == len(frames)-1:
                end_times.append(frames[i])
                
            if i != len(frames)-1 and frames[i+1] - frames[i] > 1:
                end_times.append(frames[i])
                start_times.append(frames[i+1])
        
        if len(start_times) != len(end_times):
            print('The start and end time lists are not the same lengths.')
            sys.exit()
        
        results = pd.DataFrame({})
        results["Start times"] = start_times
        results["End times"] = end_times
        
        # Create ffmpeg string.
        import_video = (os.path.dirname(path) + "\\" +
                        os.path.basename(path)[:-65]+'.mp4')
        export_video = (os.path.dirname(path) + "\\" +
                        os.path.basename(path)[:-65]+' (RMD).mp4')
        import_video = '"' + import_video + '"'
        export_video = '"' + export_video + '"'
        timestamps = ''
        for i in range(len(results)):
            timestamps = (timestamps + 'between(t,' + str(results.at[i,'Start times']/30) + 
                          ',' + str(results.at[i,'End times']/30) + ')+')
        timestamps = timestamps[:-1] # Remove the '+' at the end.
        timestamps = "'" + timestamps + "'"
        
        string = ('ffmpeg -y -i ' + import_video + ' -vf "select=' + timestamps +
                  ',setpts=N/FRAME_RATE/TB" ' + export_video + ' & ^')
        
        input1 += [string]
    
    # # Remove the last "& ^" because there is nothing else left to add.
    input1[-1] = input1[-1][:-4]
    
    # Save the lines to a text file.
    with open('C:/Users/DLC/Desktop/Clipped_videos.txt', 'w') as f:
        for line in input1:
            f.write(line)
            f.write('\n')

def find_average_velocity_and_durations(location):

    # location = '//storage.erc.monash.edu.au/shares/DeepLabCut-rodent-vid/Catherine PhenoSys/*/*/Cut videos/*_RMD.csv'
    paths = glob(location)
    results = pd.DataFrame(columns=['Average velocity (px/sec)', 'Total duration (secs)'])
    results.index.name = 'Videos'
    
    for path in tqdm(paths, ncols=70):
        
        # Import the centre-point data.
        centre_point = pd.read_csv(path, skiprows=[0,1], usecols=[10,11])
        centre_point.columns = ['x1','y1']
        
        # Shift the original data points to make new ones.
        centre_point['x2'] = centre_point['x1'].shift(1)
        centre_point['y2'] = centre_point['y1'].shift(1)
        centre_point = centre_point.drop(0)
        
        # Find the difference between the new and old ones.
        centre_point['dx'] = centre_point['x2'] - centre_point['x1']
        centre_point['dy'] = centre_point['y2'] - centre_point['y1']
        centre_point['(dx,dy)'] = list(zip(centre_point['dx'], centre_point['dy']))
        
        # Compute the distance travelled in each frame.
        centre_point['norm'] = centre_point['(dx,dy)'].apply(norm)
        
        # Find the average velocity for this file.
        distance = centre_point['norm'].sum()
        duration = len(centre_point)*(1/30)
        average_velocity = distance / duration
        
        # Add the data to the results table.
        results.loc[os.path.basename(path)] = [average_velocity, duration]
    
    # Save the results.
    results.to_csv('C:/Users/DLC/Desktop/Average_velocity.csv')
            
def plot_centre_point_likelihoods_over_time(location):

    # location = '//storage.erc.monash.edu.au/shares/DeepLabCut-rodent-vid/Catherine PhenoSys/*/*/Cut videos/*RMD.csv'
    paths = glob(location)
    
    for path in tqdm(paths, ncols=70):
        
        df = pd.read_csv(path, skiprows=[0,2], usecols=[12])
        plt.figure(figsize=(12, 5))
        plt.scatter(df.index, df, color='black', s=0.005)
        plt.axhline(y=0.05, color='r', linestyle='-')
        plt.ylim(0, 1)
        plt.xlim(0, 60000)
        plt.ylabel('Likelihood of the centre-point prediction')
        plt.xlabel('Frame number')
        plt.title('Likelihood of the centre-point prediction vs frame number')
        plt.xticks(list(range(0,60000,1000)), rotation='vertical')
        plt.savefig('C:/Users/DLC/Desktop/PhenoSys plots 25-5-22/'+
                    os.path.basename(path)[:-4]+'.png')
        plt.close()
        