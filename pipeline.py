"""Pipeline Initialization for HAB-ML on Lab Deployment"""
# Standard dist imports
import os
import tarfile
import glob
import shutil
import sys
from pathlib import Path

# Third party imports

# Project level imports
from config.config import opt
from constants.genericconstants import GenericConstants as CONST
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

        if not (os.path.isdir(img_dir)):
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

    def run_app(self):
        #TODO @Kush
        #Run the code to activate your application. If shell command, use os.system(cmd)
        pass
    

#Main 
if __name__ == '__main__':
    # This is the set of commands to execute on the local lab machine for:
    # 0. Run image sampling on odroid virtual machine
    # 1. Transfer the .tif images from the local machine to a folder in SVCL server
    # 2. Convert images using spcconvert
    # 3. Deploy model
    # 4. Upload predictions to static html
    # 5. Open Annotation tool

    run_app = (input('Run images sampling? \n [Enter y to run images sampling or model deploy. Enter n to open annotation tool.] \n').lower()).strip()
    if run_app == 'y':
        # Step 0
        date = input('Enter date and sample run for data storage location, followed by [ENTER]:\n')
        run_images = (input('Run LIVIS Imaging? [y/n]: \n').lower()).strip()

        # Ssh into camera virtual machine (odroid) and runs the imaging
        if run_images == 'y':
            user = 'odroid'
            host = '192.168.1.110'
            print('Looging into odroid remote server')
            source_dir='LIVIS/LIVIS_automate'
            cmd = 'ssh {}@{} \"cd {};./run_livis.sh {}\" '
            cmd = cmd.format(user,host,source_dir,date)
            os.system(cmd)

        # Step 1
        print('Uploading images to svcl server')

        # Navigate to latest generated image dir
        samba_data_dir="/Volumes/data/*/"
        source_path=max(glob.glob(samba_data_dir, key=os.path.getmtime))

        # Prepare remote data storage location
        ssh_key="plankton@gpu2"
        dest_path="{}:{}"
        dest_path=dest_path.format(ssh_key, opt.data_dir.format(date))

        if len(os.listdir(source_path) ) == 0:
            print("Images not found in {}. Check if images were taken".format(source_path))
            sys.exit()

        # Upload images to remote server
        cmd='ssh {} \"mkdir -p {}\" '
        cmd=cmd.format(ssh_key, opt.data_dir.format(date))
        os.system(cmd)
        cmd='scp -r {} {}'
        cmd=cmd.format(os.path.join(source_path,'*/'),dest_path)
        os.system(cmd)

        #Step 2-4
        run_livis = (input('Run LIVIS Deployment? [y/n]\n').lower()).strip()
        if run_livis == 'y':
            print('Deploying model')
            os.system(("ssh {}".format(ssh_key)))
            os.system("source activate hab_env")
            pip = Pipeline()
            pip.process(date)
            pip.predict(date)
                    
    #Step 5
    else:
        ssh_key="plankton@gpu2"
        os.system(("ssh {}".format(ssh_key)))
        pip = Pipeline()
        pip.run_app()
    
        

        