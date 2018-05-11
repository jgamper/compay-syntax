import numpy as np
from skimage import filters, color
from skimage.morphology import disk
from skimage.morphology import opening, closing, dilation
import os
from PIL import Image
import pickle

import modules.utils as ut


class NumpyTissueMask(object):

    def __init__(self):
        """
        An object for storing the tissue mask.
        """
        self.level = None
        self.data = None
        self.patchsize = None

    def generate(self, parent_wsi, approx_downsampling, method='otsu_sat_morph'):
        """
        Generate a mask.
        :param parent_wsi:
        :param approx_downsampling:
        :param method:
        :return:
        """
        # threshold=50 is just 'any large number'.
        self.level = ut.get_level(parent_wsi, desired_downsampling=approx_downsampling, threshold=50)
        if method == 'otsu_sat_morph':
            self.data = self._generate_otsu_sat_morph(parent_wsi, self.level)

    def set_patchsize(self, x):
        """
        Set patchsize
        :param x:
        :return:
        """
        self.patchsize = x

    def _generate_otsu_sat_morph(self, wsi, level):
        """
        Generate a tissue mask by 'otsu_sat_morph' method.
        This is achieved by Otsu thresholding on the saturation channel \
        followed by morphological closing and opening to remove noise.
        :param wsi:
        :param level:
        :return:
        """
        disk_radius = 10  # radius of disk for morphological operations.
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

    def save_visualization(self, ID='slide', size=3000, savedir=os.getcwd(), wsi=None):
        """
        Save a visualization of the mask.
        :param size:
        :param savedir:
        :param ID:
        :param wsi:
        :return:
        """
        os.makedirs(savedir, exist_ok=True)
        file_name = os.path.join(savedir, ID + '_tissuemask.png')
        print('Saving tissue mask visualization to {}'.format(file_name))

        bg = Image.fromarray(self.data.astype(float))  # a resize hack...
        bg.thumbnail(size=(size, size))
        bg = np.asarray(bg).copy()

        dilated = dilation(bg, disk(10))
        contour = np.logical_xor(dilated, bg).astype(np.bool)

        if wsi is None:
            im = np.zeros_like(contour, dtype=np.uint8)
            im[contour] = 255
        else:
            im = np.asarray(wsi.get_thumbnail(size=(size, size))).copy()
            im[contour] = 0

        pil = Image.fromarray(im)
        pil.save(file_name)

    def save(self, ID='slide', savedir=os.getcwd()):
        """
        Save (pickle) the NumpyTissueMask object
        :param savedir: where to save to
        """
        filename = os.path.join(savedir, ID + '_NumpyTissueMask.pickle')
        print('Pickling NumpyTissueMask to {}'.format(filename))
        pickling_on = open(filename, 'wb')
        pickle.dump(self, pickling_on)
        pickling_on.close()

    def load(self, path, validation_wsi=None):
        """
        Load a NumpyTissueMask object.
        :return:
        """
        pickling_off = open(path, 'rb')
        npbg = pickle.load(pickling_off)
        self.level = npbg.level
        self.data = npbg.data
        self.patchsize = npbg.patchsize
        pickling_off.close()
        if validation_wsi is not None:
            assert validation_wsi.level_dimensions[self.level][0] == self.data.shape[1]
            assert validation_wsi.level_dimensions[self.level][1] == self.data.shape[0]


if __name__ == '__main__':
    import openslide

    slide = openslide.OpenSlide('/home/peter/Dropbox/SharedMore/WSI_sampler/Normal_106.tif')

    tm1 = NumpyTissueMask()
    tm1.generate(slide, 30)
    tm1.save(ID='myslide')

    tm2 = NumpyTissueMask()
    tm2.load(path='./myslide_NumpyTissueMask.pickle', validation_wsi=slide)
    tm2.save_visualization(ID='myslide_bare')
    tm2.save_visualization(ID='myslide', wsi=slide)
