import numpy as np
from skimage.morphology import disk
from skimage.morphology import dilation
from PIL import Image

def visualize(tissue_mask, slide, size):
    """
    Get a thumbnail visualization.
    :param slide:
    :return:
    """
    # A resize hack...
    tm = Image.fromarray(tissue_mask.data.astype(float))
    tm.thumbnail(size=(size, size))
    tm = np.asarray(tm)

    dilated = dilation(tm, disk(10))
    contour = np.logical_xor(dilated, tm).astype(np.bool)

    wsi_thumb = np.asarray(slide.get_thumbnail(size=(size, size))).copy()  # Copy to avoid read-only issue.
    wsi_thumb[contour] = 0

    pil = Image.fromarray(wsi_thumb)
    return pil