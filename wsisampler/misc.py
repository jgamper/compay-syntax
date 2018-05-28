"""
Utils module
"""

import pandas as pd
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
