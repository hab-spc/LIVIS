"""Pipeline Initialization for HAB-ML on Lab Deployment"""
# Standard dist imports
import argparse
import os

# Project level imports
from config.config import opt
from data_preprocess.spc import batchprocess

# Third party imports

# Module level constants

parser = argparse.ArgumentParser()
parser.add_argument('--date', type=str, help='Format: YYYYMMDD')
parser.add_argument('--run_app', action='store_true', help='Run annotation tool')
args = parser.parse_args()


def main(date=None, run_app=None):
    if date:
        pip = Pipeline()
        pip.process(date)
        pip.predict(date)

    if run_app:
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

    def predict(self, date):
        """Run model prediction"""
        hab_ml_main = opt.hab_ml_main.format('main.py')
        data_dir = os.path.join(opt.data_dir.format(date),'00000')
        model_dir = opt.model_dir
        cmd = "python {} --mode deploy --batch_size 16 --deploy_data {} --model_dir {} --lab_config"
        cmd = cmd.format(hab_ml_main, data_dir, model_dir)
        os.system(cmd)

    def process(self, date):
        """
        Process binary files (not to be confused with model preprocessing)
        :param date: the date for which data is being processed
        :param root: path to the tar files to be processed
        """

        img_dir = opt.data_dir.format(date)
        print(img_dir)
        print("KEVINS TEST")

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

    def update(self):
        """Update the database with the predictions"""
        # TODO @SuryaKrishnan
        pass

    @staticmethod
    def run_app():
        #TODO @Kush
        #Run the code to activate your application. If shell command, use os.system(cmd)
        cmd = "cd hab-viewer && npm start & cd hab_service & npm start"
        os.system(cmd)


#Main 
if __name__ == '__main__':
    main(date=args.date, run_app=args.run_app)
