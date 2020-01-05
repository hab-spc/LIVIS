#!/usr/bin/env bash
# This is the set of commands to execute on the local lab machine for:
# 0. Run image sampling on odroid virtual machine
# 1. Transfer the .tif images from the local machine to a folder in SVCL server
# 2. Convert images using spcconvert
# 3. Deploy model
# 4. Upload predictions to static html
# 5. Retrieve predicted images back to lab computer

# NOTE: Steps 2-4 occurs on the SVCL server, hence the `deploy_remote.sh`
# Step 0
# ****************************************************************************

echo "Enter date and sample run for data storage location, followed by [ENTER]:"
read date

# Ssh into camera virtual machine (odroid) and runs the imaging
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
# Step 1
# ****************************************************************************
echo Uploading images to svcl server

# Navigate to latest generated image dir
samba_data_dir="/Volumes/data/*/"
source_path="$(ls -td -- $samba_data_dir | head -1)"
#source_path=/Volumes/data/1558641021/ #DEBUG purposes

# Prepare remote data storage location
ssh_key="plankton@gpu3"
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

# Step 2-4
# ****************************************************************************

# Run `auto_script` on remote server to convert images and get predictions
# expects $date of format `20190523/001`. No 0000000s accompanied.

read -p "Run LIVIS Deployment? [y/n]: " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    cd_dir="cd $svcl_dir"
    activate_env="source activate hab_env"
    deploy="python pipeline.py --date $date"
    echo Deploying classification
    ssh plankton@gpu3 "$cd_dir;$activate_env;$deploy"
fi

read -p "Run LIVIS Annotation? [y/n]: " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    cd_dir="cd $svcl_dir"
    activate_env="source activate hab_env"
    deploy="python pipeline.py --run_app"
    echo Starting Annotation tool
    ssh plankton@gpu3 "$cd_dir;$activate_env;$deploy"
fi