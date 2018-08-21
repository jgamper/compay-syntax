import numpy as np
import os
from PIL import Image

from ..utils.misc_utils import index_last_non_zero
from ..utils.slide_utils import get_level

try:
    import matlab
    from matlab import engine
except ImportError:
    raise ImportError('No MATLAB engine found.')


###

class OpenJP2(object):

    def __init__(self, wsi_file, engine):
        """
        TODO: What is this?

        :param wsi_file: path to a WSI file.
        :param engine:
        """
        self.wsi_file = wsi_file

        # Engine stuff
        self.engine = engine
        call_path = os.path.dirname(os.path.realpath(__file__))
        self.engine.addpath(r'{}'.format(call_path), nargout=0)

        # Just to flag as JP2
        self.jp2 = True

        ### Get slide info
        level_dim, level_downsamples, level_count = self.engine.get_jp2_info(self.wsi_file, nargout=3)
        # Make sure we have the right formats
        level_dim, level_downsamples, level_count = np.array(level_dim), np.array(level_downsamples), int(level_count)

        self.level_downsamples = [float(downsample[0]) for downsample in level_downsamples]
        self.level_dimensions = [(level_dim[level, 1], level_dim[level, 0]) for level in range(level_count)]

    def read_region(self, location, level, size):
        """
        Read a region of the WSI using the MATLAB function `read_jp2_region`.

        :param location:
        :param level:
        :param size:
        :return:
        """
        y1 = int(location[0] / pow(2, level)) + 1
        x1 = int(location[1] / pow(2, level)) + 1
        y2 = int(y1 + size[0] - 1)
        x2 = int(x1 + size[1] - 1)
        patch = self.engine.read_jp2_region(self.wsi_file, level, matlab.int32([x1, x2, y1, y2]))
        patch = np.array(patch._data).reshape(patch.size, order='F')
        return patch


###

class JP2Plus(OpenJP2):

    def __init__(self, file, level0, engine):
        """
        An extension to OpenJP2 object with a method to get a patch by maginifaction.

        :param file: Path to the matlab_files format WSI
        :param level0: The 'magnification' at level 0.
        :param engine: Matlab engine object.
        """
        super(JP2Plus, self).__init__(file, engine)

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
        extraction_level = index_last_non_zero(higher_mags)
        extraction_mag = self.mags[extraction_level]
        extraction_size = int(size * extraction_mag / mag)

        patch = self.read_region((w, h), extraction_level, (extraction_size, extraction_size))
        patch = Image.fromarray(patch, 'RGB')
        if extraction_size != size:
            patch.thumbnail((size, size))  # Resize inplace.
        return patch

    def get_thumbnail(self, size):
        """
        Generates a thumbnail image for visualisation
        :param size: a tuple of the target size
        :return: PIL Image
        """
        level = get_level(mag=1.25, mags=self.mags, threshold=5.0)
        low_res = self.read_region(location=(0,0), level=level, size=self.level_dimensions[level])
        low_res = Image.fromarray(low_res)
        low_res.thumbnail(size)
        return low_res
