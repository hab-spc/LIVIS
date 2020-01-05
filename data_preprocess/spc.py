"""
Filename: spc.py
Authors: Taruj
Description: Takes an image directory and processes a SPC images
"""
from __future__ import print_function, division

# Standard dist imports
import cv2
import os
import glob
import time
import datetime
import math
from multiprocessing import Process, Queue
import multiprocessing
import numpy as np
import pandas
import sqlite3
from tqdm import tqdm

# Third party imports

# Project level imports
from data_preprocess import cvtools
from constants.genericconstants import DBConstants as DBCONST
from config.config import opt


def write_data(output, raw_color, use_jpeg):
    # output_path = os.path.join(output['entry'][DBCONST.IMG_FNAME], output['entry'][DBCONST.IMG_ID])
    output_path = output['entry'][DBCONST.IMG_FNAME][:-4]
    extension = ".jpeg" if use_jpeg else ".png"

    if raw_color:
        cv2.imwrite(os.path.join(output_path + "_rawcolor" + extension), output['features']['rawcolor'])
    cv2.imwrite(os.path.join(output_path + extension), output['features']['image'])
    cv2.imwrite(os.path.join(output_path + "_binary.png"), output['features']['binary'])


def load_data(index, image, image_dir, images_per_dir, bayer_conv):
    absdir = os.path.join(image_dir, str(images_per_dir * int(index / images_per_dir)).zfill(5))

    filename = os.path.basename(image)

    if not os.path.exists(absdir):
        os.makedirs(absdir)

    bundle = {'image_path': image,
              'image': cvtools.import_image(os.path.dirname(image), filename, bayer_pattern=bayer_conv),
              'image_dir': absdir}
    return bundle

def process_image(bundle):
    image_path = bundle['image_path']
    image = bundle['image']
    image_dir = bundle['image_dir']

    filename = os.path.basename(image_path)
    timestamp = 0
    for substr in filename.split('-'):
        try:
            timestamp = int(substr)
            break
        except ValueError:
            pass

    # Check the timestamp range
    if timestamp < 100000 or timestamp > time.time():
        print("" + filename + " strange timestamp.")
        output = {}
        return output

    img_c_8bit = cvtools.convert_to_8bit(image)

    # Compute the features of the Images
    features = cvtools.quick_features(img_c_8bit)

    image_res = opt.PixelSize / 1000

    # print("Image resolution is set to: {} mm/pixel.".format(str(image_res)))

    entry = {DBCONST.IMG_FNAME: os.path.join(image_dir, filename),
             DBCONST.IMG_ID: filename.split('.')[0],
             DBCONST.IMG_DATE: datetime.date.fromtimestamp(timestamp).strftime('%Y-%m-%d'),
             DBCONST.IMG_TIME: datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S'),
             DBCONST.IMG_TSTAMP: timestamp,
             DBCONST.IMG_FSIZE: os.path.getsize(image_path) / 1000.0,
             DBCONST.ECCENTRICITY: features['eccentricity'],
             DBCONST.ORIENT: features['orientation'] * 180 / math.pi,
             DBCONST.MJR_LEN: features['major_axis_length'] * image_res,
             DBCONST.MIN_LEN: features['minor_axis_length'] * image_res,
             DBCONST.HEIGHT: img_c_8bit.shape[0],
             DBCONST.WIDTH: img_c_8bit.shape[1],
             DBCONST.SOLIDITY: features['solidity'],
             DBCONST.ASPT_RATIO: features['aspect_ratio'],
             DBCONST.EST_VOL: features['estimated_volume'] * image_res * image_res * image_res,
             DBCONST.AREA: features['area'] * image_res * image_res}

    output = {'entry': entry, 'features': features}
    return output


# threaded function for each process to call
# queues are used to sync processes
def process_bundle_list(bundle_queue, output_queue):
    while True:
        try:
            output_queue.put(process_image(bundle_queue.get()))
        except:
            time.sleep(0.02 * np.random.rand())


