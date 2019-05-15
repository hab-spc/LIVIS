#!/usr/bin/env bash

# This script lives in the server ar data6/phytoplankton-db/hab_invitro/LIVIS_automate

# Step 2
# Using SPC Convert
root="/data6/phytoplankton-db/hab_invitro"
cd "$root/LIVIS_automate/SPCConvert"

img_dir="$root/images/20190515"
python spcconvert.py $img_dir

# Step 3
# Deploy classifier
cd "$root/LIVIS_automate/hab-ml/"
deploy_data="$root/images/20190515"
model_dir='/data6/lekevin/hab-master/hab-spc/experiments/proro_run'
source activate hab_env
python main.py --mode deploy --batch_size 16 --deploy_data $deploy_data --model_dir $model_dir

