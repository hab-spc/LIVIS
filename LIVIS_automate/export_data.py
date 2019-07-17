""" Exports and updates meta.csv files

- accepts text file of dates to upload
-


"""
# Standard dist imports
import argparse
import glob
import os
import subprocess

# Third party imports

# Project level imports

# Module level constants
g

# root_dir = '/Volumes/LACIE SHARE/'
source_dir = '/data6/phytoplankton-db/hab_in_vitro/images'
user_ip = 'plankton@gpu2:'
dest_dir = '/data6/phytoplankton-db/hab_in_vitro/images'

start_date = '20190530'
end_date = '20190606'
date_files = sorted(os.listdir(source_dir))
if start_date != end_date:
    desired_dates = date_files[
                    date_files.index(start_date): date_files.index(end_date)+1] # include end date
else:
    desired_dates = list(start_date)

# Append root directory to dates
print('Exporting data for dates: {}'.format(desired_dates))
for date in desired_dates:
    rel_path = '001/00000_static_html'
    source_json = os.path.join(source_dir, date, rel_path, 'pred.json')
    dest_json = os.path.join(user_ip + dest_dir, date, rel_path, 'pred.json')
    subprocess.call(['scp', source_json, dest_json])