def insert_database(df, db_path, table_name):

    #TODO: Check if the table exists in the path
    try:
        conn = sqlite3.connect(db_path)
        print("\ta. Connected to Sqlite")
        df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
        print("\tb. Inserted into Database")
        conn.commit()
        conn.close()
    except sqlite3.Error as error:
        print("Failed to Insert into table ", error)

    finally:
        if conn:
            conn.close()
            print("\tc. Sqlite connection is closed")


def run(data_path):
    print("Running SPC image conversion...")

    # get the base name of the directory with tif file
    base_dir_name = os.path.basename(os.path.abspath(data_path))
    print("\nListing directory " + base_dir_name + "...")

    # Combines all the Directories and puts in list
    image_list = []
    if opt.MergeSubDirs:
        sub_directory_list = sorted(glob.glob(os.path.join(data_path, "[0-9]" * 10)))
        for sub_directory in sub_directory_list:
            print("Listing sub directory " + sub_directory + "...")
            image_list += glob.glob(os.path.join(sub_directory, "*.tif"))
    else:
        image_list += glob.glob(os.path.join(data_path, "*.tif"))

    image_list = sorted(image_list)

    # Return if no images are found
    if len(image_list) == 0:
        print("No images were found. skipping this directory.")
        return

    # Create the output directories for the images
    subdir = os.path.join(data_path, '..', base_dir_name + '_processed')
    print(subdir)
    if not os.path.exists(subdir):
        os.makedirs(subdir)
    image_dir = os.path.join(subdir, 'images')
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    print("Starting image conversion...")

    # loop over the images and do the processing
    images_per_dir = opt.ImagesPerDir

    if opt.BayerPattern.lower() == "rg":
        bayer_conv = cv2.COLOR_BAYER_RG2RGB
    if opt.BayerPattern.lower() == "bg":
        bayer_conv = cv2.COLOR_BAYER_BG2RGB

    entry_list = []
    use_jpeg = opt.UseJpeg
    raw_color = opt.SaveRawColor

    for index, image in enumerate(tqdm(image_list)):
        bundle = load_data(index, image, image_dir, images_per_dir, bayer_conv)
        output = process_image(bundle)
        entry_list.append(output['entry'])
        write_data(output, raw_color=raw_color, use_jpeg=use_jpeg)

    print("Exporting spreadsheet results...")
    df = pandas.DataFrame.from_dict(entry_list)
    extension = ".jpeg" if use_jpeg else ".png"
    df[DBCONST.IMG_FNAME] = df[DBCONST.IMG_FNAME].apply(lambda x: "{}{}".format(x[:-4], extension))
    df.to_csv(os.path.join(subdir, 'features.csv'), index=False, sep=',')

    # Insert into database
    print("Inserting into Database")
    insert_database(df, db_path=opt.db_dir.format('test.db'), table_name=DBCONST.date_table)
    print("Done Processing.")

