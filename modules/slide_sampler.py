import openslide
import os
import numpy as np
from skimage import filters, color
from skimage.morphology import disk
from skimage.morphology import opening, dilation
from PIL import Image


# def pil_show(x):
#     x = x.astype(np.float32)
#     if np.max(x) < 1.01: x *= 255.
#     x_pil = Image.fromarray(x)
#     x_pil.show()


class Slide_Sampler(object):

    def __init__(self, wsi_file, desired_down_sampling, size, background_desired_down_sampling=32):
        super(Slide_Sampler, self).__init__()
        self.wsi_file = wsi_file
        self.wsi = openslide.OpenSlide(self.wsi_file)
        self.desired_down_sampling = desired_down_sampling
        self.size = size
        self.background_desired_down_sampling = background_desired_down_sampling
        self.get_level_and_downsampling()
        self.width_available = int(self.wsi.dimensions[0] - self.down_sampling * size)
        self.height_available = int(self.wsi.dimensions[1] - self.down_sampling * size)
        self.get_background_mask()
        print('\nInitialized Slide_Sampler for slide {}'.format(os.path.basename(self.wsi_file)))
        print('Patches will be sampled at (level {0} == downsampling of {1}) with size {2} x {2}'.format(self.level,
                                                                                                         self.down_sampling,
                                                                                                         self.size))

    def get_level_and_downsampling(self):
        """
        Get the level and downsampling for the desired downsampling. If level is not found an exception is raised. Small threshold to allow for not exactly equal desired and true downsampling.
        :return:
        """
        threshold = 0.1
        diffs = [abs(self.desired_down_sampling - self.wsi.level_downsamples[i]) for i in
                 range(len(self.wsi.level_downsamples))]
        minimum = min(diffs)
        if minimum > threshold:
            raise Exception(
                '\nLevel not found for desired downsampling.\nAvailable downsampling factors are\n{}'.format(
                    self.wsi.level_downsamples))
        self.level = diffs.index(minimum)
        self.down_sampling = self.wsi.level_downsamples[self.level]

    def get_background_mask(self, disk_radius=10):
        """
        Get a background mask. That is a binary, downsampled image where True denotes a tissue region. This is achieved by otsu thresholding on the saturation channel followed by morphological opening to remove noise.
        :param disk_radius:
        :return:
        """
        print('\nGetting background mask...')
        self.get_background_mask_level()
        low_res = self.wsi.read_region(location=(0, 0), level=self.background_mask_level,
                                       size=self.wsi.level_dimensions[self.background_mask_level]).convert('RGB')
        low_res_numpy = np.asarray(low_res)
        low_res_numpy_hsv = color.convert_colorspace(low_res_numpy, 'RGB', 'HSV')
        saturation = low_res_numpy_hsv[:, :, 1]
        value = filters.threshold_otsu(saturation)
        mask = saturation > value
        selem = disk(disk_radius)
        mask = opening(mask, selem)
        self.background_mask = mask

    def get_background_mask_level(self):
        """
        Get level and downsampling of background mask for the desired background downsampling. If level is not found an exception is raised. Medium threshold to allow for not exactly equal desired and true downsampling.
        :return:
        """
        threshold = 4.
        diffs = [abs(self.background_desired_down_sampling - self.wsi.level_downsamples[i]) for i in
                 range(len(self.wsi.level_downsamples))]
        minimum = min(diffs)
        if minimum > threshold:
            raise Exception(
                '\nLevel not found for desired downsampling.\nAvailable downsampling factors are\n{}'.format(
                    self.wsi.level_downsamples))
        self.background_mask_level = diffs.index(minimum)
        self.background_mask_down_sampling = self.wsi.level_downsamples[self.background_mask_level]

    def get_patch(self):
        w = np.random.choice(self.width_available)
        h = np.random.choice(self.height_available)
        patch = self.wsi.read_region(location=(w, h), level=self.level, size=(self.size, self.size)).convert('RGB')
        return patch

    def print_slide_properties(self):
        """
        Print some WSI properties
        :return:
        """
        print('\nSlide properties.')
        print('Dimensions as level 0:')
        print(self.wsi.dimensions)
        print('Number of levels:')
        print(self.wsi.level_count)
        print('with downsampling factors:')
        print(self.wsi.level_downsamples)


###

data_dir = '/media/peter/HDD 1/datasets_peter/Camelyon16/Train/Original/Tumor'
file = os.path.join(data_dir, 'Tumor_001.tif')
mask_file = os.path.join(data_dir, 'Mask_Tumor', 'Tumor_001.tif')

sampler = Slide_Sampler(file, 4, 256)

sampler.print_slide_properties()

sampler.get_background_mask()

import matplotlib.pyplot as plt

mask = sampler.background_mask
plt.imshow(mask)
plt.show()

c = 2
