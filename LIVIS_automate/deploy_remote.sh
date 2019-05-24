#!/usr/bin/env bash

# This script lives in the server ar data6/phytoplankton-db/hab_invitro/LIVIS_automate

# Step 2
# Using SPC Convert
root="/data6/phytoplankton-db/hab_in_vitro"

# Receive data folder
date=$1
source activate hab_env
img_dir="$root/images/$date" # test img_dir

# Uncompress all tar files and join into one folder
cd "$img_dir"
for i in *.tar;do tar -xvf $i && rm $i; done
mkdir "$img_dir/00000"
for d in $img_dir/000000*; do cp -r $d/* "$img_dir/00000/"; rm -rf $d; done

cd "$root/LIVIS_automate/SPCConvert"
python spcconvert.py "$img_dir/00000"

# Step 3
# Deploy classifier
cd "$root/LIVIS_automate/hab-ml/"
deploy_data="$root/images/$date/00000"
model_dir='/data6/lekevin/hab-master/hab-spc/experiments/proro_run'
python main.py --mode deploy --batch_size 16 --deploy_data $deploy_data --model_dir $model_dir --lab_config

# Step 4
cd "$root/LIVIS_automate/SPCConvert"
html_dir="$root/images/${date}/00000_static_html"
url="$html_dir/spcdata.html"
pred="$html_dir/predictions.json"
python addPredictions.py $url $pred

