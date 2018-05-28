import numpy as np
from skimage import filters, color
from skimage.morphology import disk
from skimage.morphology import opening, closing, dilation
import pickle
import os
from PIL import Image

from wsisampler.utils.slide_utils import get_level
from wsisampler.utils.misc_utils import item_in_directory
from .slides.openslideplus import OpenSlidePlus
from .slides.jp2plus import JP2Plus


class TissueMask(object):

    def __init__(self, search_dir, reference_wsi):
        """
        An object for computing and storing tissue masks.

        :param search_dir: Where we store tissue masks.
        :param reference_wsi:
        """
        assert isinstance(reference_wsi, OpenSlidePlus) or isinstance(reference_wsi, JP2Plus), 'Reference WSI should be OpenSlidePlus or JP2Plus.'

        truth, filename = item_in_directory(reference_wsi.ID, search_dir)
        if truth:
            print('Tissue mask found. Loading.')
            self.load(filename)
        else:
            print('Tissue mask not found. Generating now.')
            self.level = get_level(mag=1.25, mags=reference_wsi.mags, threshold=5.0)
            self.mag = reference_wsi.mags[self.level]
            self.ref_factor = self.mag / reference_wsi.level0  # Use to convert coordinates.
            self.data = self._generate_tissue_mask_basic(reference_wsi, self.level)
            self.save(reference_wsi.ID, search_dir)

    def get_patch(self, w_ref, h_ref, mag, effective_size):
        """
        Get a patch.

        :param w_ref: Width coordinate in frame of reference WSI level 0.
        :param h_ref: Height coordinate in frame of reference WSI level 0.
        :param mag: Desired magnification.
        :param effective_size: Desired effective patchsize. \
            NOTE: The patch returned does not have this size!
        :return:
        """
        w = int(w_ref * self.ref_factor)
        h = int(h_ref * self.ref_factor)
        patchsize = int(effective_size * self.mag / mag)
        patch = self.data[h:h + patchsize, w:w + patchsize].astype(float)
        return patch

    def save(self, ID, savedir):
        """
        Save (pickle) the TissueMask.

        :param ID:
        :param savedir: where to save to
        """
        os.makedirs(savedir, exist_ok=True)
        filename = os.path.join(savedir, ID + '_TissueMask.pickle')
        print('Pickling TissueMask to {}'.format(filename))
        pickling_on = open(filename, 'wb')
        pickle.dump(self, pickling_on)
        pickling_on.close()

    def load(self, path):
        """
        Load TissueMask object.

        :return:
        """
        pickling_off = open(path, 'rb')
        tm = pickle.load(pickling_off)
        self.level = tm.level
        self.mag = tm.mag
        self.ref_factor = tm.ref_factor
        self.data = tm.data
        pickling_off.close()

    def visualize(self, reference_wsi):
        """
        Get a thumbnail visualization.

        :param reference_wsi:
        :return:
        """
        assert isinstance(reference_wsi, OpenSlidePlus), 'Reference WSI should be OpenSlidePlus.'
        size = 3000
        # A resize hack...
        tm = Image.fromarray(self.data.astype(float))
        tm.thumbnail(size=(size, size))
        tm = np.asarray(tm)

        dilated = dilation(tm, disk(10))
        contour = np.logical_xor(dilated, tm).astype(np.bool)

        wsi_thumb = np.asarray(reference_wsi.get_thumbnail(size=(size, size))).copy()  # Copy to avoid read-only issue.
        wsi_thumb[contour] = 0

        pil = Image.fromarray(wsi_thumb)
        return pil

    ### Tissue mask generation methods. Could add some more?

    @staticmethod
    def _generate_tissue_mask_basic(wsi, level):
        """
        Generate a tissue mask.
        This is achieved by Otsu thresholding on the saturation channel \
        followed by morphological closing and opening to remove noise.

        :param wsi:
        :param level:
        :return:
        """
        if not hasattr(wsi, 'jp2'):
            low_res = wsi.read_region(location=(0, 0), level=level, size=wsi.level_dimensions[level]).convert('RGB') \
                # Read slide at low resolution and make sure it's RGB (not e.g. RGBA).
            low_res_numpy = np.asarray(low_res)  # Convert to numpy array.
        else:
            low_res_numpy = wsi.read_region(location=(0, 0), level=level, size=wsi.level_dimensions[level])
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
