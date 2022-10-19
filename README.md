# Steps from start to finish for the pose estimation and behavioural clustering analysis in PhenoSys eLife 2022 🐁

## Overview

This repository contains the codes and steps used to analyse the pose estimation and behavioural clustering data and create figures for PhenoSys eLife 2022. <br>
The following files are also needed to follow these steps:
* The example import and export files folder.
* The DeepLabCut project folder, which is used to predict the locations of the rodent body parts over time.
* The B-SOiD project folder, which is used to predict the rodent behaviours over time.

## Installation

### FFMPEG

Follow the steps [here](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/) to install FFMPEG. <br>
This is used for the video pre-processing.

### R

Follow the steps [here](https://github.com/ETHZ-INS/DLCAnalyzer) to install the packages and DLCAnalyzer repository. <br>
I recommend using [RGui](https://cran.r-project.org/bin/windows/base/) for the IDE.
This is used for generating the zone analysis results.

### Python

Follow the steps below to install the packages needed to run these codes. <br>
Most of the analysis and plotting is done in Python. <br>

Install [Anaconda Navigator](https://www.anaconda.com/products/distribution). <br>
Open Anaconda Prompt (on Mac open terminal and install X-Code when prompted). <br>
Download this repository to your home directory by typing in the line below.
```
git clone https://github.com/Foldi-Lab/PhenoSys-data.git
```
Change the directory to the place where the downloaded folder is. <br>
```
cd PhenoSys-data
```

Create a conda environment and install the dependencies.
```
conda env create -n PSD -f Python_dependencies.yaml
```

Change the directory to the place where the are.
```
cd PhenoSys-data/Codes
```

Activate the conda environment.
```
conda activate PSD
```

Edit and run whichever codes you want to.
```
python Step_5_Prepare_zone_data_for_analysis.py
python Step_7_Add_row_info.py
python Step_8_Prepare_tracking_data_for_behavioural_clustering.py
python Step_10_Prepare_behavioural_data_for_plotting.py
python Step_11_Create_spider_plots_and_time_bin_heatmaps.py
```

## Using the codes

Set the import_location in these codes to the example import and export files folder. <br>
The top of each code will also show which files are used.
Click here to see a new guide 

### Acknowledgements

__Author:__ <br>
[Harry Dempsey](https://github.com/H-Dempsey) (Andrews lab and Foldi lab) <br>

__Credits:__ <br>
Laura Milton, Stephen Power, Claire Foldi, Zane Andrews, Karsten Krepinsky, Sarah Lockie, Kaixin Huang, Kyna Conn, Amelia Trice, Sheida Shadani <br>

__About the labs:__ <br>
The [Foldi lab](https://www.monash.edu/discovery-institute/foldi-lab) investigates the biological underpinnings of anorexia nervosa and feeding disorders. <br>
The [Andrews lab](https://www.monash.edu/discovery-institute/andrews-lab) investigates how the brain senses and responds to hunger. <br>
