"""
Utils module
"""

import pandas as pd
import os
import glob

from wsisampler import openslideplus


def val_in_list(val, search_list, tol=0.01):
    """
    Is a value in a list?
    :param val:
    :param search_list:
    :param tol:
    :return:
    """
    diffs = [abs(search_list[i] - val) for i in range(len(search_list))]
    minimum = min(diffs)
    if minimum > tol:
        return (False, None)
    else:
        return (True, diffs.index(minimum))


def index_last_non_zero(x):
    """
    Index of last non-zero element of list
    e.g. for [1,4,3,7,0,0,0,...] would return 3
    :param x:
    :return:
    """
    for idx in range(len(x)):
        if not x[idx]:
            return idx - 1


def item_in_directory(search_key, dir):
    """
    Search for file in a given directory by a substring.
    :param search_key: string
    :param dir: directory
    :return: (bool, string)
    """
    if not os.path.isdir(dir):
        return False, 'Not a directory'
    files_in_dir = glob.glob(os.path.join(dir, '*'))
    for file in files_in_dir:
        if search_key in file:
            return True, file
    return False, 'Not found'


def level_converter(wsi, x, lvl_in, lvl_out):
    """
    Convert a length/coordinate 'x' from lvl_in to lvl_out.
    :param wsi:
    :param x: a length/coordinate
    :param lvl_in: level to convert from
    :param lvl_out: level to convert to
    :return: New length/coordinate
    """
    return int(x * wsi.level_downsamples[lvl_in] / wsi.level_downsamples[lvl_out])


def get_level(mag, mags, threshold=0.01):
    """
    Get the level closest to a specified magnification.
    :param mag:
    :param threshold:
    :return:
    """
    diffs = [abs(mag - mags[i]) for i in range(len(mags))]
    minimum = min(diffs)
    assert minimum < threshold, 'Suitable level not found.'
    level = diffs.index(minimum)
    return level


def get_patch_from_info_dict(info):
    """
    Get a patch from an info dict
    :param info: info dict
    :return: patch (PIL image)
    """
    slide = openslideplus.OpenSlidePlus(info['parent'], info['lvl0'])
    patch = slide.get_patch(info['w'], info['h'], info['mag'], info['size'])
    return patch


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

    os.makedirs(save_dir, exist_ok=True)

    num_patches = patchframe.shape[0]
    print('Saving hard copies of patches in patchframe to {}.'.format(save_dir))
    for i in range(num_patches):
        info = patchframe.ix[i]
        patch = get_patch_from_info_dict(info)
        filename = os.path.join(save_dir, 'p{}_class_{}_from_{}.png'.format(i, info['class'], info['id']))
        patch.save(filename)
