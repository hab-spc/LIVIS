from collections import OrderedDict

class GenericConstants:
    RAW_DATA = 'raw'
    PROCESSED_DATA = 'processed'
    CURRENT_ENV = 'current_environment'
    DEV_ENV = 'dev_mac'
    PROD_ENV = 'prod_env'
    LIVIS = 'livis'

class DBConstants:
    TABLE = 'seascape_table'

    pre = 'image_'
    # Image Info
    IMG_FNAME = pre + 'filename'
    IMG_ID = pre + 'id'
    IMG_TSTAMP = pre + 'timestamp'
    IMG_DATE = pre + 'date'
    ORIENT = pre + 'orientation'
    MJR_LEN = pre + 'major_axis_length'
    MIN_LEN = pre + 'minor_axis_length'
    HEIGHT = pre + 'height'
    WIDTH = pre + 'width'
    ASPT_RATIO = pre + 'aspect_ratio'
    AREA = pre + 'area'

    # Label info
    IMG_LBL = 'ml_user_labels'

    # Unlabeled image name
    IMG_UNLBLED = 'Not labeled'
