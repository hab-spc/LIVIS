#!/usr/bin/env bash

# This script lives in the server ar data6/phytoplankton-db/hab_invitro/LIVIS_automate

# Step 2
# Using SPC Convert
root="/data6/phytoplankton-db/hab_in_vitro"
cd "$root/LIVIS_automate/SPCConvert"

date=$1
source activate hab_env
img_dir="$root/images/$date" # test img_dir
python spcconvert.py $img_dir

# Step 3
# Deploy classifier
cd "$root/LIVIS_automate/hab-ml/"
deploy_data="$root/images/$date"
deploy_data="$img_dir" # test deploy data
model_dir='/data6/lekevin/hab-master/hab-spc/experiments/proro_run'
python main.py --mode deploy --batch_size 16 --deploy_data $deploy_data --model_dir $model_dir --lab_config

# Step 4
cd "$root/LIVIS_automate/SPCConvert"
html_dir="$root/images/${date}_static_html"
url="$html_dir/spcdata.html"
pred="$html_dir/predictions.json"
python addPredictions.py $url $pred
echo Predictions updated on html!
