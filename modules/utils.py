"""
utils module
"""

import pandas as pd
import os
import openslide
import glob


def string_in_directory(s, dir):
    """
    Is a string in a filename in the given directory?
    :param s: string
    :param dir: directory
    :return: (bool, string)
    """
    if not os.path.isdir(dir):
        return 0, 'Not a directory'
    files_in_dir = glob.glob(os.path.join(dir, '*'))
    for file in files_in_dir:
        if s in file:
            return 1, file
    return 0, 'Not found'


def get_level(slide, desired_downsampling, threshold):
    """
    Get the level for a desired downsampling. Threshold controls how close true and desired downsampling must be.
    :param slide:
    :param desired_downsampling:
    :param threshold:
    :return: level
    """
    number_levels = len(slide.level_downsamples)
    diffs = [abs(desired_downsampling - slide.level_downsamples[i]) for i in range(number_levels)]
    minimum = min(diffs)
    warn = 'Level not found for desired downsampling\nAvailable downsampling levels are:\n{}'
    assert minimum > threshold, warn.format(slide.level_downsamples)
    level = diffs.index(minimum)
    return level


def get_patch_from_info_dict(info):
    """
    Get a patch from an info dict
    :param info: info dict
    :return: patch (PIL image)
    """
    slide = openslide.OpenSlide(info['parent'])
    patch = slide.read_region(location=(info['w'], info['h']), level=info['level'], size=(info['size'], info['size']))
    return patch.convert('RGB')


def save_patchframe_patches(input, save_dir=os.path.join(os.getcwd(), 'patches')):
    """
    Save patches in a patchframe to disk for visualization
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
