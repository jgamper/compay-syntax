import os
import glob
from typeguard import typechecked
from typing import Any, List, Tuple

@typechecked
def val_in_list(val: Any, search_list: List[Any], tol: float=0.01) -> Tuple[bool, int]:
    """
    Search for a value in a list
    Args:
        val:
        search_list:
        tol:

    Returns:

    """
    diffs = [abs(search_list[i] - val) for i in range(len(search_list))]
    minimum = min(diffs)
    if minimum > tol:
        return (False, None)
    else:
        return (True, diffs.index(minimum))

@typechecked
def index_last_non_zero(x: List[int]) -> int:
    """
    Index of last non-zero element of list
        e.g. for [1,4,3,7,0,0,0,...] would return 3
    Args:
        x: List

    Returns:
        index of last non-zero element
    """
    for idx in range(len(x)):
        if not x[idx]:
            return idx - 1

@typechecked
def item_in_directory(search_key: str, dir: str) -> Tuple[bool, str]:
    """
    Search for file in a given directory by a substring.
    Args:
        search_key:
        dir: directory path

    Returns:
        (bool, string)
    """
    if not os.path.isdir(dir):
        return False, 'Not a directory'
    files_in_dir = glob.glob(os.path.join(dir, '*'))
    for file in files_in_dir:
        if search_key in file:
            return True, file
    return False, 'Not found'
