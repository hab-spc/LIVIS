"""Pipeline Initialization for HAB-ML on Lab Deployment"""
# Standard dist imports
import argparse
from datetime import datetime
import logging
import os

# Project level imports
from config.config import opt
from constants.genericconstants import DBConstants as DBCONST
from database.db_util import pull_data, insert_db

# Third party imports
import pandas as pd

# Module level constants
DB_PATH = 'database/image.db'

def main(args):
    pip = Pipeline()

    if args.pull:
        pip.pull(db_path=args.pull)

    elif args.push:
        pip.push(db_path=args.push)

    elif args.run_app:
        pip.run_app()

class Pipeline():
    """"""
    def push(self, db_path):
        """Push data into database"""
        # Get images
        import glob
        images = glob.glob(
            "/Users/ktl014/PycharmProjects/spc_annotation_tool/images/test_001"
            "/001/00000_processed/images/00000/*")
        images = [img for img in images if img.endswith('-.jpeg')]
        data_dict = {"image_id": [], "image_filename": [], "image_date":[]}
        for img in images:
            data_dict["image_id"].append(os.path.basename(img).replace('.jpeg',''))
            data_dict["image_filename"].append(img)
            data_dict["image_date"].append("2020-02-27")

        # Insert into database
        df = pd.DataFrame.from_dict(data_dict)
        db_path = db_path if db_path else opt.DB_PATH
        insert_db(df, db_path=db_path, table_name=DBCONST.TABLE)

    def pull(self, db_path):
        """Pull images from sql database"""
        logger = logging.getLogger(__name__)
        db_path = db_path if db_path else opt.DB_PATH
        logger.info(f'Pulling data from {db_path}')
        date = datetime.now().strftime("%Y%m%d")
        data = pull_data(db_path=db_path, image_date=date, all=True, filtered_size=True)

        csv_fname = os.path.join(opt.META_DIR, f'seascape_{date}.csv')
        data.to_csv(csv_fname, index=False)
        logger.info(f'Saved dataset as {csv_fname}')

    @staticmethod
    def run_app():
        #Run the code to activate your application. If shell command, use os.system(cmd)
        cmd = "cd hab-viewer && npm start & cd hab_service && npm start"
        os.system(cmd)

#Main 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--push', type=str, default=None, help='Push data into database')
    parser.add_argument('--pull', type=str, default=None, help='Pull data from database')
    parser.add_argument('--run_app', action='store_true', help='Run annotation tool')

    args = parser.parse_args()

    main(args)
