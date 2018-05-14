import numpy as np
from skimage import filters, color
from skimage.morphology import disk
from skimage.morphology import opening, closing
import pickle
import os

import modules.misc as ut
from modules.openslideplus import OpenSlidePlus


class TissueMask(object):

    def __init__(self, reference_wsi, search_dir):
        """
        An object for computing and storing tissue masks.
        :param reference_wsi:
        :param search_dir: Where we store tissue masks.
        """
        assert isinstance(reference_wsi, OpenSlidePlus), 'Reference WSI should be OpenSlidePlus.'

        truth, filename = ut.item_in_directory(reference_wsi.ID, search_dir)
        if truth:
            print('Tissue mask found. Loading.')
            self._load(filename)
        else:
            print('Tissue mask not found. Generating now.')
            self.level = reference_wsi._get_level(mag=1.25, threshold=5.0)
            self.mag = reference_wsi.mags[self.level]
            self.ref_factor = self.mag / reference_wsi.level0  # Use to convert coordinates.
            self.data = self._generate_tissue_mask_basic(reference_wsi, self.level)
            self._save(reference_wsi.ID, search_dir)

    def get_reduced_patch(self, w_ref, h_ref, mag, effective_size):
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

    def _save(self, ID, savedir):
        """
        Save (pickle) the TissueMask
        :param ID:
        :param savedir: where to save to
        """
        os.makedirs(savedir, exist_ok=True)
        filename = os.path.join(savedir, ID + '_TissueMask.pickle')
        print('Pickling TissueMask to {}'.format(filename))
        pickling_on = open(filename, 'wb')
        pickle.dump(self, pickling_on)
        pickling_on.close()

    def _load(self, path):
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
