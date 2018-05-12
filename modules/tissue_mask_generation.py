"""
Tissue mask generation methods.

Add your own...
"""

import numpy as np
from skimage import filters, color
from skimage.morphology import disk
from skimage.morphology import opening, closing


def generate_tissue_mask(wsi, level):
    """
    Generate a tissue mask.
    This is achieved by Otsu thresholding on the saturation channel \
    followed by morphological closing and opening to remove noise.
    :param wsi:
    :param level:
    :return:
    """
    low_res = wsi.read_region(location=(0, 0), level=level, size=wsi.level_dimensions[level]).convert('RGB') \
        # Read slide at low resolution and make sure it's RGB (not e.g. RGBA).
    low_res_numpy = np.asarray(low_res)  # Convert to numpy array.
    low_res_numpy_hsv = color.convert_colorspace(low_res_numpy, 'RGB', 'HSV')  # Convert to Hue-Saturation-Value.
    saturation = low_res_numpy_hsv[:, :, 1]  # Get saturation channel.
    threshold = filters.threshold_otsu(saturation)  # Otsu threshold.
    mask = (saturation > threshold)  # Tissue is 'high saturation' region.

    # Morphological operations
    disk_radius = 10  # radius of disk for morphological operations.
    disk_object = disk(disk_radius)
    mask = closing(mask, disk_object)  # remove 'pepper'.
    mask = opening(mask, disk_object)  # remove 'salt'.
    assert mask.dtype == bool, 'Mask not Boolean'

    return mask
