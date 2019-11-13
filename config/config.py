""" configuration file to store constants
"""
from __future__ import absolute_import

# Standard dist imports
import os
from pathlib import Path

from constants.genericconstants import DBConstants as DBCONST
# Project level imports
from constants.genericconstants import GenericConstants as CONST

# Module level constants
DEFAULT_ENV = CONST.DEV_ENV
PROJECT_DIR = Path(__file__).resolve().parents[1]

create_table_commands = {
    'livis': 'CREATE TABLE livis ()',
    'date_sampled': f'CREATE TABLE date_sampled ('
    # Image Info
                    f'{DBCONST.IMG_FNAME} TEXT PRIMARY KEY,'
                    f'{DBCONST.IMG_ID} TEXT,'
                    f'{DBCONST.IMG_TSTAMP} TEXT,'
                    f'{DBCONST.IMG_DATE} TEXT,'
                    f'{DBCONST.IMG_TIME} TEXT,'
                    f'{DBCONST.IMG_FSIZE} REAL,'
                    f'{DBCONST.ECCENTRICITY} REAL,'
                    f'{DBCONST.ORIENT} REAL,'
                    f'{DBCONST.MJR_LEN} REAL,'
                    f'{DBCONST.MIN_LEN} REAL,'
                    f'{DBCONST.HEIGHT} REAL,'
                    f'{DBCONST.WIDTH} REAL,'
                    f'{DBCONST.SOLIDITY} REAL,'
                    f'{DBCONST.ASPT_RATIO} REAL,'
                    f'{DBCONST.EST_VOL} REAL,'
                    f'{DBCONST.AREA} REAL,'

    # Machine Learning Info
                    f'{DBCONST.MODEL_NAME} TEXT,'
                    f'{DBCONST.USR_LBLS} TEXT,'
                    f'{DBCONST.PRED} TEXT,'
                    f'{DBCONST.PROB} REAL,'

    # Annotation Info
                    f'{DBCONST.IMG_STATUS} TEXT,'
                    f'{DBCONST.IMG_TAG} TEXT,'
                    f'{DBCONST.ML_LBL} BOOLEAN,'
                    f'{DBCONST.HMN_LBL} BOOLEAN)'
}

insert_into_table_commands = {
    'insert_images': ''' INSERT INTO date_sampled({}) VALUES({})'''.format(DBCONST().image_fields,
                                                                           '?,' * len(DBCONST().image_fields))
}

class Environment():
    def __init__(self, env_type=None):
        if env_type == CONST.DEV_ENV:
            self.models_dir = os.path.join(PROJECT_DIR, 'src/models')
            self.data_dir = os.path.join(PROJECT_DIR, 'src/data')
        elif env_type == CONST.PROD_ENV:
            self.models_dir = 'prod/models'
            self.data_dir = 'prod/data'

class Config(Environment):
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
    NOTE that, config items could be overwriten by passing
    argument `set_config()`. e.g. --voc-data-dir='./data/'
    """
    # Training flags
    log2file = False
    print_freq = 50
    save_freq = 2

    db_path = os.path.join(PROJECT_DIR, 'DB/livis.db')

    def __init__(self, env_type):
        super().__init__(env_type)

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

opt = Config(DEFAULT_ENV)
