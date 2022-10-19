# CHOOSE THE LOCATION OF THE LIST OF PATHS FOR ZONE ANALYSIS AND EXPORT DESTINATION.
# USE THESE EXAMPLE FILES:
# List paths for zone analysis.csv
# Zone results.csv
list_path_zone_analysis <- "C:/Users/hazza/Desktop/DeepLabCut/Codes/All together/Example run/List paths for zone analysis.csv"
export_file <- "C:/Users/hazza/Desktop/DeepLabCut/Codes/All together/Example run/Zone results.csv"

# ENSURE THE FOLLOWING PACKAGES AND REPOSITORY ARE INSTALLED.
# Here are the instructions: https://github.com/ETHZ-INS/DLCAnalyzer
library(sp)         #tested with v1.3-2
library(imputeTS)   #tested with v3.0
library(ggplot2)    #tested with v3.1.0
library(ggmap)      #tested with v3.0.0
library(data.table) #tested with v1.12.8
library(cowplot)    #tested with v0.9.4
library(corrplot)   #tested with v0.84

# CHANGE THE DIRECTORY TO THE DLCANALYZER FOLDER.
setwd("C:/Users/hazza/DLCAnalyzer-master")
source('R/DLCAnalyzer_Functions_final.R')

# RUN THE ANALYSIS.
paths_list <- read.table(list_path_zone_analysis, sep = ",", header = T)
length_list = dim(paths_list)[1]

for (x in 1:length_list) {
    
  path1 = paths_list[x,1]
  path2 = paths_list[x,2]
  path3 = paths_list[x,3]
  path4 = paths_list[x,4]

  # Create path variables

  # Import the excel session data from DeepLabCut.
  Tracking <- ReadDLCDataFromCSV(path1, fps = 30)

  # Make the distance between the bottom 2 ends of the test wall 22 cm.
  Tracking <- CalibrateTrackingData(Tracking, method = "distance", in.metric = 22, points = c("TBwall_bottom","ETwall_bottom"))

  # Import the data about the points in the arena that make up each zone.
  zoneinfo <- read.table(path2, sep = ",", header = T)
  Tracking <- AddZones(Tracking,zoneinfo)

  # Plot the zones, so I can check them.
  png(filename=path3)
  print(PlotZones(Tracking))
  dev.off()

  # Create a column with the zone information for a given point on the mouse.
  key_point = "Nose_point"
  Tracking <- CalculateMovement(Tracking, movement_cutoff = 5, integration_period = 5)
  zonenames <- list("arena", "pellet_dispenser", "left_image", "right_image", "escape_hole", "floor", "pellet_wall", "escape_wall", "test_wall", "blank_wall")
  Report <- ZoneReport(Tracking, point = key_point, zones = c("arena"), zone.name = "outside", invert = TRUE)
  column <- t(data.frame(Report))
  colnames(column) <- c(path4)
  for (zone in zonenames) {
    Report <- ZoneReport(Tracking, point = key_point, zones = zone)
    column <- rbind(column, t(data.frame(Report)))
  }

  # Add this column to a master file.
  if (x == 1) {
    master <- column
  } else {
    master <- cbind(master, column)
  }

}

# Export the data.
write.csv(master, export_file, row.names = TRUE)
