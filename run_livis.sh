#!/usr/bin/env bash

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

echo Uploading images to svcl server

# Navigate to latest generated image dir
samba_data_dir="/Volumes/data/*/"
source_path="$(ls -td -- $samba_data_dir | head -1)"
#TODO try and catch to verify if volume is mounted

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

# Run predictions
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

# View images to annotate or visualize
read -p "View Collected Images [y/n]: " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    #TODO instantiate the tunneing heere
fi