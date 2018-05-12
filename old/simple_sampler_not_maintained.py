from __future__ import division

import openslide
import os
import glob
import numpy as np
from skimage import filters, color
from skimage.morphology import disk
from skimage.morphology import opening, closing, dilation
from PIL import Image
from random import shuffle
import pandas as pd


###

class Sampler(object):

    def __init__(self, wsi_file, tissue_mask_dir=os.path.join(os.getcwd(), 'tissue_masks')):
        """
        A WSI sampler object
        :param wsi_file: path to openslide readable WSI
        :param tissue_mask_dir: a directory where tissue masks are/will-be stored
        """
        self.wsi_file = wsi_file
        self.tissue_mask_dir = tissue_mask_dir

        self.wsi = openslide.OpenSlide(self.wsi_file)
        self.objective = float(self.wsi.properties['openslide.objective-power'])  # magnification at level 0
        self.fileID = os.path.splitext(os.path.basename(self.wsi_file))[0]

        self.magnifications = [self.objective / downsample for downsample in self.wsi.level_downsamples]

        # add tissue mask
        self.tissue_mask_level = self.get_level(magnification=1.25, threshold=5)
        truth, string = self.item_in_directory(self.fileID, self.tissue_mask_dir)
        if not truth:
            print('Tissue mask not found. Generating now.')
            self.tissue_mask = self.generate_tissue_mask(self.wsi, self.tissue_mask_level)
            os.makedirs(self.tissue_mask_dir, exist_ok=1)
            filename = self.fileID + '_tissue_mask.npy'
            filepath = os.path.join(self.tissue_mask_dir, filename)
            np.save(filepath, self.tissue_mask)
        if truth:
            self.tissue_mask = np.load(string)
            # sanity checks
            if self.wsi.level_dimensions[self.tissue_mask_level][0] != self.tissue_mask.shape[1]:
                raise Exception('Error loading tissue mask')
            if self.wsi.level_dimensions[self.tissue_mask_level][1] != self.tissue_mask.shape[0]:
                raise Exception('Error loading tissue mask')

        # add a visualization of tissue mask for inspection
        self.tissue_mask_visual_dir = os.path.join(self.tissue_mask_dir, 'visual')
        truth, _ = self.item_in_directory(self.fileID, self.tissue_mask_visual_dir)
        if not truth:
            print('Adding tissue mask visualization')
            self.add_tissue_mask_visualization()

    def prepare_sampling(self, magnification, patchsize):
        self.patchsize = patchsize

        # is the desired magnification available? If not take a higher magnification and resize.
        truths = [m > (magnification - 0.01) for m in self.magnifications]
        self.level = self.index_last_non_zero(truths)
        self.magnification = self.magnifications[self.level]
        ratio = self.magnification / magnification
        self.sample_patchsize = int(round(patchsize * ratio))
        self.resize = abs(ratio - 1) > 0.01

        self.tissue_mask_patchsize = self.level_converter(self.sample_patchsize, self.level, self.tissue_mask_level)

    def build_patchframe(self, n_patches):
        print('Building patchframe')
        # approximate coordinates of patches
        nonzero = np.nonzero(self.tissue_mask)
        factor = self.wsi.level_downsamples[self.tissue_mask_level]
        N = nonzero[0].shape[0]
        coordinates = [(int(round(nonzero[0][i] * factor)), int(round(nonzero[1][i] * factor))) for i in range(N)]
        shuffle(coordinates)
        self.coordinates = coordinates

        # blank patchframe
        patchframe = pd.DataFrame(columns=['id', 'w', 'h', 'level', 'sample_size', 'parent', 'resize', 'size'])

        # fill the patchframe. Add patch if over 95% is tissue.
        n_accepted = 0
        n_rejected = 0
        while n_accepted < n_patches:
            n_tried = n_accepted + n_rejected
            h, w = self.coordinates[n_tried]
            i = self.level_converter(h, 0, self.tissue_mask_level)
            j = self.level_converter(w, 0, self.tissue_mask_level)
            tissue_mask_patch = self.tissue_mask[i:i + self.tissue_mask_patchsize, j:j + self.tissue_mask_patchsize]
            tissue_mask_patch = tissue_mask_patch.astype(int)
            if np.sum(tissue_mask_patch) / (self.tissue_mask_patchsize ** 2) > 0.95:
                info = {'id': self.fileID, 'w': w, 'h': h, 'level': self.level, 'sample_size': self.sample_patchsize,
                        'parent': self.wsi_file, 'resize': int(self.resize), 'size': self.patchsize}
                patchframe = patchframe.append(info, ignore_index=1)
                n_accepted += 1
            else:
                n_rejected += 1
        print('Rejected {} patches'.format(n_rejected))
        self.patchframe = patchframe

    def sample_patches_via_patchframe(self, savedir=os.path.join(os.getcwd(), 'patches')):
        os.makedirs(savedir, exist_ok=1)
        print('Saving hard copies of patches in patchframe to {}'.format(savedir))
        for i in range(self.patchframe.shape[0]):
            info = self.patchframe.ix[i]
            patch = self.wsi.read_region(location=(info['w'], info['h']), level=info['level'],
                                         size=(info['sample_size'], info['sample_size']))
            patch = patch.convert('RGB')
            if info['resize']:
                patch.thumbnail((info['size'], info['size']))
            filename = os.path.join(savedir, '{}_patch{}.png'.format(info['id'], i))
            patch.save(filename)

    ###

    def get_level(self, magnification, threshold=0.01):
        """
        Get the level corresponding to a specified magnification
        :param magnification:
        :param threshold:
        :return:
        """
        diffs = [abs(magnification - self.magnifications[i]) for i in range(len(self.magnifications))]
        minimum = min(diffs)
        if minimum > threshold:
            raise Exception(
                'Failed to find a suitable level\nAvailable magnifications are \n{}'.format(self.magnifications))
        level = diffs.index(minimum)
        return level

    def add_tissue_mask_visualization(self):
        """
        A hacky way to visualize the tissue mask
        :return:
        """
        size = 1000
        savedir = self.tissue_mask_visual_dir
        os.makedirs(savedir, exist_ok=1)
        file_name = os.path.join(savedir, self.fileID + '_tissue_mask.png')

        bg = Image.fromarray(self.tissue_mask.astype(float))  # a resize hack...
        bg.thumbnail(size=(size, size))
        bg = np.asarray(bg).copy()

        dilated = dilation(bg, disk(8))
        contour = np.logical_xor(dilated, bg).astype(np.bool)

        wsi_thumb = np.asarray(self.wsi.get_thumbnail(size=(size, size))).copy()
        wsi_thumb[contour] = 0

        pil = Image.fromarray(wsi_thumb)
        pil.save(file_name)

    def level_converter(self, x, lvl_in, lvl_out):
        """
        Convert a length/coordinate 'x' from lvl_in to lvl_out
        :param x:
        :param lvl_in:
        :param lvl_out:
        :return:
        """
        return int(round(x * self.wsi.level_downsamples[lvl_in] / self.wsi.level_downsamples[lvl_out]))

    ###

    @staticmethod
    def item_in_directory(search_key, directory):
        """
        Is an item in a directory?
        Search using a search_key
        :param search_key:
        :param directory:
        :return:
        """
        if not os.path.isdir(directory):
            return 0, 'Not a directory'
        items_in_dir = glob.glob(os.path.join(directory, '*'))
        for item in items_in_dir:
            if search_key in item:
                return 1, item
        return 0, 'Not found'

    @staticmethod
    def generate_tissue_mask(wsi, level, disk_radius=10):
        """
        Generate a tissue mask for a WSI (a binary np.ndarray)
        This is achieved by otsu thresholding on the saturation channel
        followed by morphological closing and opening to remove noise.
        :param wsi:
        :param level:
        :param disk_radius:
        :return:
        """
        low_res = wsi.read_region(location=(0, 0), level=level, size=wsi.level_dimensions[level])
        low_res = low_res.convert('RGB')
        low_res_numpy = np.asarray(low_res).copy()
        low_res_numpy_hsv = color.convert_colorspace(low_res_numpy, 'RGB', 'HSV')
        saturation = low_res_numpy_hsv[:, :, 1]
        theshold = filters.threshold_otsu(saturation)
        high_saturation = (saturation > theshold)
        disk_object = disk(disk_radius)
        mask = closing(high_saturation, disk_object)  # remove 'pepper'
        mask = opening(mask, disk_object)  # remove 'salt'
        return mask

    @staticmethod
    def index_last_non_zero(x):
        """
        Index of last non-zero element of list
        e.g. for [1,4,3,7,0,0,0,...] would return 3
        :param x:
        :return:
        """
        for idx in range(len(x)):
            if not x[idx]:
                return idx - 1
