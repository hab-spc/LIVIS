#!/usr/bin/env bash
# This is the set of commands to execute on the local machine for:
# 1. Transfer the .tif images from the local machine to a folder in SVCL server
# 2. Convert images using spcconvert and deploy model
# 3. Upload predictions to static html

# ****************************************************************************

# Step 1
# We transfer the images on the local machine to the SVCL Server using scp command
# Change the paths accordingly:
source_path="/Users/ktl014/PycharmProjects/hab-master/LIVIS/LIVIS_automate/sampleImgs"
ssh_key="plankton@gpu6"
svcl_dir="/data6/phytoplankton-db/hab_invitro"
img_dir="$svcl_dir/images/20190515/"
dest_path="$ssh_key:$img_dir"

scp -r $source_path $dest_path

# ****************************************************************************

# Step 2
# Run `auto_script` on remote server to convert images and get predictions
cd_dir="cd $svcl_dir/LIVIS_automate"
activate_env="source activate hab_env"
deploy="bash deploy_remote.sh"
echo Deploying classification
ssh plankton@gpu6 "$cd_dir;$activate_env;$deploy"

# ****************************************************************************

# Step 3
# Upload predictions to static html