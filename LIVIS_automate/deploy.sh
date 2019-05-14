#!/usr/bin/env bash
# This is the set of commands to execute on the local machine for:
# 1. Transfer the .tif images from the local machine to a folder in SVCL server
# 2. Convert the .tif files into jpeg (into the preferred input type of the classifier) using spcconvert
# 3. Deploy the classifier and Obtain the predictions
# 4. Send the predictions back to SIO server

# ****************************************************************************

# Step 1
# We transfer the images on the local machine to the SVCL Server using scp command
# Change the paths accordingly:
source_path="/Users/ktl014/PycharmProjects/hab-master/LIVIS/LIVIS_automate/sample_imgs"
ssh_key="plankton@gpu6"
svcl_dir="/data6/lekevin/hab-master/LIVIS"
dest_path="$ssh_key:$svcl_dir/LIVIS_automate/test"

scp -r $source_path $dest_path

# ****************************************************************************

# Step 2
#Convert the .tif files into jpeg (into the preferred input type of the classifier) using spcconvert
#Using spc convert on the images uploaded to the server

ssh "plankton@gpu6"
main_dir="$svcl_dir/LIVIS_automate"
cd $main_dir
pwd
# ssh sneha@gpu6 "cd /data6/SnehaKondur/hab-spc/LIVIS_automate/spcvisualizer/spcconvert/; python spcconvert.py /data6/SnehaKondur/hab-spc/LIVIS_automate/spcvisualizer/sampleImgs/sampleImgs"

# THERE SEEMS TO BE AN ERROR IN THE SPCCONVERT - NEED TO SORT IT

# ****************************************************************************

# Step 3
# Deploy the classifier and get the Predictions (TODO)

# ****************************************************************************

# Step 4
# Copy the Predictions file from the server to the local machine using SCP command with source as server and destination on local

#scp -r sneha@gpu6:/data6/SnehaKondur/hab-spc/LIVIS_automate/spcvisualizer/sampleImgs /Users/snehakondur/PycharmProjects/hab-spc

# ****************************************************************************