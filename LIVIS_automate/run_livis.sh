#!/usr/bin/env bash

source_dir="/home/odroid"
sh $source_dir/run_camera

# Source directory
source_path=$(ls -td -- $source_dir/data/*/ | head -1)

echo "Enter date and sample run for data storage location, followed by [ENTER]:"
read date

ssh_key="plankton@gpu6"
svcl_dir="/data6/phytoplankton-db/hab_in_vitro"
img_dir="$svcl_dir/images/$date/"
dest_path="$ssh_key:$img_dir"

# Upload images
ssh $ssh_key "mkdir -p $img_dir"
scp -r $source_path $dest_path