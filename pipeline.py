"""Pipeline Initialization for HAB-ML on Lab Deployment"""
# Standard dist imports
import argparse
from datetime import datetime
import logging
import os

# Project level imports
from config.config import opt
from constants.genericconstants import DBConstants as DBCONST
from data_preprocess.spc import batchprocess
from database.db_util import pull_data
from hab_ml.utils.constants import Constants as MLCONST

# Third party imports

# Module level constants

def main(date=None, filtered_pull=False, run_app=None):
    if filtered_pull and date:
        pip = Pipeline()
        pip.filtered_pull(date=date)

    elif date:
        pip = Pipeline()
        pip.process(date)
        pip.predict(date)

    elif run_app:
        pip = Pipeline()
        pip.run_app()

class Pipeline():
    """Pipeline Instance for HAB-ML

    Operations consist of the following:
        - processing binary image files from the lab-camera
        - running predictions on the converted image
        - updating the internal database with the predictions

    """

    def __init__(self):
        pass

    def predict(self, date, gpu=0):
        """Run model prediction"""
        hab_ml_main = opt.hab_ml_main.format('main.py')
        data_dir = os.path.join(opt.data_dir.format(date),'00000')
        model_dir = opt.model_dir
        cmd = "CUDA_VISIBLE_DEVICES={} python {} --mode deploy --batch_size 16 --deploy_data {} --model_dir {} --lab_config --log2file"
        cmd = cmd.format(gpu, hab_ml_main, data_dir, model_dir)
        os.system(cmd)

    def process(self, date):
        """
        Process binary files (not to be confused with model preprocessing)
        :param date: the date for which data is being processed
        :param root: path to the tar files to be processed
        """

        img_dir = opt.data_dir.format(date)
        print(img_dir)

        if not (os.path.isdir(img_dir)):
            print("Please input a directory of data directories, aborting.")

        else:
            # Step 1
            # Uncompress all tar files and join into one folder
            # print("Uncompressing tar files")
            # extracted_path = os.path.join(img_dir, '00000')
            # for file in os.path.join(img_dir, glob.glob('*.tar')):
            #     with tarfile.open(file) as archive:
            #         archive.extractall(path=extracted_path)
            #         os.remove(file)
            # img_dir = extracted_path
            #
            # os.mkdir(os.path.join(img_dir, '00000'))
            # for file in os.path.join(img_dir, '00000', glob.glob('*')):
            #     shutil.copy(os.path.join(file, glob.glob('*')), os.path.join(img_dir, '00000'))

            # Step 2
            # Convert images using batchprocess in SPC
            batchprocess(os.path.join(img_dir, '00000'))

    def filtered_pull(self, date, hab_eval=True):
        logger = logging.getLogger('filtered_pull')

        sample_id = '001'
        if sample_id in date:
            date = date.split('/')[0]

        expected_fmt = '%Y%m%d'
        if date != datetime.strptime(date, expected_fmt).strftime(expected_fmt):
            raise ValueError(f"time data '{date}' does not match format '{expected_fmt}'")

        data = pull_data(image_date=date, filtered_size=True, save=False)
        if hab_eval:
            data = Pipeline()._reformat_lab_data(data)
        csv_fname = os.path.join(opt.meta_dir, f'hab_in_vitro_{date}.csv')
        data.to_csv(csv_fname, index=False)
        logger.info(f'Saved dataset as {csv_fname}')

    @staticmethod
    def _reformat_lab_data(data):
        df = data.copy()
        logger = logging.getLogger('_reformat_lab_data')
        logger.debug('Reformatting dataset...\n')
        df = df.rename({DBCONST.IMG_FNAME:MLCONST.IMG}, axis=1)

        hab_species = open('/data6/phytoplankton-db/hab.txt', 'r').read().splitlines()[:-1]

        def label_mapping(x):
            if x in hab_species:
                return x
            else:
                return 'Other'

        df[MLCONST.LABEL] = df[DBCONST.USR_LBLS].apply(label_mapping)
        logger.info(f'HAB Lbl Distribution\n{"-" * 30}\n'
                    f'{df[MLCONST.LABEL].value_counts()}')
        return df


    @staticmethod
    def run_app():
        #TODO @Kush
        #Run the code to activate your application. If shell command, use os.system(cmd)
        cmd = "cd hab-viewer && npm start & cd hab_service & npm start"
        os.system(cmd)


#Main 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=str, help='Format: YYYYMMDD')
    parser.add_argument('--run_app', action='store_true', help='Run annotation tool')
    parser.add_argument('--filtered_pull', action='store_true', help='Pull data')
    args = parser.parse_args()

    main(date=args.date, filtered_pull=args.filtered_pull, run_app=args.run_app)
