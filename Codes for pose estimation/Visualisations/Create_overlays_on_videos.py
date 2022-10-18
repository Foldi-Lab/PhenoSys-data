import cv2
import pandas as pd
import numpy as np
from glob import glob
from tqdm import tqdm
import matplotlib.pyplot as plt

def create_video_with_behaviours_overlayed(video_path, csv_path):
    
    # Put in settings
    # video_path = r"D:\B-SOiD off storage drive 2\Session\Red 0 Session 2 (2021-11-06) (576x432) (RMD)DLC_resnet50_Catherine_2VDLRFeb23shuffle1_200000_labeled.mp4"
    cap = cv2.VideoCapture(video_path)
    # csv_path = r"D:\B-SOiD off storage drive 2\Session\B-SOiD file.csv"
    df = pd.read_csv(csv_path, skiprows=[0,1], usecols=[1,2])
    df = df.rename(columns={'33': 'Group number', 'coords': 'Video time (frames)'})
    df.set_index('Video time (frames)')
    
    # Start of Harry's added code to rename group numbers to behaviours.
    def Harry_names1(name):
        name = int(name)
        if   name in [4,5,1,2,19]:
            name = 'Grooming'
        elif name in [28,25,30]:
            name = 'Walking'
        elif name in [29]:
            name = 'Rearing'
        elif name in [16,11,22,26,27,31,32,33,0,3,6,7,8,9,10,12,13,14,15,17,18,20,21,23,24]:
            name = 'Stationary'
        return(name)
    def Harry_names2(name):
        name = int(name)
        if   name in [4,5]:
            name = 'Grooming left side'
        elif name in [1,2,19]:
            name = 'Grooming right side'
        elif name in [28]:
            name = 'Rotate left'
        elif name in [25]:
            name = 'Rotate right'
        elif name in [30]:
            name = 'Locomote'
        elif name in [29]:
            name = 'Rearing'
        elif name in [16]:
            name = 'Huddled'
        elif name in [11,22,26,27,31,32,33]:
            name = 'Investigating'
        elif name in [0,3,6,7,8,9,10,12,13,14,15,17,18,20,21,23,24]:
            name = 'Inactive'
        return(name)
    def Harry_names3(name):
        name = int(name)
        if   name in [4,5,1,2,19]:
            name = 'Grooming'
        elif name in [28,25]:
            name = 'Rotate body'
        elif name in [30]:
            name = 'Locomote'
        elif name in [29]:
            name = 'Rearing'
        elif name in [16]:
            name = 'Huddled'
        elif name in [11,22,26,27,31,32,33]:
            name = 'Investigating'
        elif name in [0,3,6,7,8,9,10,12,13,14,15,17,18,20,21,23,24]:
            name = 'Inactive'
        return(name)
    df['Behaviour'] = df['Group number'].apply(Harry_names3)
    
    current_behaviour = ''
    start_frame = ''
    end_frame = ''
    exclude_behaviour = []
    behaviours = df['Behaviour'].to_list()
    grouped_behav = []
    behav_lengths = []
    
    for i in range(len(behaviours)):
        if behaviours[i] != current_behaviour:
            grouped_behav += [[]]
            current_behaviour = behaviours[i]
        grouped_behav[-1] += [behaviours[i]]
    
    for i in range(len(grouped_behav)):
        for j in range(len(grouped_behav[i])):
            behav_lengths += [len(grouped_behav[i])]
    
    df['Behaviour lengths (frames)'] = behav_lengths
    
    df['Behaviour (with exclusions)'] = list(zip(df['Behaviour'], df['Behaviour lengths (frames)']))
    def exclude(name):
        minimum_bout_length = 0.3*30
        if name[1] < minimum_bout_length:
            return('')
        else:
            return(name[0])
    df['Behaviour (with exclusions)'] = df['Behaviour (with exclusions)'].apply(exclude)
    df['Behaviour (with interpolations)'] = df['Behaviour (with exclusions)'].replace('',np.nan).fillna(method='ffill')
    
    cmap = plt.get_cmap('Set3').colors
    cmap = [tuple1[::-1] for tuple1 in cmap]
    cmap1 = []
    for tuple1 in cmap:
        temp = []
        for num in tuple1:
            temp += [num*255]
        cmap1 += [tuple(temp)]
    color_bgr = {}
    unique_behav = list(df['Behaviour'].unique()) + ['']
    for i in range(len(unique_behav)):
        color_bgr[unique_behav[i]] = cmap1[i]
        
    frame2event = {}
    for frame_no in df.index:
        event = df.at[frame_no, 'Behaviour (with interpolations)']
        
        frame2event[frame_no] = [event, (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color_bgr[event], 2, cv2.LINE_4]
        # if event == 'Walking':
        #     frame2event[frame_no] = ['Walking', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,32,160), 2, cv2.LINE_4]
        # elif event == 'Stationary':
        #     frame2event[frame_no] = ['Stationary', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 255, 96), 2, cv2.LINE_4]
        # elif event == 'Rearing':
        #     frame2event[frame_no] = ['Rearing', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_4]
        # elif event == 'Grooming':
        #     frame2event[frame_no] = ['Grooming', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (16, 160, 255), 2, cv2.LINE_4]
        # elif pd.isna(event):
        #     frame2event[frame_no] = ['', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (16, 160, 255), 2, cv2.LINE_4]
            
    frame_no = 0
    fps = cap.get(cv2.CAP_PROP_FPS)
    video_width   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    result = cv2.VideoWriter('C:/Users/DLC/Desktop/Labelled_video.mp4', 
                             cv2.VideoWriter_fourcc(*'mp4v'),
                             fps, (video_width, video_height))
    for frame_no in tqdm(range(1,total_frames)):
          
        # Capture frames in the video
        ret, frame = cap.read()
        #frame_no = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
     
        # # Use putText() method for
        # # inserting text on video
        options = [frame] + frame2event[frame_no]
        cv2.putText(*options)
            
        # Display the resulting frame
        #cv2.imshow('video', frame)
      
        # creating 'q' as the quit 
        # button for the video
        # if cv2.waitKey(25) & 0xFF == ord('q'):
        #     break
        
        result.write(frame)
        
    # When everything done, release 
    # the video capture and video 
    # write objects
    cap.release()
    result.release()
        
    # Closes all the frames
    cv2.destroyAllWindows()

def create_labelled_video_using_video_individual_session(video_path, csv_path):
    
    # # Put in settings
    # choose_session = '1'
    # choose_idlabel = 'Red 0'
    # choose_date = '(2022-02-18)'
    # choose_delay = 0 # This should take into account the 30 second buffer at the start.
    # # Put in the paths to the video and csv file.
    # video_path = ("C:/Users/DLC/Desktop/DeepLabCut analysis/"+
    #               choose_idlabel+" Session "+choose_session+" "+choose_date+" (576x432).mp4")
    # #video_path = glob(video_path)[0]
    # cap = cv2.VideoCapture(video_path)
    # csv_path = r"C:\Users\DLC\Desktop\DeepLabCut analysis\Time Bins of Sessions for 2VDLR-22.02.18 Sys20.xlsx"
    
    # # MOUSE STARTS INSIDE THE CHAMBER.
    # choose_session = '5'
    # choose_idlabel = 'Red 2'
    # choose_date = '(2022-02-24)'
    # choose_delay = 5 # This should take into account the 30 second buffer at the start.
    # # Put in the paths to the video and csv file.
    # video_path = ("Y:/Catherine PhenoSys/ABA+PhenoSys cohort 1/2VDLR 220224/Cut videos/"+
    #               choose_idlabel+" Session "+choose_session+" "+choose_date+" (576x432).mp4")
    # #video_path = glob(video_path)[0]
    # cap = cv2.VideoCapture(video_path)
    # csv_path = r"Y:\Catherine PhenoSys\ABA+PhenoSys cohort 1\2VDLR 220224\Time Bins of Sessions for 2VDLR-22.02.24 Sys20.xlsx"
    
    # MOUSE STARTS OUTSIDE THE CHAMBER.
    choose_session = '4'
    choose_idlabel = 'Red 1'
    choose_date = '(2022-02-20)'
    choose_delay = 10.5 # This should take into account the 30 second buffer at the start.
    # Put in the paths to the video and csv file.
    video_path = ("Y:/Catherine PhenoSys/ABA+PhenoSys cohort 1/2VDLR 220220/Cut videos/"+
                  choose_idlabel+" Session "+choose_session+" "+choose_date+" (576x432).mp4")
    video_path = r"Y:\Catherine PhenoSys\ABA+PhenoSys cohort 1\2VDLR 220220\Cut videos\Red 1 Session 4 (2022-02-20) (576x432)DLC_resnet50_Catherine_2VDLRFeb23shuffle1_200000_filtered_labeled.mp4"
    #video_path = glob(video_path)[0]
    cap = cv2.VideoCapture(video_path)
    csv_path = r"Y:\Catherine PhenoSys\ABA+PhenoSys cohort 1\2VDLR 220220\Time Bins of Sessions for 2VDLR-22.02.20 Sys20.xlsx"
    
    df = pd.read_excel(csv_path)
    
    # Filter the data down to the mouse and session.
    df = df[df["IdLabel"] == choose_idlabel]
    df = df[df["Session number"] == int(choose_session)]
    
    # Adjust the seconds column.
    first_time_point = df['Video time (secs)'].iloc[0]
    df['Video time (secs)'] = df['Video time (secs)'] - first_time_point
    df['Video time (secs)'] = df['Video time (secs)'] + choose_delay
    
    # Create a frames column.
    df['Frames'] = df['Video time (secs)'] * 30
    df['Frames'] = round(df['Frames'])
    df['Frames shifted'] = df['Frames'].shift(-1)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    df.index = range(len(df))
    df.at[len(df)-1,'Frames shifted'] = total_frames
    
    # Create a column that defines the frames for each event.
    df['Frame boundaries'] = list(zip(df['Frames'], df['Frames shifted']))
    df['Frame intervals'] = [list(range(int(pair[0]),int(pair[1]))) for pair in df['Frame boundaries']]
    
    # Create reference between the event and its frame numbers.
    events = df[['SystemMsg','Frame intervals']].groupby('SystemMsg').agg(sum)
    
    frame2event = {}
    for event in events.index:
        for frame_no in events.at[event,'Frame intervals']:
            if event == 'start exp':
                frame2event[frame_no] = ['Start exp', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,32,160), 2, cv2.LINE_4]
            elif event == 'positive':
                frame2event[frame_no] = ['Positive', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 255, 96), 2, cv2.LINE_4]
            elif event == 'incorrect':
                frame2event[frame_no] = ['Incorrect', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_4]
            elif event == 'omission':
                frame2event[frame_no] = ['Omission', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (16, 160, 255), 2, cv2.LINE_4]
            elif event == 'end exp':
                frame2event[frame_no] = ['End exp', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4]
            elif event == 'CondMod1':
                frame2event[frame_no] = ['Retrieved pellet', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4]
    for frame_no in np.arange(choose_delay*30):
        frame2event[frame_no] = ['Before session start', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (169, 169, 169), 2, cv2.LINE_4]
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    video_width   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    result = cv2.VideoWriter('C:/Users/hazza/Desktop/Labelled_video.mp4', 
                             cv2.VideoWriter_fourcc(*'mp4v'),
                             fps, (video_width, video_height))
    
    for frame_no in tqdm(range(1,total_frames)):
          
        # Capture frames in the video
        ret, frame = cap.read()
        #frame_no = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
     
        # # Use putText() method for
        # # inserting text on video
        options = [frame] + frame2event[frame_no]
        cv2.putText(*options)
            
        # # Display the resulting frame
        # cv2.imshow('video', frame)
      
        # # creating 'q' as the quit 
        # # button for the video
        # if cv2.waitKey(2) & 0xFF == ord('q'):
        #     break
    
        result.write(frame)
        
    # When everything done, release 
    # the video capture and video 
    # write objects
    cap.release()
    result.release()
        
    # Closes all the frames
    cv2.destroyAllWindows()
    
