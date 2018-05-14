from openslide import OpenSlide
import numpy as np

from modules.openslideplus import OpenSlidePlus


class Annotation(OpenSlide):

    def __init__(self, file, reference_wsi):
        """
        An extension to the OpenSlide class for annotations.
        :param file:
        :param reference_wsi:
        """
        super(Annotation, self).__init__(file)

        assert isinstance(reference_wsi, OpenSlidePlus), 'Reference WSI should be OpenSlidePlus.'
        self.ref_factor = self.level_dimensions[0][0] / reference_wsi.level_dimensions[0][0] \
            # Use to convert coordinates.

        # Get level 0.
        self.level0 = reference_wsi.level0 * self.ref_factor

        # Get level magnifications.
        self.mags = [self.level0 / downsample for downsample in self.level_downsamples]

    def get_patch(self, w_ref, h_ref, mag, size):
        """
        Get a patch.
        If required magnification not available will use nearby magnification and resize.
        :param w_ref: Width coordinate in frame of reference WSI level 0.
        :param h_ref: Height coordinate in frame of reference WSI level 0.
        :param mag: Desired magnification.
        :param size: Desired patch size (square patch).
        :return:
        """
        w = int(w_ref * self.ref_factor)
        h = int(h_ref * self.ref_factor)

        extraction_level = self._get_level(mag, threshold=5.0)
        extraction_mag = self.mags[extraction_level]
        extraction_size = int(size * extraction_mag / mag)

        patch = self.read_region((w, h), extraction_level, (extraction_size, extraction_size)).convert('L')  # Mode 'L' is uint8 grayscale.
        if extraction_size != size:
            patch.thumbnail((size, size))  # Resize inplace.
        return patch

    def get_low_res_numpy(self):
        """
        Get a low resolution version as numpy array.
        Also returns a factor for converting lengths back to reference WSI level 0 frame.
        :return:
        """
        level = self._get_level(mag=1.25, threshold=5.0)
        size = self.level_dimensions[level]
        low_res = self.read_region((0, 0), level, size).convert('L')  # Mode 'L' is uint8 grayscale.
        low_res_np = np.asarray(low_res)
        factor = self.level_downsamples[level] / self.ref_factor  # Factor for converting lengths back to reference WSI level 0 frame.
        return low_res_np, factor

    def _get_level(self, mag, threshold=0.01):
        """
        Get the level corresponding to a specified magnification
        :param mag:
        :param threshold:
        :return:
        """
        diffs = [abs(mag - self.mags[i]) for i in range(len(self.mags))]
        minimum = min(diffs)
        assert minimum < threshold, 'Suitable level not found.'
        level = diffs.index(minimum)
        return level
