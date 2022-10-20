#-----------------------------------------------------------------------------#

# FILL IN THESE INPUTS BEFORE RUNNING THIS SCRIPT.
# USE THESEE EXAMPLE FILES.
# Video time results.csv
# Time bins results (Behaviour time(div)total time).csv
# Time bins results (Average bout lengths (secs)).csv

# This folder should contain the files above.
import_location = r"C:\Users\hazza\Desktop\DeepLabCut\Codes\All together\Import and export files for codes"

#-----------------------------------------------------------------------------#

import matplotlib.pyplot as plt
from matplotlib import rc
import pandas as pd
import numpy as np
from math import pi
from scipy import stats
import os
from tqdm import tqdm
import seaborn as sns

def create_spider_plots(import_location):
    
    import_path = os.path.join(import_location, 'Video time results.csv')
    export_base_path = import_location
    
    all_data    = pd.read_csv(import_path)
    all_data.index = all_data['Full name']
    
    # Create data about the proportion of time spent doing a behaviour and average
    # bout lengths.
    behaviours = ['Grooming', 'Inactive', 'Investigating', 'Locomote', 'Rearing', 'Rotate body']
    # behaviours = ['Rotate body', 'Locomote', 'Inactive', 'Investigating', 'Rearing', 'Grooming']
    durations = [behav+' (total duration in secs)' for behav in behaviours]
    all_data['Sum of durations'] = all_data[durations].sum(axis=1)
    proportions = [behav+' (total duration/total time)' for behav in behaviours]
    all_data[proportions] = all_data[durations].div(all_data['Sum of durations'], axis=0)
    all_data[proportions] = all_data[proportions].fillna(0)
    
    bout_lengths = [behav+' (average bout length in secs)' for behav in behaviours]
    num_bouts    = [behav+' (bout frequency)' for behav in behaviours]
    bout_lengths_data = all_data[durations]
    bout_lengths_data.columns = bout_lengths
    num_bouts_data = all_data[num_bouts]
    num_bouts_data.columns = bout_lengths
    all_data[bout_lengths] = bout_lengths_data.div(num_bouts_data)
    all_data[bout_lengths] = all_data[bout_lengths].fillna(0)
    
    dataset_option   = 'All videos'
    
    for type_stat in ['total duration/total time', 'average bout length in secs']:
        
        # for dataset_option in ['All videos', 'First, middle and last videos']:
    
        print('Analysing ' + dataset_option + ' and ' + type_stat)
        
        new_folder = (dataset_option + ', ' + type_stat).replace('/',' over ')
        export_location       = os.path.join(export_base_path, new_folder)
        export_location_plots = os.path.join(export_base_path, new_folder, 'Plots')
        export_location_data  = os.path.join(export_base_path, new_folder, 'Raw data')
        os.mkdir(export_location)
        os.mkdir(export_location_plots)
        os.mkdir(export_location_data)
        
        drop_columns = [col for col in all_data.columns if type_stat not in col]
        group_data = all_data.drop(columns=drop_columns)
        
        # Create a truncated version of this dataset for within exp1, within exp2 and 
        # between exp1 and exp2 analyses.
        within_exp1 = all_data.copy()
        within_exp1 = within_exp1[pd.isna(within_exp1["Non-learners to exclude"])]
        within_exp1 = within_exp1[pd.isna(within_exp1["Sessions to exclude"    ])]
        within_exp1 = within_exp1[pd.isna(within_exp1["Sessions post-criterion"])]
        within_exp1 = within_exp1[within_exp1['Timing of ABA'] == 'Before ABA']
    
        within_exp2 = all_data.copy()
        # Laura said for this analysis, not to exclude the resistant rats.
        # within_exp2 = within_exp2[pd.isna(within_exp2["Resistant rats to exclude"])]
        within_exp2 = within_exp2[pd.isna(within_exp2["Sessions to exclude"      ])]
        within_exp2 = within_exp2[pd.isna(within_exp2["Sessions post-criterion"  ])]
        within_exp2 = within_exp2[within_exp2['Timing of ABA'] == 'After ABA']
    
        exp1_v_exp2 = all_data.copy()
        # Laura said for this analysis, keep the non-learners.
        # exp1_v_exp2 = exp1_v_exp2[pd.isna(exp1_v_exp2["Non-learners to exclude"])]
        exp1_v_exp2 = exp1_v_exp2[pd.isna(exp1_v_exp2["Sessions to exclude"    ])]
        exp1_v_exp2 = exp1_v_exp2[pd.isna(exp1_v_exp2["Sessions post-criterion"])]
        
        if dataset_option == 'First, middle and last videos':
            claire_path  = r"C:\Users\hazza\Desktop\DeepLabCut\Codes\DeepLabCut zone and behavioural results\Videos highlighted by Claire.xlsx"
            FML_videos = pd.read_excel(claire_path)
            inc_rows_wexp1 = set(within_exp1['Full name']).intersection(list(FML_videos['Full name']))
            inc_rows_wexp2 = set(within_exp2['Full name']).intersection(list(FML_videos['Full name']))
            inc_rows_e1ve2 = set(exp1_v_exp2['Full name']).intersection(list(FML_videos['Full name']))
            within_exp1 = within_exp1.loc[inc_rows_wexp1]
            within_exp2 = within_exp2.loc[inc_rows_wexp2]
            exp1_v_exp2 = exp1_v_exp2.loc[inc_rows_e1ve2]
        
        # Create a list of options for analysis.
        options = []
        
        option = {}
        option['Group 1 videos'] = within_exp1[within_exp1['ABA phenotype'] == 'Susceptible']['Full name'].to_list()
        option['Group 2 videos'] = within_exp1[within_exp1['ABA phenotype'] == 'Resistant']['Full name'].to_list()
        option['Group 1 name']   = 'Susceptible'
        option['Group 2 name']   = 'Resistant'
        options += [option]
        
        option = {}
        option['Group 1 videos'] = within_exp2[within_exp2['Learnt R1 within 20 sessions?'] == 'Yes']['Full name'].to_list()
        option['Group 2 videos'] = within_exp2[within_exp2['Learnt R1 within 20 sessions?'] == 'No' ]['Full name'].to_list()
        option['Group 1 name']   = 'Learners'
        option['Group 2 name']   = 'Non-learners'
        options += [option]
        
        option = {}
        option['Group 1 videos'] = exp1_v_exp2[exp1_v_exp2['Timing of ABA'] == 'Before ABA']['Full name'].to_list()
        option['Group 2 videos'] = exp1_v_exp2[exp1_v_exp2['Timing of ABA'] == 'After ABA' ]['Full name'].to_list()
        option['Group 1 name']   = 'Before ABA'
        option['Group 2 name']   = 'After ABA'
        options += [option]
        
        option = {}
        option['Group 1 videos'] = within_exp1[(within_exp1['Session type']=='PD') &
                                               (within_exp1['ABA phenotype']=='Susceptible')]['Full name'].to_list()
        option['Group 2 videos'] = within_exp1[(within_exp1['Session type']=='PD') &
                                               (within_exp1['ABA phenotype']=='Resistant')]['Full name'].to_list()
        option['Group 1 name']   = 'Within PD, Susceptible'
        option['Group 2 name']   = 'Within PD, Resistant'
        options += [option]
        
        option = {}
        option['Group 1 videos'] = within_exp2[(within_exp2['Session type']=='PD') &
                                               (within_exp2['Learnt R1 within 20 sessions?']=='Yes')]['Full name'].to_list()
        option['Group 2 videos'] = within_exp2[(within_exp2['Session type']=='PD') &
                                               (within_exp2['Learnt R1 within 20 sessions?']=='No') ]['Full name'].to_list()
        option['Group 1 name']   = 'Within PD, Learners'
        option['Group 2 name']   = 'Within PD, Non-learners'
        options += [option]
        
        option = {}
        option['Group 1 videos'] = exp1_v_exp2[(exp1_v_exp2['Session type']=='PD') &
                                               (exp1_v_exp2['Timing of ABA']=='Before ABA')]['Full name'].to_list()
        option['Group 2 videos'] = exp1_v_exp2[(exp1_v_exp2['Session type']=='PD') &
                                               (exp1_v_exp2['Timing of ABA']=='After ABA') ]['Full name'].to_list()
        option['Group 1 name']   = 'Within PD, Before ABA'
        option['Group 2 name']   = 'Within PD, After ABA'
        options += [option]
        
        option = {}
        option['Group 1 videos'] = within_exp1[(within_exp1['Session type']=='R1') &
                                               (within_exp1['ABA phenotype']=='Susceptible')]['Full name'].to_list()
        option['Group 2 videos'] = within_exp1[(within_exp1['Session type']=='R1') &
                                               (within_exp1['ABA phenotype']=='Resistant')]['Full name'].to_list()
        option['Group 1 name']   = 'Within R1, Susceptible'
        option['Group 2 name']   = 'Within R1, Resistant'
        options += [option]
        
        option = {}
        option['Group 1 videos'] = within_exp2[(within_exp2['Session type']=='R1') &
                                               (within_exp2['Learnt R1 within 20 sessions?']=='Yes')]['Full name'].to_list()
        option['Group 2 videos'] = within_exp2[(within_exp2['Session type']=='R1') &
                                               (within_exp2['Learnt R1 within 20 sessions?']=='No') ]['Full name'].to_list()
        option['Group 1 name']   = 'Within R1, Learners'
        option['Group 2 name']   = 'Within R1, Non-learners'
        options += [option]
        
        option = {}
        option['Group 1 videos'] = exp1_v_exp2[(exp1_v_exp2['Session type']=='R1') &
                                               (exp1_v_exp2['Timing of ABA']=='Before ABA')]['Full name'].to_list()
        option['Group 2 videos'] = exp1_v_exp2[(exp1_v_exp2['Session type']=='R1') &
                                               (exp1_v_exp2['Timing of ABA']=='After ABA') ]['Full name'].to_list()
        option['Group 1 name']   = 'Within R1, Before ABA'
        option['Group 2 name']   = 'Within R1, After ABA'
        options += [option]
        
        results = []
        graph_no = 0
        
        for option in tqdm(options, ncols=70):
            
            graph_no += 1
        
            drop_rows1 = [row for row in group_data.index if row not in option['Group 1 videos']]
            drop_rows2 = [row for row in group_data.index if row not in option['Group 2 videos']]
            df1 = group_data.drop(drop_rows1)
            df2 = group_data.drop(drop_rows2)
            
            # Find the number of sessions and rats.
            group1_sessions = len(df1)
            group1_rats = [' '.join(name.split(' ')[:2]) for name in df1.index]
            group1_rats = len(set(group1_rats))
            
            group2_sessions = len(df2)
            group2_rats = [' '.join(name.split(' ')[:2]) for name in df2.index]
            group2_rats = len(set(group2_rats))
            
            # ------- PART 1: Create background
            
            # Analyse the data
            result = {}
            headings = []
            
            from math import log10, floor
            def round_to_1(x):
               return round(x, -int(floor(log10(abs(x)))))
            
            # for behav in behaviours:
            #     # Perform a 2-sample independent t-test with equal variances.
            #     group1_values = df1[behav+' ('+type_stat+')'].to_list()
            #     group2_values = df2[behav+' ('+type_stat+')'].to_list()
            #     t_stat, p_val = stats.ttest_ind(group1_values, group2_values)
            #     result['t-Test p-value'+behav] = p_val
            #     if p_val < 0.05:
            #         headings += [behav+'\n(* p='+str(round_to_1(p_val))+')']
            #         continue
            #     headings += [behav]
            # headings = [('Rotate\nbody' if behav=='Rotate body' else behav)
            #             for behav in behaviours]
            headings = behaviours
            
            fontsize_labels = 11
            fontsize_ticks  = 8
             
            # number of variable
            categories=headings
            N = len(categories)
             
            # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
            angles = [n / float(N) * 2 * pi for n in range(N)]
            angles += angles[:1]
             
            # Initialise the spider plot
            fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(4,5), dpi=150)
             
            # If you want the first axis to be on top:
            ax.set_theta_offset(pi / 2)
            ax.set_theta_direction(-1)
             
            # Draw one axe per variable + add labels
            # ax.tick_params(pad=-1)
            plt.xticks(angles[:-1], categories, fontsize=fontsize_labels)
            
            # Go through labels and adjust alignment based on where
            # it is in the circle.
            for label, angle in zip(ax.get_xticklabels(), angles):
              if angle in (0, np.pi):
                label.set_horizontalalignment('center')
              elif 0 < angle < np.pi:
                label.set_horizontalalignment('left')
              else:
                label.set_horizontalalignment('right')
            
            # ------- PART 2: Add plots
             
            # Plot each individual = each line of the data
            # I don't make a loop, because plotting more than 3 groups makes the chart unreadable
                
            mean_values1 = list(df1.mean())
            sem_values1  = list(stats.sem(df1))
            mean_values1 += mean_values1[:1]
            sem_values1  += sem_values1[:1]
            upper_bound1 = [mean+sem for mean,sem in zip(mean_values1,sem_values1)]
            lower_bound1 = [mean-sem for mean,sem in zip(mean_values1,sem_values1)]
            label1      = (option['Group 1 name'] + ', ' + str(group1_sessions) + 
                           ' sessions, ' + str(group1_rats) + ' rats')
            ax.plot(angles, mean_values1, linewidth=1, linestyle='solid',  label=label1, color='red')
            ax.plot(angles, upper_bound1, linewidth=1, linestyle='dashed', color='red', alpha=0.3)
            ax.plot(angles, lower_bound1, linewidth=1, linestyle='dashed', color='red', alpha=0.3)
            ax.fill_between(angles, upper_bound1, lower_bound1, color='lightpink', alpha=0.3)
            
            mean_values2 = list(df2.mean())
            sem_values2  = list(stats.sem(df2))
            mean_values2 += mean_values2[:1]
            sem_values2  += sem_values2[:1]
            upper_bound2 = [mean+sem for mean,sem in zip(mean_values2,sem_values2)]
            lower_bound2 = [mean-sem for mean,sem in zip(mean_values2,sem_values2)]
            label2      = (option['Group 2 name'] + ', ' + str(group2_sessions) + 
                           ' sessions, ' + str(group2_rats) + ' rats')
            ax.plot(angles, mean_values2, linewidth=1, linestyle='solid',  label=label2, color='blue')
            ax.plot(angles, upper_bound2, linewidth=1, linestyle='dashed', color='blue', alpha=0.3)
            ax.plot(angles, lower_bound2, linewidth=1, linestyle='dashed', color='blue', alpha=0.3)
            ax.fill_between(angles, upper_bound2, lower_bound2, color='lightblue', alpha=0.3)
             
            # # Ind2
            # values=df.loc[1].drop('group').values.flatten().tolist()
            # values += values[:1]
            # ax.plot(angles, values, linewidth=1, linestyle='solid', label="group B")
            # ax.fill(angles, values, 'r', alpha=0.1)
            
            if type_stat == 'total duration/total time':
                # Draw ylabels
                ax.set_rlabel_position(0)
                max_value = 0.6
                y_ticks  = list(np.arange(0,max_value,max_value/6))
                y_labels = [str(round(num,2)) for num in y_ticks]
                plt.yticks(y_ticks, y_labels, fontsize=fontsize_ticks)
                plt.ylim(0,max_value)
            elif type_stat == 'average bout length in secs':
                # Draw ylabelsa
                ax.set_rlabel_position(0)
                max_value = 9
                y_ticks  = list(np.arange(0,max_value,max_value/6))
                y_labels = [str(round(num,2)) for num in y_ticks]
                plt.yticks(y_ticks, y_labels, fontsize=fontsize_ticks)
                plt.ylim(0,max_value)
            
            # Add legend
            plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.3))
            
            plt.title('Graph number: '+str(graph_no)+'\n'+
                      'Statistic: '+type_stat+'\n'+
                      'Dataset: '+dataset_option+'\n', color='grey', fontsize=fontsize_labels)
            
            # Analyse the data.
            result['Graph number'] = graph_no
            result['Group 1 name'] = option['Group 1 name']
            result['Group 1 number of sessions'] = group1_sessions
            result['Group 1 number of rats']     = group1_rats
            result['Group 1 statistical entropy'] = stats.entropy(mean_values1)
            result['Group 2 name'] = option['Group 2 name']
            result['Group 2 number of sessions'] = group2_sessions
            result['Group 2 number of rats']     = group2_rats
            result['Group 2 statistical entropy'] = stats.entropy(mean_values2)
            result['Kullback-Leibler divergence'] = stats.entropy(mean_values1, qk=mean_values2)
            results += [result]
            
            # Save the raw data.
            export_name_data = ('Graph '+str(graph_no)+' '+
                                option['Group 1 name']+' vs '+option['Group 2 name']+'.xlsx')
            
            with pd.ExcelWriter(os.path.join(export_location_data, export_name_data)) as writer:  
                df1.to_excel(writer, sheet_name=option['Group 1 name'])
                df2.to_excel(writer, sheet_name=option['Group 2 name'])
            
            # Save the plots.
            export_name_plots = ('Graph '+str(graph_no)+' '+
                                 option['Group 1 name']+' vs '+option['Group 2 name']+'.png')
            export_destination = os.path.join(export_location_plots, export_name_plots)
            plt.savefig(export_destination, bbox_inches='tight')
            
            plt.close()
            
        results = pd.DataFrame(results)
        results = results.set_index('Graph number')
        results.to_excel(os.path.join(export_location_data,'Distribution stats.xlsx'))

