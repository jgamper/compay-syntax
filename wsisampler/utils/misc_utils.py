"""
Utils module
"""

import os
import glob


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
