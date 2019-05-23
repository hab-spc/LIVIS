#!/usr/bin/env bash

date=$1

source_path="/home/odroid"
cd ~
sh run_camera

# Source directory
#source_path="$(ls -td -- $source_path/data/*/ | head -1)/0000000000"
source_path="$source_path/data/1558380800/0000000000"
echo "$source_path"