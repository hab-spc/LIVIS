#!/usr/bin/env bash

date=$1

source_path="/home/odroid"
cd source_dir
sh run_camera

# Source directory
#source_path="$(ls -td -- $source_path/data/*/ | head -1)/0000000000"
source_path="$source_path/data/1558380800/0000000000"

# Uncompress tar file
tar -xvf "${source_path}.tar"

# Upload images
dest_path="/Users/spcuser/Documents/$date"
scp -r $source_path $dest_path