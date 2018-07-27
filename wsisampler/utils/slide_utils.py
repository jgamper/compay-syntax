import pandas as pd
import os


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
