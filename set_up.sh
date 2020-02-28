#!/usr/bin/env bash

git submodule update --init --recursive

# create conda environment
conda create -y -n seascape-env
# if first time, need to run conda init --all, exit, and relogin

pip3 install -r requirements.txt

# install node js
conda install -c conda-forge nodejs

# Create database
cd database & python create_db.py --db_path test.db

# Symlink database to hab_service
ln -s database/image.db hab_service/test.db

# Symlink images relative to viewer
ln -s /Users hab-viewer/public/Users

cd hab-viewer & npm install
cd hab-viewer & npm install react-bootstrap-buttons
cd hab-viewer & npm install axios

cd hab_service & npm install
cd hab_service & npm install -g npm@4.6.1
cd hab_service & npm install cors --save
cd hab_service & npm install -g create-react-native-app
cd hab_service & create-react-native-app hab_service



