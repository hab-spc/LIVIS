#!/usr/bin/env bash
# This is the set of commands to execute on the local machine for:
# 1. Transfer the .tif images from the local machine to a folder in SVCL server
# 2. Convert images using spcconvert and deploy model
# 3. Upload predictions to static html

# ****************************************************************************

echo "Enter date and sample run for data storage location, followed by [ENTER]:"
read date

# Make data storage location
#source_path="/Users/ktl014/PycharmProjects/hab-master/LIVIS/images"
source_path="/Users/spcuser/Documents"
source_path="$source_path/$date"
mkdir -p $source_path

# Run camera
read -p "Run LIVIS Imaging? [y/n]: " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    user=odroid
    host=192.168.1.110
    echo Logging into odroid remote server
    source_dir="LIVIS/LIVIS_automate"
    ssh $user@$host "cd $source_dir;./run_livis.sh $date"
fi

source_path="$(ls -td -- /Volumes/data/*/ | head -1)"
#source_path=/Volumes/data/1558641021/
# ****************************************************************************
echo Uploading images to svcl server

# Prepare remote data storage location
ssh_key="plankton@gpu2"
svcl_dir="/data6/phytoplankton-db/hab_in_vitro"
img_dir="$svcl_dir/images/$date"
dest_path="$ssh_key:$img_dir"

if [ -z "$(ls -A $source_path)" ]; then
	echo "Images not found in $source_path. Check if images were taken"
	exit 0
fi	

# Upload images to remote server
ssh $ssh_key "mkdir -p $img_dir"
scp -r $source_path/* $dest_path

# ****************************************************************************

# Run `auto_script` on remote server to convert images and get predictions
# expects $date of format `20190523/001`. No 0000000s accompanied.

read -p "Run LIVIS Deployment? [y/n]: " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    cd_dir="cd $svcl_dir/LIVIS_automate"
    activate_env="source activate hab_env"
    deploy="bash deploy_remote.sh $date"
    echo Deploying classification
    ssh plankton@gpu2 "$cd_dir;$activate_env;$deploy"
fi

# ****************************************************************************

# Copy back all of the images to the local machine
dest_path="/Volumes/LACIE\ SHARE/$date"
mkdir -p dest_path
scp -r "plankton@gpu2:/data6/phytoplankton-db/hab_in_vitro:images/$date" $dest_path
