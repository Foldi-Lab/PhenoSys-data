# Steps from start to finish for the pose estimation and behavioural clustering analysis in PhenoSys eLife 2022 🐁

## Overview

This repository contains the codes and steps used to analyse the pose estimation and behavioural clustering data and create figures for PhenoSys eLife 2022. <br>
The following files are also needed to follow these steps:
* The example import and export files folder.
* The DeepLabCut project folder, which is used to predict the locations of the rodent body parts over time.
* The B-SOiD project folder, which is used to predict the rodent behaviours over time.

## Installation

## Using the codes

Set the import_location in these codes to the example import and export files folder. <br>
The top of each code will also show which files are used.

## Steps for analysis

### Pre-processing

__Step 1__

Snip the whole experiment videos into videos for each session.
The steps for doing this can be found [here](https://github.com/Foldi-Lab/PhenoSys-codes):

__Step 2__

Crop videos to 960x720, sharpen blurry videos, downsample everything to 576x432 and converted to the .mp4 file format. Videos that had black frames, frozen frames, the mouse was completely absent, the pellet magazine was covered, there was high glare or the video was corrupted were excluded.

### Zone analysis

__Step 3__

Run the videos through [DeepLabCut](https://github.com/DeepLabCut/DeepLabCut) and apply a median filter to this data with default settings.
Our DeepLabCut project folder can be found here.

__Step 4__

Record the coordinates of the vertices for the pellet magazine, images/screens and the arena using the DeepLabCut labelling interface. Store this in an excel file.

__Step 5__

Prepare the tracking data to be analysed:
* In the median-filtered tracking data, make the rows that have a centre-point likelihood drop below 0.05 blank.
* Add the vertices of the magainze, images, etc. from step 4 to the tracking data.
* Create a file with the vertex names in clockwise order.

__Step 6__

Analyse the tracking data for time spent in zones.

__Step 7__

Add row labels to these zone results.

### Behavioural analysis

__Step 8__

Prepare the tracking data to be analysed for Behaviours.
* In the non-filtered data, remove the rows that have the centre-point likelihood drop below 0.05 (rather than make blank).
* Find which files become empty after this, and remove these.
* Reset the frame numbers, so they are 0, 1, 2, ...
* Combine CSVs so they are importable in B-SOiD. CSVs need to be imported one at a time, so this makes it easier to select a large dataset.

__Step 9__

Use the combined CSVs as training data in [B-SOiD](https://github.com/YttriLab/B-SOID).
Once the model is trained, analyse the tracking data before combining.
Export the "bout_lengths" and "labels_pose" data types.
Our B-SOiD project folder can be found here.

__Step 10__

Prepare the behavioural data for plotting.
* Find the time spent doing each behaviour.
* Find the time spent doing each behaviour per time bin. Make sure to add the missing data (when the centre point likelihood drops below 0.05) back to these files.

__Step 11__

Create plots:
* Spider plots about the proportion of time spent doing behaviours across each video.
* Time bin heat maps about the proportion of time spent doing behaviours within video time bins.
