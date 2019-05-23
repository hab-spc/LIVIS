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
user=odroid
host=192.168.1.110
echo Logging into odroid remote server
source_dir="LIVIS/LIVIS_automate"
data_dir=$(ssh $user@$host "cd $source_dir;./run_livis.sh $date")

# Download to local directory
ID=~/.ssh/id_rsa
scp -ri $ID $user@$host:$data_dir $source_path

# Uncompress tar file
source_path="$source_path/0000000000"
tar -xvf "${source_path}.tar"

# ****************************************************************************

# Prerepare remote data storage location
ssh_key="plankton@gpu6"
svcl_dir="/data6/phytoplankton-db/hab_in_vitro"
img_dir="$svcl_dir/images/$date/"
dest_path="$ssh_key:$img_dir"

# Upload images to remote server
ssh $ssh_key "mkdir -p $img_dir"
scp -r $source_path $dest_path

# ****************************************************************************

# Run `auto_script` on remote server to convert images and get predictions
cd_dir="cd $svcl_dir/LIVIS_automate"
activate_env="source activate hab_env"
deploy="bash deploy_remote.sh $date"
echo Deploying classification
ssh plankton@gpu6 "$cd_dir;$activate_env;$deploy"
