"""
utils modules
"""

import pandas as pd
import os
import openslide


def save_patchframe_patches(frame_path, save_dir):
    """For viewing hard copies of the patches in a patch frame"""
    patchframe = pd.read_pickle(frame_path)
    os.makedirs(save_dir, exist_ok=1)
    num_patches = patchframe.shape[0]
    for i in range(num_patches):
        info = patchframe.ix[i]
        slide = openslide.OpenSlide(info['parent'])
        patch = slide.read_region(location=(info['w'], info['h']), level=info['level'],
                                  size=(info['size'], info['size'])).convert('RGB')
        filename = os.path.join(save_dir, 'patch{}.png'.format(i))
        patch.save(filename)
