"""Pipeline Initialization for HAB-ML on Lab Deployment"""
# Standard dist imports
import os
import tarfile
import glob
import shutil

# Third party imports

# Project level imports
from config.config import opt
from constants.genericconstants import GenericConstants as CONST
from constants.genericconstants import PipelineConstants as CONST_P
from data_preprocess.spc import batchprocess


# Module level constants

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
        hab_ml_main = os.path.join(os.getcwd(), 'hab_ml/main.py')
        img_dir = os.path.join(CONST_P.ROOT, 'images', date)
        model_dir = CONST_P.MODEL_DIR
        cmd = "python $main_path --mode deploy --batch_size 16 --deploy_data $img_dir --model_dir $model_dir --lab_config"
        cmd_dict = {'$main_path': hab_ml_main, '$img_dir': img_dir, '$model_dir': model_dir}
        for key, value in cmd_dict.items():
            cmd = cmd.replace(key, value)
        os.system(cmd)

    def process(self, date, root="/data6/phytoplankton-db/hab_in_vitro"):
        """
        Process binary files (not to be confused with model preprocessing)
        :param date: the date for which data is being processed
        :param root: path to the tar files to be processed
        """

        img_dir = os.path.join(root, 'images', date)

        if not (os.path.isfile(img_dir)):
            print("Please input a directory of data directories, aborting.")

        else:
            # Step 1
            # Uncompress all tar files and join into one folder
            print("Uncompressing tar files")
            extracted_path = os.path.join(img_dir, '00000')
            for file in os.path.join(img_dir, glob.glob('*.tar')):
                with tarfile.open(file) as archive:
                    archive.extractall(path=extracted_path)
                    os.remove(file)
            img_dir = extracted_path

            os.mkdir(os.path.join(img_dir, '00000'))
            for file in os.path.join(img_dir, '00000', glob.glob('*')):
                shutil.copy(os.path.join(file, glob.glob('*')), os.path.join(img_dir, '00000'))

            # Step 2
            # Convert images using batchprocess in SPC
            batchprocess(os.path.join(img_dir, '00000'))

    def update(self):
        """Update the database with the predictions"""
        # TODO @SuryaKrishnan
        pass
