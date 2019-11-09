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
from spc import batchprocess

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

    def predict(self):
        """Run model prediction"""
        #TODO @ZhouyuanYuan
        pass

    def process(self, date, root="/data6/phytoplankton-db/hab_in_vitro"):
        """
        Process binary files (not to be confused with model preprocessing)
        :param date: the date for which data is being processed
        :param root: path to the tar files to be processed
        """

        img_dir = os.path.join(root, 'images', date)
                
        if not(os.path.isfile(img_dir)):
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
            spc.batchprocess(os.path.join(img_dir, '00000'))

    def update(self):
        """Update the database with the predictions"""
        #TODO @SuryaKrishnan
        pass

