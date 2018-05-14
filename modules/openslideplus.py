from openslide import OpenSlide
import os

import modules.misc as ut


class OpenSlidePlus(OpenSlide):

    def __init__(self, file, level0):
        """
        An extension to the OpenSlide class with a method to get a patch by magnification.
        :param file: Path to the WSI readable by openslide.
        :param level0: The 'magnification' at level 0. If 'infer' we attempt to get from metadata.
        """
        super(OpenSlidePlus, self).__init__(file)

        # ID (name) of the WSI.
        self.ID = os.path.splitext(os.path.basename(file))[0]

        # Add level0 magnification.
        if level0 == 'infer':
            try:
                self.level0 = float(self.properties['openslide.objective-power'])
                print('Level 0 found @ {}X'.format(self.level0))
            except:
                raise Exception('Slide does not have property objective-power.')
        else:
            self.level0 = float(level0)

        # Compute level magnifications.
        self.mags = [self.level0 / downsample for downsample in self.level_downsamples]

    def get_patch(self, w, h, mag, size):
        """
        Get a patch.
        If required magnification not available will use a higher magnification and resize.
        :param w: Width coordinate in level 0 frame.
        :param h: Height coordinate in level 0 frame.
        :param mag: Desired magnification.
        :param size: Desired patch size (square patch).
        :return:
        """
        assert self.level0 >= mag, 'Magnification not available.'

        higher_mags = [self.mags[i] >= mag for i in range(len(self.mags))]
        extraction_level = ut.index_last_non_zero(higher_mags)
        extraction_mag = self.mags[extraction_level]
        extraction_size = int(size * extraction_mag / mag)

        patch = self.read_region((w, h), extraction_level, (extraction_size, extraction_size)).convert('RGB')  # Make sure it's RGB (not e.g. RGBA).
        if extraction_size != size:
            patch.thumbnail((size, size))  # Resize inplace.
        return patch

    def _get_level(self, mag, threshold=0.01):
        """
        Get the level corresponding to a specified magnification.
        :param mag:
        :param threshold:
        :return:
        """
        diffs = [abs(mag - self.mags[i]) for i in range(len(self.mags))]
        minimum = min(diffs)
        assert minimum < threshold, 'Suitable level not found.'
        level = diffs.index(minimum)
        return level
