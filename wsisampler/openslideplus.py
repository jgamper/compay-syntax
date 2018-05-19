from openslide import OpenSlide
import os
from PIL import Image
from jp2 import OpenJP2
from .misc import index_last_non_zero


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
        extraction_level = index_last_non_zero(higher_mags)
        extraction_mag = self.mags[extraction_level]
        extraction_size = int(size * extraction_mag / mag)

        patch = self.read_region((w, h), extraction_level, (extraction_size, extraction_size)).convert('RGB')  # Make sure it's RGB (not e.g. RGBA).
        if extraction_size != size:
            patch.thumbnail((size, size))  # Resize inplace.
        return patch

class JP2Plus(OpenJP2):

    def __init__(self, file, level0, engine):
        """
        An extension to OpenJP2 object with a method to get a patch by maginifaction.
        :param file: Path to the jp2 format WSI
        :param level0: The 'magnification' at level 0.
        :param engine: Matlab engine object.
        """
        super(OpenJP2, self).__init__(file, engine)

        # ID (name) of the WSI
        self.ID = os.path.splitext(os.path.basename(file))[0]

        self.level0 = float(level0)

        # Compute level maginifications
        self.mags = [self.level0 / downsample for downsample in self.level_downsamples]

    def get_patch(self, w, h, mag, size):
        """
        Get a patch.
        If required magnification is not available will use higher magnification and resize.
        :param w: Width coordinate in level 0 frame.
        :param h: Height coordinate in level 0 frame.
        :param mag: Desired magnification.
        :param size: Desired patch size (square patch).
        :return:
        """

        assert self.level0 >= mag, 'Magnification not available.'

        higher_mags = [self.mags[i] >= mag for i in range(len(self.mags))]
        exctraction_level = index_last_non_zero(higher_mags)
        exctraction_mag = self.mags[exctraction_level]
        extraction_size = int(size * extraction_mag / mag)

        patch = self.read_region((w, h), extraction_level, (extraction_size, extraction_size))
        patch = Image.fromarray(patch, 'RGB')
        if exctraction_size != size:
            patch.thumbnail((size, size)) # Resize inplace.
        return patch

def assign_wsi_plus(file, level0, engine=None):
    """
    Function to select if the JP2Plus or OpenSlidePlus should be used for a given image.
    :param file: Path to the jp2 format WSI
    :param level0: The 'magnification' at level 0.
    :param engine: Matlab engine object.
    """
    if engine == None:
        return OpenSlidePlus(file, level0)
    if engine != None:
        return JP2Plus(file, level0, engine)