def create_time_bin_plots(import_location):
    
    proportions_path = os.path.join(import_location, 'Time bins results (Behaviour time(div)total time).csv')
    aveboutleng_path = os.path.join(import_location, 'Time bins results (Average bout lengths (secs)).csv')
    export_base_path = import_location
    
    for type_stat in ['Time spent doing behaviour/total time', 'Average bout lengths (secs)']:
        
        if type_stat == 'Time spent doing behaviour/total time':
            path = proportions_path
        elif type_stat == 'Average bout lengths (secs)':
            path = aveboutleng_path
        all_data = pd.read_csv(path, header=[0,1])
        all_data.index = all_data[('Full name','Blank')]
        
        # Change the headers from a multi-index to a single index.
        current_headers = tuple(all_data.columns)
        new_headers     = []
        for tuple1 in current_headers:
            if tuple1[1] == 'Blank':
                new_headers += [tuple1[0]]
            else:
                new_headers += [tuple1[0]+","+tuple1[1]]
        all_data.columns = new_headers
    
        # for dataset_option in ['All videos', 'First, middle and last videos']:
    
        print('Analysing ' + type_stat)
        
        new_folder = 'Time bin heat maps, '+type_stat.replace('/','(div)')
        export_location = os.path.join(export_base_path, new_folder)
        os.mkdir(export_location)
        
        # Create a truncated version of this dataset for within exp1, within exp2 and 
        # between exp1 and exp2 analyses.
        
        within_exp1 = all_data.copy()
        within_exp1 = within_exp1[pd.isna(within_exp1["Non-learners to exclude"])]
        within_exp1 = within_exp1[pd.isna(within_exp1["Sessions to exclude"    ])]
        within_exp1 = within_exp1[pd.isna(within_exp1["Sessions post-criterion"])]
        within_exp1 = within_exp1[within_exp1['Timing of ABA'] == 'Before ABA']
        
        within_exp2 = all_data.copy()
        # Laura said for this analysis, not to exclude the resistant rats.
        # within_exp2 = within_exp2[pd.isna(within_exp2["Resistant rats to exclude"])]
        within_exp2 = within_exp2[pd.isna(within_exp2["Sessions to exclude"      ])]
        within_exp2 = within_exp2[pd.isna(within_exp2["Sessions post-criterion"  ])]
        within_exp2 = within_exp2[within_exp2['Timing of ABA'] == 'After ABA']
        
        exp1_v_exp2 = all_data.copy()
        # Laura said for this analysis, keep the non-learners.
        # exp1_v_exp2 = exp1_v_exp2[pd.isna(exp1_v_exp2["Non-learners to exclude"])]
        exp1_v_exp2 = exp1_v_exp2[pd.isna(exp1_v_exp2["Sessions to exclude"    ])]
        exp1_v_exp2 = exp1_v_exp2[pd.isna(exp1_v_exp2["Sessions post-criterion"])]
        
        # Exclude the columns that do not contain the statistic of interest.
        drop_columns = [col for col in all_data.columns if ',' not in col]
        all_data = all_data.drop(columns=drop_columns)
        
        # Import a file with the existing first, middle and last sessions (FML) for PD/R1.
        dataset_option = 'All videos'
        # dataset_option = 'First, middle and last videos'
        
        if dataset_option == 'First, middle and last videos':
            claire_path  = r"C:\Users\hazza\Desktop\DeepLabCut\Codes\DeepLabCut zone and behavioural results\Videos highlighted by Claire.xlsx"
            FML_videos = pd.read_excel(claire_path)
            inc_rows_wexp1 = set(within_exp1['Full name']).intersection(list(FML_videos['Full name']))
            inc_rows_wexp2 = set(within_exp2['Full name']).intersection(list(FML_videos['Full name']))
            inc_rows_e1ve2 = set(exp1_v_exp2['Full name']).intersection(list(FML_videos['Full name']))
            within_exp1 = within_exp1.loc[inc_rows_wexp1]
            within_exp2 = within_exp2.loc[inc_rows_wexp2]
            exp1_v_exp2 = exp1_v_exp2.loc[inc_rows_e1ve2]
        
        # Create a list of options for analysis.
        options = []
        
        option = {}
        option['Group 1 videos'] = within_exp1[within_exp1['ABA phenotype'] == 'Susceptible']['Full name'].to_list()
        option['Group 2 videos'] = within_exp1[within_exp1['ABA phenotype'] == 'Resistant']['Full name'].to_list()
        option['Group 1 name']   = 'Susceptible'
        option['Group 2 name']   = 'Resistant'
        options += [option]
        
        option = {}
        option['Group 1 videos'] = within_exp2[within_exp2['Learnt R1 within 20 sessions?'] == 'Yes']['Full name'].to_list()
        option['Group 2 videos'] = within_exp2[within_exp2['Learnt R1 within 20 sessions?'] == 'No' ]['Full name'].to_list()
        option['Group 1 name']   = 'Learners'
        option['Group 2 name']   = 'Non-learners'
        options += [option]
        
        option = {}
        option['Group 1 videos'] = exp1_v_exp2[exp1_v_exp2['Timing of ABA'] == 'Before ABA']['Full name'].to_list()
        option['Group 2 videos'] = exp1_v_exp2[exp1_v_exp2['Timing of ABA'] == 'After ABA' ]['Full name'].to_list()
        option['Group 1 name']   = 'Before ABA'
        option['Group 2 name']   = 'After ABA'
        options += [option]
        
        option = {}
        option['Group 1 videos'] = within_exp1[(within_exp1['Session type']=='PD') &
                                               (within_exp1['ABA phenotype']=='Susceptible')]['Full name'].to_list()
        option['Group 2 videos'] = within_exp1[(within_exp1['Session type']=='PD') &
                                               (within_exp1['ABA phenotype']=='Resistant')]['Full name'].to_list()
        option['Group 1 name']   = 'Within PD, Susceptible'
        option['Group 2 name']   = 'Within PD, Resistant'
        options += [option]
        
        option = {}
        option['Group 1 videos'] = within_exp2[(within_exp2['Session type']=='PD') &
                                               (within_exp2['Learnt R1 within 20 sessions?']=='Yes')]['Full name'].to_list()
        option['Group 2 videos'] = within_exp2[(within_exp2['Session type']=='PD') &
                                               (within_exp2['Learnt R1 within 20 sessions?']=='No') ]['Full name'].to_list()
        option['Group 1 name']   = 'Within PD, Learners'
        option['Group 2 name']   = 'Within PD, Non-learners'
        options += [option]
        
        option = {}
        option['Group 1 videos'] = exp1_v_exp2[(exp1_v_exp2['Session type']=='PD') &
                                               (exp1_v_exp2['Timing of ABA']=='Before ABA')]['Full name'].to_list()
        option['Group 2 videos'] = exp1_v_exp2[(exp1_v_exp2['Session type']=='PD') &
                                               (exp1_v_exp2['Timing of ABA']=='After ABA') ]['Full name'].to_list()
        option['Group 1 name']   = 'Within PD, Before ABA'
        option['Group 2 name']   = 'Within PD, After ABA'
        options += [option]
        
        option = {}
        option['Group 1 videos'] = within_exp1[(within_exp1['Session type']=='R1') &
                                               (within_exp1['ABA phenotype']=='Susceptible')]['Full name'].to_list()
        option['Group 2 videos'] = within_exp1[(within_exp1['Session type']=='R1') &
                                               (within_exp1['ABA phenotype']=='Resistant')]['Full name'].to_list()
        option['Group 1 name']   = 'Within R1, Susceptible'
        option['Group 2 name']   = 'Within R1, Resistant'
        options += [option]
        
        option = {}
        option['Group 1 videos'] = within_exp2[(within_exp2['Session type']=='R1') &
                                               (within_exp2['Learnt R1 within 20 sessions?']=='Yes')]['Full name'].to_list()
        option['Group 2 videos'] = within_exp2[(within_exp2['Session type']=='R1') &
                                               (within_exp2['Learnt R1 within 20 sessions?']=='No') ]['Full name'].to_list()
        option['Group 1 name']   = 'Within R1, Learners'
        option['Group 2 name']   = 'Within R1, Non-learners'
        options += [option]
        
        option = {}
        option['Group 1 videos'] = exp1_v_exp2[(exp1_v_exp2['Session type']=='R1') &
                                               (exp1_v_exp2['Timing of ABA']=='Before ABA')]['Full name'].to_list()
        option['Group 2 videos'] = exp1_v_exp2[(exp1_v_exp2['Session type']=='R1') &
                                               (exp1_v_exp2['Timing of ABA']=='After ABA') ]['Full name'].to_list()
        option['Group 1 name']   = 'Within R1, Before ABA'
        option['Group 2 name']   = 'Within R1, After ABA'
        options += [option]
        
        graph_no = 0
        
        for option in tqdm(options, ncols=70):
            
            graph_no += 1
        
            drop_rows1 = [row for row in all_data.index if row not in option['Group 1 videos']]
            drop_rows2 = [row for row in all_data.index if row not in option['Group 2 videos']]
            df1 = all_data.drop(drop_rows1)
            df2 = all_data.drop(drop_rows2)
            
            # Apply the log transformations.
            df1_means = df1.mean()
            df2_means = df2.mean()
            comparison = pd.Series(zip(df1_means, df2_means), index=df1_means.index)
            def divide_tuples(tuple1):
                if pd.isna(tuple1[0]) or pd.isna(tuple1[1]):
                    return(np.nan)
                elif tuple1[0] == 0 or tuple1[1] == 0:
                    return(np.nan)
                else:
                    return(tuple1[0]/tuple1[1])
            comparison = comparison.apply(divide_tuples)
            def nat_log(value):
                if pd.isna(value):
                    return(np.nan)
                else:
                    return(np.log(value))
            comparison = comparison.apply(nat_log)
            
            # Unstack the data in the format for the heatmaps.
            new_columns = [(item.split(',')[0], item.split(',')[1]) 
                           for item in list(comparison.index)]
            comparison.index = pd.MultiIndex.from_tuples(new_columns)
            comparison = comparison.unstack()
            
            # Order the rows by time bins.
            comparison.index = comparison.index.astype(float).astype(int)
            comparison = comparison.sort_index().T
            comparison.index.name = "Behaviours"
            comparison.columns.name = "Time bins (mins)"
            
            # plt.figure(figsize=(20,5), dpi=300)
            if type_stat == 'Time spent doing behaviour/total time':
                axis_limit = 1.75
            elif type_stat == 'Average bout lengths (secs)':
                axis_limit = 1      
            plt.figure(figsize=(12,3), dpi=300)
            g = sns.heatmap(comparison, cmap='bwr', vmin=-axis_limit, vmax=axis_limit)
            g.set_facecolor('gray')
        
            plt.title('Graph number: '+str(graph_no)+'\n'+
                      'Statistic: '+type_stat+'\n'+
                      'Dataset: '+dataset_option+'\n'+
                      'Groups: '+option['Group 1 name']+' vs '+option['Group 2 name']+'\n')
            rc('xtick', labelsize=7) 
            #plt.tight_layout()
            
            export_name_plots = ('Graph '+str(graph_no)+' '+
                                 option['Group 1 name']+' vs '+option['Group 2 name']+'.png')
            export_fig = os.path.join(export_location, export_name_plots)
            plt.savefig(export_fig, bbox_inches='tight', pad_inches=0.2)

            # Save the raw data.
            export_name_data = ('Graph '+str(graph_no)+' '+
                                option['Group 1 name']+' vs '+option['Group 2 name']+'.xlsx')
            export_data = os.path.join(export_location, export_name_data)
            comparison.to_excel(export_data)
            
            plt.close()
            
if __name__ == "__main__":
    
    create_spider_plots(import_location)
    create_time_bin_plots(import_location)
