### Data and codes for PhenoSys paper

__Codes for pose estimation__

This folder contains the codes used to analyse the data from DeepLabCut and B-SOiD and also generate the pose estimation/behavioural clustering figures.

__Raw data for figures__

This folder contains the raw data used to plot each figure.

### Steps for analysis

__Step 1__

Snip the whole experiment videos into videos for each session.
The steps for doing this can be found here: https://github.com/Foldi-Lab/PhenoSys-codes

__Step 2__

Crop videos to 960x720, sharpen blurry videos, downsample everything to 576x432 and converted to the .mp4 file format. Videos that had black frames, frozen frames, the mouse was completely absent, the pellet magazine was covered, there was high glare or the video was corrupted were excluded.

__Step 3__

Run the videos through [DeepLabCut](https://github.com/DeepLabCut/DeepLabCut) and apply a median filter to this data with default settings.
Our DeepLabCut project folder can be found here.

__Step 4__

Record the coordinates of the vertices for the pellet magazine, images/screens and the arena using the DeepLabCut labelling interface.

__Step 5__

Prepare the tracking data to be analysed:
__Step 5.1__
* In the median-filtered tracking data, make the rows that have a centre-point likelihood drop below 0.05 blank.
__Step 5.2__
* Add the vertices of the magainze, images, etc. from step 4 to the tracking data.
__Step 5.3__
* Create a file with the vertex names in clockwise order.

