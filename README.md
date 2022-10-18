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
