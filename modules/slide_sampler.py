"""
Module for sampling from a slide
"""

import openslide
import os
import numpy as np
from skimage import filters, color
from skimage.morphology import disk
from skimage.morphology import opening, dilation, closing
from PIL import Image


class Slide_Sampler(object):
    """
    A WSI patch sampler.

    Important are:
    self.wsi - an OpenSlide object of the multiresolution WSI specified by wsi_file.
    self.background_mask - a background mask (generate with self.add_background_mask()). Stored as a numpy array where 1.0 denotes tissue.
    """

    def __init__(self, wsi_file, desired_downsampling, size):
        self.wsi_file = wsi_file
        self.fileID = os.path.splitext(os.path.basename(self.wsi_file))[0]
        self.wsi = openslide.OpenSlide(self.wsi_file)
        self.desired_downsampling = desired_downsampling
        self.size = size
        self.level, self.downsampling = self.get_level_and_downsampling(desired_downsampling, 0.1)
        self.width_available = int(self.wsi.dimensions[0] - self.downsampling * size)
        self.height_available = int(self.wsi.dimensions[1] - self.downsampling * size)
        print('\nInitialized Slide_Sampler for slide {}'.format(self.fileID))
        print('Patches will be sampled at level {0} (downsampling of {1}), with size {2} x {2}.'.format(self.level,
                                                                                                        self.downsampling,
                                                                                                        self.size))

    def get_level_and_downsampling(self, desired_downsampling, threshold):
        """
        Get the level and downsampling for a desired downsampling.
        A threshold is used to allow for not exactly equal desired and true downsampling.
        If an appropriate level is not found an exception is raised.

        :param desired_downsampling:
        :param threshold:
        :return:
        """
        diffs = [abs(desired_downsampling - self.wsi.level_downsamples[i]) for i in
                 range(len(self.wsi.level_downsamples))]
        minimum = min(diffs)
        if minimum > threshold:
            raise Exception(
                '\nLevel not found for desired downsampling.\nAvailable downsampling factors are\n{}'.format(
                    self.wsi.level_downsamples))
        level = diffs.index(minimum)
        return level, self.wsi.level_downsamples[level]

    def add_background_mask(self, desired_downsampling=32, threshold=4, disk_radius=10):
        """
        Add a background mask. That is a binary (0.0 vs 1.0), downsampled image where 1.0 denotes a tissue region.
        This is achieved by otsu thresholding on the saturation channel followed by morphological closing and opening to remove noise.
        The mask desired downsampling factor has a default of 32. For a WSI captured at 40X this corresponds to 1.25X.
        A moderate threshold is used to account for the fact that the desired downsampling may not be available.
        If an appropriate level is not found an exception is raised.
        :param desired_downsampling:
        :param threshold:
        :param disk_radius: for morphological opening
        :return:
        """
        print('\nAdding background mask.')
        self.background_mask_level, self.background_mask_downsampling = self.get_level_and_downsampling(
            desired_downsampling, threshold)
        low_res = self.wsi.read_region(location=(0, 0), level=self.background_mask_level,
                                       size=self.wsi.level_dimensions[self.background_mask_level]).convert('RGB')
        low_res_numpy = np.asarray(low_res).copy()
        low_res_numpy_hsv = color.convert_colorspace(low_res_numpy, 'RGB', 'HSV')
        saturation = low_res_numpy_hsv[:, :, 1]
        thesh1 = filters.threshold_otsu(saturation)
        high_saturation = (saturation > thesh1)
        selem = disk(disk_radius)
        mask = closing(high_saturation, selem)
        mask = opening(mask, selem)
        self.background_mask = mask.astype(np.float32)
        self.size_at_background_level = self.level_converter(self.size, self.level, self.background_mask_level)
        print('Added background mask at level{} (downsampling of {})'.format(self.background_mask_level,
                                                                             self.background_mask_downsampling))

    def view_background_mask(self, dir=os.getcwd()):
        """
        Save a visualization of the background mask.
        :param dir:
        :return:
        """
        file_name = os.path.join(dir, self.fileID + '_background.png')
        print('\nSaving background mask visualization to {}'.format(file_name))
        dilated = dilation(self.background_mask, disk(25))
        contour = np.logical_xor(dilated, self.background_mask).astype(np.bool)
        low_res = self.wsi.read_region(location=(0, 0), level=self.background_mask_level,
                                       size=self.wsi.level_dimensions[self.background_mask_level]).convert('RGB')
        low_res_numpy = np.asarray(low_res).copy()
        low_res_numpy[contour] = 0
        pil = Image.fromarray(low_res_numpy)
        pil.thumbnail(size=(1500, 1500))
        pil.save(file_name)

    def view_WSI(self, dir=os.getcwd()):
        """
        Save a thumbnail of the WSI
        :param dir:
        :return:
        """
        file_name = os.path.join(dir, self.fileID + '_thumb.png')
        print('\nSaving WSI thumbnail to {}'.format(file_name))
        thumb = self.wsi.get_thumbnail(size=(1500, 1500))
        thumb.save(file_name)

    def get_patch(self):
        """
        Get a random patch from the WSI.
        Accept if over 90% is non-background
        :return:
        """
        done = 0
        while not done:
            w = np.random.choice(self.width_available)
            h = np.random.choice(self.height_available)
            patch = self.wsi.read_region(location=(w, h), level=self.level, size=(self.size, self.size)).convert('RGB')
            i = self.level_converter(h, 0, self.background_mask_level)
            j = self.level_converter(w, 0, self.background_mask_level)
            background_mask_patch = self.background_mask[i:i + self.size_at_background_level,
                                    j:j + self.size_at_background_level]
            if np.sum(background_mask_patch) / (self.size_at_background_level ** 2) > 0.9: done = 1
        return patch

    def print_slide_properties(self):
        """
        Print some WSI properties
        :return:
        """
        print('\nSlide properties.')
        print('Dimensions at level 0:')
        print(self.wsi.dimensions)
        print('Number of levels:')
        print(self.wsi.level_count)
        print('with downsampling factors:')
        print(self.wsi.level_downsamples)

    def level_converter(self, x, lvl_in, lvl_out, round=1):
        """
        Convert a coordinate 'x' at lvl_in from lvl_in to lvl_out
        :param x:
        :param lvl_in:
        :param lvl_out:
        :return:
        """
        if round:
            return np.floor(x * self.wsi.level_downsamples[lvl_in] / self.wsi.level_downsamples[lvl_out]).astype(
                np.uint32)
        else:
            return x * self.wsi.level_downsamples[lvl_in] / self.wsi.level_downsamples[lvl_out]
