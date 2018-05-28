import pandas as pd
import os

from wsisampler.slides.assign import get_wsi_plus


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


def get_patch_from_info_dict(info, engine=None):
    """
    Get a patch from an info dict.

    :param info: info dict
    :return: patch (PIL image)
    """
    slide = get_wsi_plus(info['parent'], info['lvl0'], engine=engine)
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
