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

    def __init__(self, wsi_file, background_dir, annotation_dir=None, level0=40.):
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
            self.background = NumpyBackround(self.wsi, approx_downsampling=down, threshold=15)
            print('Made background at {}X'.format(self.level0 / self.wsi.level_downsamples[self.background.level]))
            os.makedirs(self.background_dir, exist_ok=1)
            self.pickle_NumpyBackground(savedir=self.background_dir)
        if truth:
            pickling_off = open(string, 'rb')
            self.background = pickle.load(pickling_off)
            self.validate_NumpyBackground()
            pickling_off.close()

        if annotation_dir is not None:
            truth, string = utils.string_in_directory(self.fileID, self.annotation_dir)
            if truth:
                self.annotation = openslide.OpenSlide(string)
            if not truth:
                self.annotation = None
        else:
            self.annotation = None

    def prepare_sampling(self, desired_downsampling, patchsize):
        self.desired_downsampling = desired_downsampling
        self.patchsize = patchsize
        self.level = utils.get_level(self.wsi, self.desired_downsampling, threshold=0.01)
        background_patchsize = self.level_converter(self.patchsize, self.level, self.background.level)
        self.background.add_patchsize(background_patchsize)
        if self.annotation is not None:
            self.annotation_level = utils.get_level(self.annotation, self.desired_downsampling, threshold=0.01)
        self.get_seeds()
        self.width_available = int(self.wsi.dimensions[0] - self.wsi.level_downsamples[self.level] * self.patchsize)
        self.height_available = int(self.wsi.dimensions[1] - self.wsi.level_downsamples[self.level] * self.patchsize)

    def get_seeds(self):
        if self.annotation is None:
            self.class_seeds = None
            self.classes = None
        else:
            down = int(self.level0 / 2.5)  # annotation must have same level 0 as wsi
            temp_level = utils.get_level(self.annotation, desired_downsampling=down, threshold=15)
            downsample = self.annotation.level_downsamples[temp_level]
            low_res = self.annotation.read_region((0, 0), temp_level,
                                                  self.annotation.level_dimensions[temp_level]).convert('L')
            low_res = np.asarray(low_res).copy()
            classes = sorted(list(np.unique(low_res)))
            assert classes[0] == 0
            classes = classes[1:]
            class_seeds = []
            for c in classes:
                mask = (low_res == c)
                nonzero = np.nonzero(mask)
                coordinates = [(int(nonzero[0][i] * downsample), int(nonzero[1][i] * downsample)) for i in
                               range(nonzero[0].shape[0])]
                shuffle(coordinates)  # inplace
                class_seeds.append(coordinates)
            self.class_seeds = class_seeds
            self.classes = classes

    def get_random_patch(self):
        done = 0
        while not done:
            w = np.random.choice(self.width_available)
            h = np.random.choice(self.height_available)
            patch = self.wsi.read_region((w, h), self.level, (self.patchsize, self.patchsize))
            patch = patch.convert('RGB')
            i = self.level_converter(h, 0, self.background.level)
            j = self.level_converter(w, 0, self.background.level)
            background_patch = self.background.data[i:i + self.background.patchsize, j:j + self.background.patchsize]
            background_patch = background_patch.astype(int)
            if np.sum(background_patch) / (self.background.patchsize ** 2) > 0.9:
                done = 1
        info = {'w': w, 'h': h, 'parent': self.wsi_file, 'level': self.level, 'size': self.patchsize}
        return patch, info

    def get_class0_patch(self):
        if self.annotation is None:
            patch, info = self.get_random_patch()
            info['class'] = 0
            return patch, info
        done = 0
        while not done:
            patch, info = self.get_random_patch()
            w, h = info['w'], info['h']
            annotation_patch = self.annotation.read_region((w, h), self.annotation_level,
                                                           (self.patchsize, self.patchsize))
            annotation_patch = annotation_patch.convert('L')
            annotation_patch = np.asarray(annotation_patch).copy()
            annotation_patch = (annotation_patch > 0).astype(int)
            if np.sum(annotation_patch) / (self.patchsize ** 2) < 0.1:
                info['class'] = 0
                done = 1
        return patch, info

    def try_patch_from_seed(self, seed, seedclass):
        h, w = seed
        patch = self.wsi.read_region((w, h), self.level, (self.patchsize, self.patchsize))
        patch = patch.convert('RGB')

        i = self.level_converter(h, 0, self.background.level)
        j = self.level_converter(w, 0, self.background.level)
        background_patch = self.background.data[i:i + self.background.patchsize, j:j + self.background.patchsize]
        background_patch = background_patch.astype(int)
        if np.sum(background_patch) / (self.background.patchsize ** 2) < 0.9:
            print('Patch rejected. Too much background.')
            return None, None

        annotation_patch = self.annotation.read_region((w, h), self.annotation_level, (self.patchsize, self.patchsize))
        annotation_patch = annotation_patch.convert('L')
        annotation_patch = np.asarray(annotation_patch).copy()
        mask = (annotation_patch != seedclass).astype(int)
        if np.sum(mask) / (self.patchsize ** 2) > 0.9:
            print('Patch rejected. Too much of other classes.')
            return None, None

        info = {
            'w': w,
            'h': h,
            'parent': self.wsi_file,
            'size': self.patchsize,
            'level': self.level,
            'class': seedclass
        }
        return patch, info

    def sample_patches(self, max_per_class=100, savedir=os.getcwd()):
        frame = pd.DataFrame(data=None, columns=['w', 'h', 'class', 'parent', 'level', 'size'])
        # get class0 patches
        for i in range(max_per_class):
            _, info = self.get_class0_patch()
            frame = frame.append(info, ignore_index=1)

        # get other patches, if they exist
        if self.annotation is not None and self.classes is not None:
            for i, c in enumerate(self.classes):
                seeds = self.class_seeds[i]
                for j, seed in enumerate(seeds):
                    _, info = self.try_patch_from_seed(seed, c)
                    if info is not None:
                        frame = frame.append(info, ignore_index=1)
                    if j >= (max_per_class - 1):
                        break

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

    def __init__(self, parent_wsi, approx_downsampling, threshold=15):
        self.level = utils.get_level(parent_wsi, desired_downsampling=approx_downsampling, threshold=threshold)
        self.data = utils.generate_background_mask(parent_wsi, self.level)

    def add_patchsize(self, x):
        self.patchsize = x