def create_labelled_video_using_video_whole_experiment(video_path, csv_path):
    
    #choose_delay = 30 # This should take into account the 30 second buffer at the start.
    
    # Put in the paths to the video and csv file.
    #video_path = r"Y:\Catherine PhenoSys\ABA+PhenoSys cohort 2\GTPT4 220315\IRcam1.mov"
    cap = cv2.VideoCapture(video_path)
    #csv_path = r"Y:\Catherine PhenoSys\ABA+PhenoSys cohort 2\GTPT4 220315\Time Bins of Sessions for GTPT4-22.03.15 Sys10.xlsx"
    df = pd.read_excel(csv_path)
    
    # Create a frames column.
    df['Frames'] = df['Video time (secs)'] * 30
    df['Frames'] = round(df['Frames'])
    df['Frames shifted'] = df['Frames'].shift(-1)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    df.index = range(len(df))
    df.at[len(df)-1,'Frames shifted'] = total_frames
    
    # Create a column that defines the frames for each event.
    df['Frame boundaries'] = list(zip(df['Frames'], df['Frames shifted']))
    df['Frame intervals'] = [list(range(int(pair[0]),int(pair[1]))) for pair in df['Frame boundaries']]
    
    # Create reference between the event and its frame numbers.
    events = df[['SystemMsg','Frame intervals']].groupby('SystemMsg').agg(sum)
    
    frame2event = {}
    for event in events.index:
        for frame_no in events.at[event,'Frame intervals']:
            if event == 'start exp':
                frame2event[frame_no] = ['Start exp', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,32,160), 2, cv2.LINE_4]
            elif event == 'positive':
                frame2event[frame_no] = ['Positive', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 255, 96), 2, cv2.LINE_4]
            elif event == 'incorrect':
                frame2event[frame_no] = ['Incorrect', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_4]
            elif event == 'omission':
                frame2event[frame_no] = ['Omission', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (16, 160, 255), 2, cv2.LINE_4]
            elif event == 'end exp':
                frame2event[frame_no] = ['End exp', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_4]
    
    first_session_frame = int(df.at[0,'Frames'])
    for frame_no in range(first_session_frame):
        frame2event[frame_no] = ['Before session start', (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (169, 169, 169), 2, cv2.LINE_4]
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, first_session_frame)
    ret, frame = cap.read()
    cv2.imshow('video', frame)
    
    frame_no = first_session_frame
    
    while(True):
          
        # Capture frames in the video
        ret, frame = cap.read()
        frame_no += 1
        #frame_no = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
     
        # # Use putText() method for
        # # inserting text on video
        options = [frame] + frame2event[frame_no]
        cv2.putText(*options)
            
        # Display the resulting frame
        cv2.imshow('video', frame)
      
        # creating 'q' as the quit 
        # button for the video
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break
        
    # release the cap object
    cap.release()
    # close all windows
    cv2.destroyAllWindows()
