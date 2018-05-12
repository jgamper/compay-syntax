"""
Utils module
"""

import pandas as pd
import os
import openslide
import glob


def val_in_list(val, x, tol=0.01):
    """
    Is a value in a list?
    :param val:
    :param x:
    :param tol:
    :return:
    """
    diffs = [abs(x[i] - val) for i in range(len(x))]
    minimum = min(diffs)
    if minimum > tol:
        return (False, None)
    else:
        return (True, diffs.index(minimum))


def string_in_directory(s, dir):
    """
    Is a string in a filename in the given directory?
    :param s: string
    :param dir: directory
    :return: (bool, string)
    """
    if not os.path.isdir(dir):
        return False, 'Not a directory'
    files_in_dir = glob.glob(os.path.join(dir, '*'))
    for file in files_in_dir:
        if s in file:
            return True, file
    return False, 'Not found'


def get_patch_from_info_dict(info):
    """
    Get a patch from an info dict
    :param info: info dict
    :return: patch (PIL image)
    """
    slide = openslide.OpenSlide(info['parent'])
    patch = slide.read_region(location=(info['w'], info['h']), level=info['level'], size=(info['size'], info['size']))
    return patch.convert('RGB')  # Make sure it's RGB (not e.g. RGBA).


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
    print('Saving hard copies of patches in patchframe to {}'.format(save_dir))
    for i in range(num_patches):
        info = patchframe.ix[i]
        patch = get_patch_from_info_dict(info)
        filename = os.path.join(save_dir, 'p{}_class_{}_from_{}.png'.format(i, info['class'], info['id']))
        patch.save(filename)
