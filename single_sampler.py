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

    def __init__(self, wsi_file, desired_downsampling, size, background_dir, annotation_dir, level0=40.):
        self.wsi_file = wsi_file
        self.desired_downsampling = desired_downsampling
        self.size = size
        self.background_dir = background_dir
        self.annotation_dir = annotation_dir

        self.fileID = os.path.splitext(os.path.basename(self.wsi_file))[0]
        self.wsi = openslide.OpenSlide(self.wsi_file)
        self.level = utils.get_level(self.wsi, desired_downsampling)

        truth, string = utils.string_in_directory(self.fileID, self.background_dir)
        if not truth:
            print('Background object not found. Generating now.')
            temp = int(level0 / 1.25)
            self.background = NumpyBackround(self.wsi, desired_downsampling=temp, threshold=15)
            print('Made background at {}X'.format(level0 / self.wsi.level_downsamples[self.background.level]))
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


###

class NumpyBackround(object):

    def __init__(self, parent_wsi, desired_downsampling, threshold):
        self.level = utils.get_level(parent_wsi, desired_downsampling, threshold)
        self.data = utils.generate_background_mask(parent_wsi, self.level)
