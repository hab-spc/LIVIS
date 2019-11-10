"""
Filename: cvtools.py
Authors: Taruj
Description:image processing tools for plankton images
"""

# Standard dist imports
import os
from math import pi
import cv2
from skimage import morphology, measure, restoration
from skimage.filters import scharr, gaussian
import numpy as np
from scipy import ndimage


class configuration:
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


def make_gaussian(size, fwhm=3, center=None):
    """ Make a square gaussian kernel.
    size is the length of a side of the square
    fwhm is full-width-half-maximum, which
    can be thought of as an effective radius.
    """

    x = np.arange(0, size, 1, float)
    y = x[:, np.newaxis]

    if center is None:
        x0 = y0 = size // 2
    else:
        x0 = center[0]
        y0 = center[1]

    output = np.exp(-4 * np.log(2) * ((x - x0) ** 2 + (y - y0) ** 2) / fwhm ** 2)
    output = output / np.sum(output)

    return output


# import raw image
def import_image(abs_path, filename, raw=True, bayer_pattern=cv2.COLOR_BAYER_RG2RGB):
    # Load and convert image as needed
    img_c = cv2.imread(os.path.join(abs_path, filename), cv2.IMREAD_UNCHANGED)
    if raw:
        img_c = cv2.cvtColor(img_c, bayer_pattern)
    return img_c


# convert image to 8 bit with autoscaling
def convert_to_8bit(img):
    # Convert to 8 bit and autoscale
    result = np.float32(img) - np.min(img)
    result[result < 0.0] = 0.0
    if np.max(img) != 0:
        result = result / np.max(img)

    return np.uint8(255 * result)


# extract simple features and create a binary representation of the image
def quick_features(img, config=configuration):
    """
    :param img: 8-bit array
    """
    # Pull out some settings from config if available
    if config:
        min_obj_area = config.MinObjectArea
        objs_per_roi = config.ObjectsPerROI
        deconv = config.Deconvolve
        edge_thresh = config.EdgeThreshold
    else:
        min_obj_area = 100
        objs_per_roi = 1
        deconv = False
        edge_thresh = 2.5

    # Define an empty dictionary to hold all features
    features = {'rawcolor': np.copy(img)}

    # compute features from gray image
    gray = np.uint8(np.mean(img, 2))

    # edge-based segmentation
    edges_mag = scharr(gray)
    edges_med = np.median(edges_mag)
    edges_thresh = edge_thresh * edges_med
    edges = edges_mag >= edges_thresh
    edges = morphology.closing(edges, morphology.square(3))
    filled_edges = ndimage.binary_fill_holes(edges)
    edges = morphology.erosion(filled_edges, morphology.square(3))

    # Compute morphological descriptors based on edge
    label_img = morphology.label(edges, neighbors=8, background=0)
    props = measure.regionprops(label_img, gray, coordinates='xy')

    props = sorted(props, reverse=True, key=lambda k: k.area)

    if len(props) > 0:
        # Init mask with the largest area object in the roi
        bw_img = label_img == props[0].label
        bw_img_all = bw_img.copy()

        avg_count = 0
        n_objs = objs_per_roi if len(props) > objs_per_roi else len(props)

        for f in range(0, n_objs):
            if props[f].area > min_obj_area:
                bw_img_all = bw_img_all + ((label_img) == props[f].label)
                avg_count = avg_count + 1

            if f >= objs_per_roi:
                break

        # Take the largest object area as the roi area
        major_axis = props[0].major_axis_length
        minor_axis = props[0].minor_axis_length
        # Save simple features of the object
        features['area'] = props[0].area
        features['minor_axis_length'] = minor_axis
        features['major_axis_length'] = major_axis
        features['aspect_ratio'] = 1 if major_axis == 0 else minor_axis / major_axis
        features['orientation'] = props[0].orientation
        features['eccentricity'] = props[0].eccentricity
        features['solidity'] = props[0].solidity
        features['estimated_volume'] = 4.0 / 3 * pi * major_axis * minor_axis * minor_axis

    else:
        # Save simple features of the object
        features['area'] = 0.0
        features['minor_axis_length'] = 0.0
        features['major_axis_length'] = 0.0
        features['aspect_ratio'] = 1
        features['orientation'] = 0.0
        features['eccentricity'] = 0
        features['solidity'] = 0
        features['estimated_volume'] = 0

    # Masked background with Gaussian smoothing, image sharpening, and reduction of chromatic aberration
    # mask the raw image with smoothed foreground mask
    blurred_bw_img = gaussian(bw_img_all, 3)
    for i in range(3):
        img[:, :, i] = img[:, :, i] * blurred_bw_img

    # Make a guess of the PSF for sharpening
    psf = make_gaussian(5, 3, center=None)

    img = np.float32(img) if np.max(img) == 0 else np.float32(img) / np.max(img)

    if deconv:
        img[img == 0] = 0.0001
        for i in range(3):
            img[:, :, i] = restoration.richardson_lucy(img[:, :, i], psf, 7)

    # Rescale image to uint8 0-255
    img[img < 0] = 0
    img = np.uint8(255 * img) if np.max(img) == 0 else np.uint8(255 * img / np.max(img))

    features['image'] = img
    features['binary'] = 255 * bw_img_all

    return features
