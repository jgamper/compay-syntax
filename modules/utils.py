"""
utils module
"""

import pandas as pd
import os
import openslide
import numpy as np
from skimage import filters, color
from skimage.morphology import disk
from skimage.morphology import opening, closing
import glob


def string_in_directory(s, dir):
    """
    Is a string in a filename in the given directory?

    # Parameters
    :param s: string
    :param dir: directory

    # Returns
    :return: (bool, string)
    """
    if not os.path.isdir(dir):
        return 0, 'Not a directory'
    files_in_dir = glob.glob(os.path.join(dir, '*'))
    for file in files_in_dir:
        if s in file:
            return 1, file
    return 0, 'Not found'


def get_level(OpenSlide, desired_downsampling, threshold):
    """
    Get the level for a desired downsampling. Threshold controls how close true and desired downsampling must be.

    # Parameters
    :param OpenSlide:
    :param desired_downsampling:
    :param threshold:

    # Returns
    :return: level
    """
    number_levels = len(OpenSlide.level_downsamples)
    diffs = [abs(desired_downsampling - OpenSlide.level_downsamples[i]) for i in range(number_levels)]
    minimum = min(diffs)
    if minimum > threshold:
        raise Exception('Level not found for desired downsampling\nAvailable downsampling levels are:\n{}'.format(
            OpenSlide.level_downsamples))
    level = diffs.index(minimum)
    return level


def generate_background_mask(wsi, level):
    """
    Generate a background mask.
    This is achieved by otsu thresholding on the saturation channel followed by morphological closing and opening to remove noise.

    # Parameters
    :param wsi:
    :param level:
    :return:
    """
    disk_radius = 10
    low_res = wsi.read_region(location=(0, 0), level=level, size=wsi.level_dimensions[level]).convert('RGB')
    low_res_numpy = np.asarray(low_res).copy()
    low_res_numpy_hsv = color.convert_colorspace(low_res_numpy, 'RGB', 'HSV')
    saturation = low_res_numpy_hsv[:, :, 1]
    theshold = filters.threshold_otsu(saturation)
    high_saturation = (saturation > theshold)
    disk_object = disk(disk_radius)
    mask = closing(high_saturation, disk_object)
    mask = opening(mask, disk_object)
    if mask.dtype != bool:
        raise Exception('Background mask not boolean')
    return mask


def get_patch_from_info_dict(info):
    """
    Get a patch from an info dict

    # Parameters
    :param info: info dict

    # Returns
    :return: patch (PIL image)
    """
    slide = openslide.OpenSlide(info['parent'])
    patch = slide.read_region(location=(info['w'], info['h']), level=info['level'], size=(info['size'], info['size']))
    return patch.convert('RGB')


def save_patchframe_patches(input, save_dir=os.path.join(os.getcwd(), 'patches')):
    """
    Save patches in a patchframe to disk for visualization

    # Parameters
    :param input: patchframe or pickled patchframe
    :param save_dir: where to save to
    """
    if isinstance(input, pd.DataFrame):
        patchframe = input
    elif isinstance(input, str):
        patchframe = pd.read_pickle(input)
    else:
        raise Exception('Input should be patchframe (pd.DataFrame) or string path to pickled patchframe.')
    os.makedirs(save_dir, exist_ok=1)
    num_patches = patchframe.shape[0]
    print('\nSaving hard copies of patches in patchframe to {}'.format(save_dir))
    for i in range(num_patches):
        info = patchframe.ix[i]
        patch = get_patch_from_info_dict(info)
        filename = os.path.join(save_dir, 'p{}_class_{}_from_{}.png'.format(i, info['class'], info['id']))
        patch.save(filename)