# Process a directory of images
# def run(data_path):
#     print("Running SPC image conversion...")
#
#     # get the base name of the directory with tif file
#     base_dir_name = os.path.basename(os.path.abspath(data_path))
#     print("\nListing directory " + base_dir_name + "...")
#
#     # Combines all the Directories and puts in list
#     image_list = []
#     if opt.MergeSubDirs:
#         sub_directory_list = sorted(glob.glob(os.path.join(data_path, "[0-9]" * 10)))
#         for sub_directory in sub_directory_list:
#             print("Listing sub directory " + sub_directory + "...")
#             image_list += glob.glob(os.path.join(sub_directory, "*.tif"))
#     else:
#         image_list += glob.glob(os.path.join(data_path, "*.tif"))
#
#     image_list = sorted(image_list)
#
#     # Return if no images are found
#     if len(image_list) == 0:
#         print("No images were found. skipping this directory.")
#         return
#
#     # Get the total number of images in the directory
#     total_images = len(image_list)
#
#     # Create the output directories for the images
#     subdir = os.path.join(data_path, '..', base_dir_name + '_processed')
#     print(subdir)
#     if not os.path.exists(subdir):
#         os.makedirs(subdir)
#     image_dir = os.path.join(subdir, 'images')
#     if not os.path.exists(image_dir):
#         os.makedirs(image_dir)
#
#     print("Starting image conversion...")
#
#     # loop over the images and do the processing
#     images_per_dir = opt.ImagesPerDir
#
#     if opt.BayerPattern.lower() == "rg":
#         bayer_conv = cv2.COLOR_BAYER_RG2RGB
#     if opt.BayerPattern.lower() == "bg":
#         bayer_conv = cv2.COLOR_BAYER_BG2RGB
#
#     print("\n1. Loading {} images.\m".format(str(total_images)))
#     bundle_queue = Queue()
#     for index, image in enumerate(tqdm(image_list)):
#
#         absdir = os.path.join(image_dir, str(images_per_dir * int(index / images_per_dir)).zfill(5))
#
#         filename = os.path.basename(image)
#
#         if not os.path.exists(absdir):
#             os.makedirs(absdir)
#
#         bundle = {'image_path': image,
#                   'image': cvtools.import_image(os.path.dirname(image), filename, bayer_pattern=bayer_conv),
#                   'image_dir': absdir}
#         bundle_queue.put(bundle)
#
#     # Get the number of proceess to use based on CPUs
#     n_threads = max(multiprocessing.cpu_count() - 1, 1)
#
#     # Create the set of processes and start them
#     output_queue = Queue()
#     processes = []
#     for i in range(0, n_threads):
#         p = Process(target=process_bundle_list, args=(bundle_queue, output_queue))
#         p.start()
#         processes.append(p)
#
#     # Monitor processing of the images and save processed images to disk as they become available
#     print("2. Processing Images...")
#
#     entry_list = []
#     use_jpeg = opt.UseJpeg
#     raw_color = opt.SaveRawColor
#     images_processed = 0
#
#     for counter in tqdm(range(total_images)) or images_processed <= total_images :
#         try:
#             output = output_queue.get()
#             if output:
#                 entry_list.append(output['entry'])
#                 #output_path = os.path.join(output['entry'][DBCONST.IMG_FNAME], output['entry'][DBCONST.IMG_ID])
#                 output_path = output['entry'][DBCONST.IMG_FNAME][:-4]
#                 extension = ".jpeg" if use_jpeg else ".png"
#
#                 if raw_color:
#                     cv2.imwrite(os.path.join(output_path + "_rawcolor" + extension), output['features']['rawcolor'])
#                 cv2.imwrite(os.path.join(output_path + extension), output['features']['image'])
#                 cv2.imwrite(os.path.join(output_path + "_binary.png"), output['features']['binary'])
#                 images_processed = images_processed+1
#         except:
#             time.sleep(0.05)
#
#     # Terminate the processes in case they are stuck
#     for p in processes:
#         p.terminate()
#
#     print("3. Exporting spreadsheet results...")
#     df = pandas.DataFrame.from_dict(entry_list)
#     extension = ".jpeg" if use_jpeg else ".png"
#     df[DBCONST.IMG_FNAME] = df[DBCONST.IMG_FNAME].apply(lambda x: "{}{}".format(x[:-4],extension))
#     df.to_csv(os.path.join(subdir, 'features.csv'), index=False, sep=',')
#
#     # Insert into database
#     print("4. Inserting into Database")
#     insert_database(df, db_path=opt.db_dir.format('test.db'), table_name=DBCONST.date_table)
#     print("5. Done Processing.")


def valid_image_dir(test_path):
    num_images = glob.glob(os.path.join(test_path, "*.tif"))
    return len(num_images) > 0


def batchprocess(data_path):

    multiprocessing.freeze_support()

    # If given directory is a single data directory, just process it
    if valid_image_dir(data_path):
        run(data_path)
        return

    # List data directories to be processed (Each in unixtime format)
    directory_list = sorted(glob.glob(os.path.join(data_path, "[0-9]" * 10)))

    if len(directory_list) == 0:
        print("No data directories found.")
        return

    # Process the data directories in order
    print('Processing each data directory...')
    for directory in directory_list:
        if os.path.isdir(directory):
            run(directory)