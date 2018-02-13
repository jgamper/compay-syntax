"""
single_sampler module
"""

import openslide
import os
import numpy as np
import pickle
import pandas as pd
from random import shuffle

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
            down = int(self.level0 / 1.25)
            self.background = NumpyBackround(self.wsi, approx_downsampling=down, threshold=20)
            os.makedirs(self.background_dir, exist_ok=1)
            self.pickle_NumpyBackground(savedir=self.background_dir)
        if truth:
            pickling_off = open(string, 'rb')
            self.background = pickle.load(pickling_off)
            self.validate_NumpyBackground()
            pickling_off.close()

        if annotation_dir == None:
            self.annotation = None
        else:
            truth, string = utils.string_in_directory(self.fileID, self.annotation_dir)
            if truth:
                self.annotation = openslide.OpenSlide(string)
            if not truth:
                self.annotation = None

    def prepare_sampling(self, desired_downsampling, patchsize):
        self.desired_downsampling = desired_downsampling
        self.patchsize = patchsize
        self.level = utils.get_level(self.wsi, self.desired_downsampling, threshold=0.01)

        background_patchsize = self.level_converter(self.patchsize, self.level, self.background.level)
        self.background.add_patchsize(background_patchsize)

        if self.annotation is not None:
            self.annotation_level = utils.get_level(self.annotation, self.desired_downsampling, threshold=0.01)

        self.get_classes_and_seeds()

        self.width_available = int(self.wsi.dimensions[0] - self.wsi.level_downsamples[self.level] * self.patchsize)
        self.height_available = int(self.wsi.dimensions[1] - self.wsi.level_downsamples[self.level] * self.patchsize)

    def get_classes_and_seeds(self):
        mask = self.background.data
        nonzero = np.nonzero(mask)
        factor = self.wsi.level_downsamples[self.background.level]
        N = nonzero[0].shape[0]
        coordinates = [(int(nonzero[0][i] * factor), int(nonzero[1][i] * factor)) for i in range(N)]
        shuffle(coordinates)
        self.class_list = [0]
        self.class_seeds = [coordinates]

        if self.annotation is None:
            return

        down = int(self.level0 / 2.5)  # annotation should have same resolution at level 0 as WSI
        level = utils.get_level(self.annotation, desired_downsampling=down, threshold=20)
        annotation_low_res = self.annotation.read_region((0, 0), level, self.annotation.level_dimensions[level])
        annotation_low_res = annotation_low_res.convert('L')
        annotation_low_res = np.asarray(annotation_low_res).copy()
        classes = sorted(list(np.unique(annotation_low_res)))
        assert classes[0] == 0
        classes = classes[1:]
        for c in classes:
            mask = (annotation_low_res == c)
            nonzero = np.nonzero(mask)
            factor = self.annotation.level_downsamples[level]
            N = nonzero[0].shape[0]
            coordinates = [(int(nonzero[0][i] * factor), int(nonzero[1][i] * factor)) for i in range(N)]
            shuffle(coordinates)
            self.class_list.append(c)
            self.class_seeds.append(coordinates)

    def class_c_patch_i(self, c, i):
        idx = self.class_list.index(c)
        h, w = self.class_seeds[idx][i]
        patch = self.wsi.read_region((w, h), self.level, (self.patchsize, self.patchsize))
        patch = patch.convert('RGB')

        i = self.level_converter(h, 0, self.background.level)
        j = self.level_converter(w, 0, self.background.level)
        background_patch = self.background.data[i:i + self.background.patchsize, j:j + self.background.patchsize]
        background_patch = background_patch.astype(int)
        if not np.sum(background_patch) / (self.background.patchsize ** 2) > 0.9:
            # print('Patch rejected. Too much background.')
            return None, None

        info = {
            'w': w,
            'h': h,
            'parent': self.wsi_file,
            'size': self.patchsize,
            'level': self.level,
            'class': c
        }

        if self.annotation is None:
            return patch, info

        annotation_patch = self.annotation.read_region((w, h), self.annotation_level, (self.patchsize, self.patchsize))
        annotation_patch = annotation_patch.convert('L')
        annotation_patch = np.asarray(annotation_patch).copy()
        mask = (annotation_patch != c).astype(int)
        if np.sum(mask) / (self.patchsize ** 2) > 0.9:
            # print('Patch rejected. Too much of other classes.')
            return None, None

        return patch, info

    def sample_patches(self, max_per_class=100, savedir=os.getcwd()):
        frame = pd.DataFrame(data=None, columns=['w', 'h', 'class', 'parent', 'level', 'size'])

        for i, c in enumerate(self.class_list):
            seeds = self.class_seeds[i]
            for j, seed in enumerate(seeds):
                _, info = self.class_c_patch_i(c, j)
                if info is not None:
                    frame = frame.append(info, ignore_index=1)
                if j >= (max_per_class - 1):
                    break

        os.makedirs(savedir, exist_ok=1)
        filename = os.path.join(savedir, self.fileID + '_patchframe.pickle')
        print('Saving patchframe to {}'.format(filename))
        frame.to_pickle(filename)

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

    def __init__(self, parent_wsi, approx_downsampling, threshold=20):
        self.level = utils.get_level(parent_wsi, desired_downsampling=approx_downsampling, threshold=threshold)
        self.data = utils.generate_background_mask(parent_wsi, self.level)

    def add_patchsize(self, x):
        self.patchsize = x

###

# class SeedObject(object):
#
#     def __init__(self, wsi, npBackground, annotation, level0):
#         mask = npBackground.data
#         nonzero = np.nonzero(mask)
#         factor = wsi.level_downsamples[npBackground.level]
#         N = nonzero[0].shape[0]
#         coordinates = [(int(nonzero[0][i] * factor), int(nonzero[1][i] * factor)) for i in range(N)]
#         shuffle(coordinates)
#         self.class_list = [0]
#         self.class_seeds = [coordinates]
#
#         if annotation is None:
#             return
#
#         down = int(level0 / 2.5)
#         level = utils.get_level(annotation, desired_downsampling=down, threshold=20)
#         annotation_low_res = annotation.read_region((0, 0), level, annotation.level_dimensions[level])
#         annotation_low_res = annotation_low_res.convert('L')
#         annotation_low_res = np.asarray(annotation_low_res).copy()
#         classes = sorted(list(np.unique(annotation_low_res)))
#         assert classes[0] == 0
#         classes = classes[1:]
#         for c in classes:
#             mask = (annotation_low_res == c)
#             nonzero = np.nonzero(mask)
#             factor = annotation.level_downsamples[level]
#             N = nonzero[0].shape[0]
#             coordinates = [(int(nonzero[0][i] * factor), int(nonzero[1][i] * factor)) for i in range(N)]
#             shuffle(coordinates)
#             self.class_list.append(c)
#             self.class_seeds.append(coordinates)
