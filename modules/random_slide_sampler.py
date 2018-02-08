import openslide
import os
import numpy as np
from skimage import filters, color
from skimage.morphology import disk
from skimage.morphology import opening, dilation
from PIL import Image


def pil_show(x):
    x = x.astype(np.float32)
    if np.max(x) < 1.01: x *= 255.
    x_pil = Image.fromarray(x)
    x_pil.show()


class Random_Slide_Sampler(object):

    def __init__(self, wsi_file, desired_down_sampling, size, annotation_mask_file=None):
        super(Random_Slide_Sampler, self).__init__()
        self.wsi_file = wsi_file
        self.wsi = openslide.OpenSlide(self.wsi_file)
        self.desired_down_sampling = desired_down_sampling
        self.size = size

        self.get_level_and_downsampling()

        print('\nInitialized Random_Slide_Sampler for slide {}'.format(os.path.basename(self.wsi_file)))
        print('Patches will be sampled at level {0} (downsampling of {1}) with size {2} x {2}'.format(self.level,
                                                                                                      self.down_sampling,
                                                                                                      self.size))
        self.width_available = int(self.wsi.dimensions[0] - self.down_sampling * size)
        self.height_available = int(self.wsi.dimensions[1] - self.down_sampling * size)

        self.get_background_mask()

    def get_level_and_downsampling(self, threshold=0.1):
        diffs = [abs(self.desired_down_sampling - self.wsi.level_downsamples[i]) for i in
                 range(len(self.wsi.level_downsamples))]
        minimum = min(diffs)

        if minimum > threshold:
            raise Exception(
                '\n\nLevel not found for desired downsampling.\nAvailable downsampling factors are\n{}'.format(
                    self.wsi.level_downsamples))

        self.level = diffs.index(minimum)
        self.down_sampling = self.wsi.level_downsamples[self.level]

    def print_slide_properties(self):
        print('\nSlide properties.')
        print('Dimensions as level 0:')
        print(self.wsi.dimensions)
        print('Number of levels:')
        print(self.wsi.level_count)
        print('with downsampling factors:')
        print(self.wsi.level_downsamples)

    def get_background_mask_level(self, desired_down_sampling=32, threshold=0.1):
        diffs = [abs(desired_down_sampling - self.wsi.level_downsamples[i]) for i in
                 range(len(self.wsi.level_downsamples))]
        minimum = min(diffs)

        if minimum > threshold:
            raise Exception(
                '\n\nLevel not found for desired downsampling.\nAvailable downsampling factors are\n{}'.format(
                    self.wsi.level_downsamples))

        self.background_mask_level = diffs.index(minimum)
        # self.background_mask_down_sampling = self.wsi.level_downsamples[self.background_mask_level]

    def get_background_mask(self, desired_down_sampling=32, threshold=0.1, disk_radius=10):
        print('\nGetting background mask...')
        self.get_background_mask_level(desired_down_sampling=desired_down_sampling, threshold=threshold)

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

    def get_patch(self):
        w = np.random.choice(self.width_available)
        h = np.random.choice(self.height_available)
        patch = self.wsi.read_region(location=(w, h), level=self.level, size=(self.size, self.size)).convert('RGB')
        return patch




###

data_dir = '/media/peter/HDD 1/datasets_peter/Camelyon16/Train/Original/Tumor'
file = os.path.join(data_dir, 'Tumor_001.tif')
mask_file = os.path.join(data_dir, 'Mask_Tumor', 'Tumor_001.tif')

sampler = Random_Slide_Sampler(file, 4, 256)

sampler.print_slide_properties()

sampler.get_background_mask()

import matplotlib.pyplot as plt

mask = sampler.background_mask
plt.imshow(mask)
plt.show()

c = 2
