"""
utils modules
"""

import pandas as pd
import os
import openslide


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
        slide = openslide.OpenSlide(info['parent'])
        patch = slide.read_region(location=(info['w'], info['h']), level=info['level'],
                                  size=(info['size'], info['size'])).convert('RGB')
        filename = os.path.join(save_dir, 'patch{}.png'.format(i))
        patch.save(filename)
