"""Pipeline Initialization for HAB-ML on Lab Deployment"""
# Standard dist imports

# Third party imports

# Project level imports
from config.config import opt
from constants.genericconstants import GenericConstants as CONST

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

    def process(self):
        """Process binary files (not to be confused with model preprocessing"""
        #TODO @TarujGoyal
        pass

    def update(self):
        """Update the database with the predictions"""
        #TODO @SuryaKrishnan
        pass

