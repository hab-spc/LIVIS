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
ssh odroid@192.168.1.110 "./run_livis.sh $date"

# ****************************************************************************

# Prerepare remote data storage location
ssh_key="plankton@gpu6"
svcl_dir="/data6/phytoplankton-db/hab_in_vitro"
img_dir="$svcl_dir/images/$date/"
dest_path="$ssh_key:$img_dir"

# Upload images to remote server
source_path = "$source_path/0000000000"
ssh $ssh_key "mkdir -p $img_dir"
scp -r $source_path $dest_path

# ****************************************************************************

# Run `auto_script` on remote server to convert images and get predictions
cd_dir="cd $svcl_dir/LIVIS_automate"
activate_env="source activate hab_env"
deploy="bash deploy_remote.sh $date"
echo Deploying classification
ssh plankton@gpu6 "$cd_dir;$activate_env;$deploy"
