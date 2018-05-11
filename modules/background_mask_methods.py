import numpy as np
from skimage import filters, color
from skimage.morphology import disk
from skimage.morphology import opening, closing

def generate_background_mask(wsi, level):
    """
    Generate a background mask.
    This is achieved by Otsu thresholding on the saturation channel followed by morphological closing and opening to remove noise.
    :param wsi:
    :param level:
    :return:
    """
    disk_radius = 10
    low_res = wsi.read_region(location=(0, 0), level=level, size=wsi.level_dimensions[level]).convert('RGB')
    low_res_numpy = np.asarray(low_res).copy()
    low_res_numpy_hsv = color.convert_colorspace(low_res_numpy, 'RGB', 'HSV')
    saturation = low_res_numpy_hsv[:, :, 1]
    threshold = filters.threshold_otsu(saturation)
    high_saturation = (saturation > threshold)
    disk_object = disk(disk_radius)
    mask = closing(high_saturation, disk_object)  # remove 'pepper'
    mask = opening(mask, disk_object)  # remove 'salt'
    assert mask.dtype == bool, 'Mask not Boolean'
    return mask