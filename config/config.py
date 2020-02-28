""" configuration file to store constants
"""
from __future__ import absolute_import

# Standard dist imports
from pathlib import Path

# Project level imports
from constants.genericconstants import DBConstants as DBCONST

# Module level constants
PROJECT_DIR = Path(__file__).resolve().parents[1]

create_table_commands = {
    DBCONST.TABLE: f'CREATE TABLE {DBCONST.TABLE} ('
    # Image Info
                   f'{DBCONST.IMG_FNAME} TEXT PRIMARY KEY,'
                    f'{DBCONST.IMG_ID} TEXT,'
                    f'{DBCONST.IMG_TSTAMP} TEXT,'
                    f'{DBCONST.IMG_DATE} TEXT,'
                    f'{DBCONST.ORIENT} REAL,'
                    f'{DBCONST.MJR_LEN} REAL,'
                    f'{DBCONST.MIN_LEN} REAL,'
                    f'{DBCONST.HEIGHT} REAL,'
                    f'{DBCONST.WIDTH} REAL,'
                    f'{DBCONST.ASPT_RATIO} REAL,'
                    f'{DBCONST.AREA} REAL,'

    # Annotation Info
                   f'{DBCONST.IMG_LBL} TEXT)'
}

select_from_table_commands = {
    "select_images":
        '''SELECT * FROM {} WHERE image_date="{}"''',

    "select_images_filtered_size":
        '''SELECT * FROM {} WHERE image_date="{}" and 
        image_major_axis_length <=0.1 and image_major_axis_length >=0.03''',

    "select_all":
        f'''SELECT * FROM {DBCONST.TABLE}'''

}

class Config():
    """Default Configs for training and inference
    After initializing instance of Config, user can import configurations as a
    state dictionary into other files. User can also add additional
    configuration items by initializing them below.
    Example for importing and using `opt`:
    config.py
        >> opt = Config()
    main.py
        >> from config import opt
        >> lr = opt.lr
        
    NOTE: all path related configurations should be set up in the Environment() class above to avoid issues with developing on a person vs production environment.

    """
    # logging
    log2file = False
    MergeSubDirs = False
    ImagesPerDir = 1000
    BayerPattern = "BG"
    UseJpeg = True
    SaveRawColor = True
    PixelSize = 0.62
    MinObjectArea = 100
    ObjectsPerROI = 5
    EdgeThreshold = 2.5
    MinObjectArea = 100
    Deconvolve = True

    DB_PATH = './database/test.db'
    META_DIR = './database/csv'

    def _parse(self, kwargs):
        state_dict = self._state_dict()
        for k, v in kwargs.items():
            if k not in state_dict:
                raise ValueError('UnKnown Option: "--%s"' % k)
            setattr(self, k, v)

        # print('======user config========')
        # pprint(self._state_dict())
        # print('==========end============')

    def _state_dict(self):
        """Return current configuration state
        Allows user to view current state of the configurations
        Example:
        >>  from config import opt
        >> print(opt._state_dict())
        """
        return {k: getattr(self, k) for k, _ in Config.__dict__.items() \
                if not k.startswith('_')}


def set_config(**kwargs):
    """ Set configuration to train/test model
    Able to set configurations dynamically without changing fixed value
    within Config initialization. Keyword arguments in here will overwrite
    preset configurations under `Config()`.
    Example:
    Below is an example for changing the print frequency of the loss and
    accuracy logs.
    >> opt = set_config(print_freq=50) # Default print_freq=10
    >> ...
    >> model, meter = train(trainer=music_trainer, data_loader=data_loader,
                            print_freq=opt.print_freq) # PASSED HERE
    """
    opt._parse(kwargs)
    return opt


opt = Config()
