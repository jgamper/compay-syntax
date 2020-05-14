import pandas as pd
import os

from ..slides.assign import assign_wsi_plus

def get_patch_from_info_dict(info, engine=None):
    """
    Get a patch from an info dict.

    :param info: info dict
    :return: patch (PIL image)
    """
    slide = assign_wsi_plus(info['parent'], info['lvl0'], engine=engine)
    patch = slide.get_patch(info['w'], info['h'], info['mag'], info['size'])
    return patch

def save_patchframe_patches(input, save_dir=os.path.join(os.getcwd(), 'patches'), engine=None):
    """
    Save patches in a patchframe to disk for visualization.

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
        patch = get_patch_from_info_dict(info, engine=engine)
        filename = os.path.join(save_dir, 'p{}_class_{}_from_{}.png'.format(i, info['class'], info['id']))
        patch.save(filename)
