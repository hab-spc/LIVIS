#!/usr/bin/env bash
# This is the set of commands to execute on the local machine for:
# 1. Transfer the .tif images from the local machine to a folder in SVCL server
# 2. Convert images using spcconvert and deploy model
# 3. Upload predictions to static html

# ****************************************************************************

# Step 1
# We transfer the images on the local machine to the SVCL Server using scp command
# Change the paths accordingly:

#-- prompt for subdirectory name to save data to on local machine
echo "Enter new data directory name to store on remote machine, followed by [ENTER]: "
read date

#--
#open -a coRD
#open 'smb://spcuser:odroid@192.168.1.110'
#echo Select `data` directory when mounting and proceed to run camera system

# include into this script ./run_camera.sh upon command
# put watchdog on the data directory for the latest one after running camera
# upload those images to the server
# once imaging is done, run classifier upon yes command

local_dir="/Users/ktl014/PycharmProjects/hab-master/LIVIS/images"
source_path="$local_dir/$date/*"

ssh_key="plankton@gpu6"
svcl_dir="/data6/phytoplankton-db/hab_in_vitro"
img_dir="$svcl_dir/images/$date/"
dest_path="$ssh_key:$img_dir"

# Upload images
ssh $ssh_key "mkdir -p $img_dir"
scp -r $source_path $dest_path

# ****************************************************************************

# Step 2
# Run `auto_script` on remote server to convert images and get predictions
cd_dir="cd $svcl_dir/LIVIS_automate"
activate_env="source activate hab_env"
deploy="bash deploy_remote.sh $date"
echo Deploying classification
ssh plankton@gpu6 "$cd_dir;$activate_env;$deploy"

# ****************************************************************************

# Step 3
# Upload predictions to static html