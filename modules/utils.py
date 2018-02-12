"""
utils module
"""

import pandas as pd
import os
import openslide


def get_level_and_downsampling(OpenSlide, desired_downsampling):
    threshold = 0.1
    number_levels = len(OpenSlide.level_downsamples)
    diffs = [abs(desired_downsampling - OpenSlide.level_downsamples[i]) for i in range(number_levels)]
    minimum = min(diffs)
    if minimum > threshold:
        raise Exception('\n\nLevel not found for desired downsampling\nAvailable downsampling levels are:\n{}'.format(
            OpenSlide.level_downsamples))
    level = diffs.index(minimum)
    downsampling = OpenSlide.level_downsamples[level]
    return level, downsampling


def get_patch_from_info_dict(info):
    """
    Get a RGB PIL image from a patch info dict
    """
    slide = openslide.OpenSlide(info['parent'])
    patch = slide.read_region(location=(info['w'], info['h']), level=info['level'], size=(info['size'], info['size']))
    return patch.convert('RGB')


def save_patchframe_patches(input, save_dir):
    """
    For viewing hard copies of the patches in a patch frame.
    **Input should be a patchframe or a path to a pickled patchframe**.
    """
    if isinstance(input, pd.DataFrame):
        patchframe = input
    elif isinstance(input, str):
        patchframe = pd.read_pickle(input)
    else:
        raise Exception('\nInput should be patchframe (pd.DataFrame) or string path to pickled patchframe.')
    os.makedirs(save_dir, exist_ok=1)
    num_patches = patchframe.shape[0]
    print('\nSaving hard copies of patches in patchframe to {}'.format(save_dir))
    for i in range(num_patches):
        info = patchframe.ix[i]
        patch = get_patch_from_info_dict(info)
        filename = os.path.join(save_dir, 'patch{}.png'.format(i))
        patch.save(filename)
