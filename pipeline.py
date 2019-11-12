"""Pipeline Initialization for HAB-ML on Lab Deployment"""
# Standard dist imports
import os

# Third party imports

# Project level imports
from config.config import opt
from constants.genericconstants import GenericConstants as CONST
from constants.genericconstants import PipelineConstants as CONST_P

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
        hab_ml_main = os.path.join(os.getcwd(),'hab_ml/main.py')
        img_dir = os.path.join(CONST_P.ROOT, 'images', date)
        model_dir = CONST_P.MODEL_DIR
        cmd = "python $main_path --mode deploy --batch_size 16 --deploy_data $img_dir --model_dir $model_dir --lab_config"
        cmd_dict = {'$main_path':hab_ml_main,'$img_dir':img_dir, '$model_dir': model_dir}
        for key,value in cmd_dict.items():
            cmd = cmd.replace(key,value)
        os.system(cmd)
        

    def process(self):
        """Process binary files (not to be confused with model preprocessing"""
        #TODO @TarujGoyal
        pass

    def update(self):
        """Update the database with the predictions"""
        #TODO @SuryaKrishnan
        pass

