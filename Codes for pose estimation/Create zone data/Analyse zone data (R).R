# The instructions are here: https://github.com/ETHZ-INS/DLCAnalyzer
library(sp)         #tested with v1.3-2
library(imputeTS)   #tested with v3.0
library(ggplot2)    #tested with v3.1.0
library(ggmap)      #tested with v3.0.0
library(data.table) #tested with v1.12.8
library(cowplot)    #tested with v0.9.4
library(corrplot)   #tested with v0.84

setwd("C:/Users/hazza/DLCAnalyzer-master")
source('R/DLCAnalyzer_Functions_final.R')

zone_results <- function(list_files_to_analyse) {

  # list_files_to_analyse <- "C:/Users/DLC/Desktop/File path list for R.csv"

  paths_list <- read.table(zone_coordinates_path, sep = ",", header = T)
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
write.csv(master, "C:/Users/DLC/Desktop/All_zone_data_220610.csv", row.names = TRUE)

}




