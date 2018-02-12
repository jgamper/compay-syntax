"""
single_sampler module
"""

import openslide
import os
import numpy as np
from skimage import filters, color
from skimage.morphology import disk
from skimage.morphology import opening, dilation, closing
from PIL import Image
import pickle
import pandas as pd
from modules import utils


class Single_Sampler(object):

    def __init__(self, wsi_file, background_dir, annotation_dir, level0=40.):
        self.wsi_file = wsi_file
        self.background_dir = background_dir
        self.annotation_dir = annotation_dir
        self.level0 = level0

        self.fileID = os.path.splitext(os.path.basename(self.wsi_file))[0]
        self.wsi = openslide.OpenSlide(self.wsi_file)

        truth, string = utils.string_in_directory(self.fileID, self.background_dir)
        if not truth:
            print('Background object not found. Generating now.')
            temp = int(self.level0 / 1.25)
            self.background = NumpyBackround(self.wsi, approx_downsampling=temp, threshold=15)
            print('Made background at {}X'.format(self.level0 / self.wsi.level_downsamples[self.background.level]))
            os.makedirs(self.background_dir, exist_ok=1)
            self.pickle_NumpyBackground(savedir=self.background_dir)
        elif truth:
            pickling_off = open(string, 'rb')
            self.background = pickle.load(pickling_off)
            self.validate_NumpyBackground()
            pickling_off.close()

        truth, string = utils.string_in_directory(self.fileID, self.annotation_dir)
        if truth:
            self.annotation = openslide.OpenSlide(string)
        elif not truth:
            self.annotation = None

    def prepare_sampling(self, desired_downsampling, patchsize):
        self.desired_downsampling = desired_downsampling
        self.patchsize = patchsize
        self.level = utils.get_level(self.wsi, self.desired_downsampling, threshold=0.01)
        self.get_class_coordinates()
        self.width_available = int(self.wsi.dimensions[0] - self.wsi.level_downsamples[self.level] * self.patchsize)
        self.height_available = int(self.wsi.dimensions[1] - self.wsi.level_downsamples[self.level] * self.patchsize)

    def get_class_coordinates(self):
        if self.annotation is None:
            self.class_coordinates = None
            self.classes = None
            return
        temp = int(self.level0 / 5.)  # annotation must have same level 0 as wsi
        level = utils.get_level(self.annotation, desired_downsampling=temp, threshold=15)
        downsample = self.annotation.level_downsamples[level]
        low_res = self.annotation.read_region((0, 0), level, self.annotation.level_dimensions[level]).format('L')
        low_res = np.asarray(low_res).copy()
        classes = np.unique(low_res)
        class_coordinates = []
        for c in classes:
            mask = (low_res == c)
            nonzero = np.nonzero(mask)
            if len(nonzero) != 2:
                raise Exception('Should have length of two')
            coordinates = [(int(nonzero[0][i] * downsample), int(nonzero[1][i] * downsample)) for i in
                           range(nonzero[0].shape[0])]
            class_coordinates.append(coordinates)
        self.class_coordinates = class_coordinates
        self.classes = classes

    def get_random_patch(self):
        done = 0
        while not done:
            w = np.random.choice(self.width_available)
            h = np.random.choice(self.height_available)
            patch = self.wsi.read_region(location=(w, h), level=self.level, size=(self.patchsize, self.patchsize))
            patch = patch.convert('RGB')
            i = self.level_converter(h, 0, self.background.level)
            j = self.level_converter(w, 0, self.background.level)
            background_patchsize = self.level_converter(self.size, self.level, self.background.level)
            background_patch = self.background.data[i:i + background_patchsize, j:j + background_patchsize].astype(int)
            if np.sum(background_patch) / (background_patchsize ** 2) > 0.9:
                done = 1
        info = {'w': w, 'h': h, 'parent': self.wsi_file, 'level': self.level, 'size': self.size}
        return patch, info

    def get_class0_patch(self):
        done = 0
        if self.annotation is None:
            return self.get_random_patch()
        annotation_level = utils.get_level(self.annotation, self.desired_downsampling, threshold=0.01)
        while not done:
            patch, info = self.get_random_patch()
            w, h = info['w'], info['h']
            annotation_patch = self.annotation.read_region(location=(w, h), level=annotation_level,
                                                           size=(self.patchsize, self.patchsize))
            annotation_patch.convert('L')
            annotation_patch = np.asarray(annotation_patch).copy()
            if np.sum(annotation_patch) / (self.patchsize ** 2) < 0.1:
                info['class'] = 0
                done = 1
        return patch, info

    def sample_patches(self, max_per_class=1000):
        pass

    def pickle_NumpyBackground(self, savedir=os.getcwd()):
        if not isinstance(self.background, NumpyBackround):
            raise Exception('Only call this method when using a NumpyBackground')
        filename = os.path.join(savedir, self.fileID + '_NumpyBackground.pickle')
        print('Pickling NumpyBackground to {}'.format(filename))
        pickling_on = open(filename, 'wb')
        pickle.dump(self.background, pickling_on)
        pickling_on.close()

    def validate_NumpyBackground(self):
        if self.wsi.level_dimensions[self.background.level][0] != self.background.data.shape[1]:
            raise Exception('Error unpickling background mask')
        if self.wsi.level_dimensions[self.background.level][1] != self.background.data.shape[0]:
            raise Exception('Error unpickling background mask')

    def level_converter(self, x, lvl_in, lvl_out):
        return int(x * self.wsi.level_downsamples[lvl_in] / self.wsi.level_downsamples[lvl_out])


###

class NumpyBackround(object):

    def __init__(self, parent_wsi, approx_downsampling, threshold=15):
        self.level = utils.get_level(parent_wsi, desired_downsampling=approx_downsampling, threshold=threshold)
        self.data = utils.generate_background_mask(parent_wsi, self.level)
