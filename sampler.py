"""
Sampler module.
"""

import openslide
import os
import numpy as np
import pickle
import pandas as pd
from random import shuffle
from skimage.morphology import disk, dilation
from PIL import Image

from modules import tissue_mask_generation as tmg
from modules import utils as ut


class Sampler(object):

    def __init__(self, wsi_file, tissue_mask_dir, annotation_dir, level0_overide=None):
        """
        :param wsi_file: path to a WSI file
        :param tissue_mask_dir: directory where we do/will store tissue masks
        :param annotation_dir: directory where we keep annotations
        :param level0_overide:
        """
        self.wsi_file = wsi_file
        self.tissue_mask_dir = tissue_mask_dir
        self.annotation_dir = annotation_dir

        self.fileID = os.path.splitext(os.path.basename(self.wsi_file))[0]
        self.wsi = openslide.OpenSlide(self.wsi_file)

        if level0_overide is not None:
            self.level0 = float(level0_overide)
        else:
            self.level0 = float(self.wsi.properties['openslide.objective-power'])
            print('Level 0 found @ {}X'.format(self.level0))

        self.magnifications = [self.level0 / downsample for downsample in self.wsi.level_downsamples]

        # Add tissue mask.
        truth, string = ut.string_in_directory(self.fileID, self.tissue_mask_dir)
        if not truth:
            print('Tissue mask not found. Generating now.')
            self.tml = self.get_level(magnification=1.25, threshold=10.0)  # tissue mask level.
            self.tm = tmg.generate_tissue_mask(self.wsi, self.tml)  # tissue mask (Boolean numpy array).

            # Save for reuse.
            os.makedirs(self.tissue_mask_dir, exist_ok=True)
            filename = os.path.join(self.tissue_mask_dir, self.fileID + '_tm.npy')
            np.save(filename, self.tm)
        if truth:
            print('Tissue mask found. Loading.')
            self.tm = np.load(string)
            # self.tml =

        # # Add annotation, if present
        # if annotation_dir is None:
        #     self.annotation = None
        # else:
        #     truth, string = ut.string_in_directory(self.fileID, self.annotation_dir)
        #     if truth:
        #         self.annotation = openslide.OpenSlide(string)
        #     if not truth:
        #         self.annotation = None

    def prepare_sampling(self, desired_downsampling, patchsize):
        """
        :param desired_downsampling: the desired downsampling. \
        E.g. if level 0 is 40X then a downsampling of 4 is 10X.
        :param patchsize: sample patches of size patchsize x patchsize
        """
        self.desired_downsampling = desired_downsampling
        self.patchsize = patchsize
        self.level = ut.get_level(self.wsi, self.desired_downsampling, threshold=0.01)

        background_patchsize = self.level_converter(self.patchsize, self.level, self.background.level)
        self.background.set_patchsize(background_patchsize)

        if self.annotation is not None:
            self.annotation_level = ut.get_level(self.annotation, self.desired_downsampling, threshold=0.01)

        self._get_classes_and_seeds()  # get classes and approximate coordinates to 'seed' the patch sampling process

        self.rejected = 0  # to count how many patches we reject

    def sample_patches(self, max_per_class=100, savedir=os.getcwd(), verbose=0):
        """
        Sample patches and save in a patchframe
        :param max_per_class: maximum number of patches per class
        :param savedir: where to save patchframe
        :param verbose: report number of rejected patches?
        """
        frame = pd.DataFrame(data=None, columns=['id', 'w', 'h', 'class', 'level', 'size', 'parent'])

        for i, c in enumerate(self.class_list):
            seeds = self.class_seeds[i]
            for j, seed in enumerate(seeds):
                _, info = self._class_c_patch_i(c, j)
                if info is not None:
                    frame = frame.append(info, ignore_index=1)
                if j >= (max_per_class - 1):
                    break
        if verbose:
            print('Rejected {} patches for file {}'.format(self.rejected, self.fileID))
        os.makedirs(savedir, exist_ok=1)
        filename = os.path.join(savedir, self.fileID + '_patchframe.pickle')
        print('Saving patchframe to {}'.format(filename))
        frame.to_pickle(filename)

    ###

    def _get_classes_and_seeds(self):
        """
        Get classes and approximate coordinates to 'seed' the patch sampling process
        """
        # do class 0 i.e. unannotated first
        mask = self.background.data
        nonzero = np.nonzero(mask)
        factor = self.wsi.level_downsamples[self.background.level]
        N = nonzero[0].shape[0]
        coordinates = [(int(nonzero[0][i] * factor), int(nonzero[1][i] * factor)) for i in range(N)]
        shuffle(coordinates)
        self.class_list = [0]
        self.class_seeds = [coordinates]

        # If no annotation we're done
        if self.annotation is None:
            return

        # now add other classes
        down = int(self.level0 / 2.5)  # as near to 2.5X as possible
        level = ut.get_level(self.annotation, desired_downsampling=down, threshold=20)
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

    def _class_c_patch_i(self, c, i):
        """
        Try and get the ith patch of class c. If we reject return (None, None).
        :param c: class
        :param i: index
        :return: (patch, info_dict) or (None, None) if we reject patch.
        """
        idx = self.class_list.index(c)
        h, w = self.class_seeds[idx][i]
        patch = self.wsi.read_region((w, h), self.level, (self.patchsize, self.patchsize))
        patch = patch.convert('RGB')

        i = self.level_converter(h, 0, self.background.level)
        j = self.level_converter(w, 0, self.background.level)
        background_patch = self.background.data[i:i + self.background.patchsize, j:j + self.background.patchsize]
        background_patch = background_patch.astype(int)
        if not np.sum(background_patch) / (self.background.patchsize ** 2) > 0.9:
            self.rejected += 1
            return None, None

        info = {
            'w': w,
            'h': h,
            'parent': self.wsi_file,
            'size': self.patchsize,
            'level': self.level,
            'class': c,
            'id': self.fileID
        }
        # If no annotation we're done
        if self.annotation is None:
            return patch, info

        annotation_patch = self.annotation.read_region((w, h), self.annotation_level, (self.patchsize, self.patchsize))
        annotation_patch = annotation_patch.convert('L')
        annotation_patch = np.asarray(annotation_patch).copy()
        mask = (annotation_patch != c).astype(int)
        if np.sum(mask) / (self.patchsize ** 2) > 0.9:
            self.rejected += 1
            return None, None

        return patch, info

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
        warn = 'Failed to find a suitable level\nAvailable magnifications are \n{}'
        assert minimum < threshold, warn.format(self.magnifications)
        level = diffs.index(minimum)
        return level

    def level_converter(self, x, lvl_in, lvl_out):
        """
        Convert a length/coordinate 'x' from lvl_in to lvl_out
        :param x: a length/coordinate
        :param lvl_in: level to convert from
        :param lvl_out: level to convert to
        :return: New length/coordinate
        """
        return int(x * self.wsi.level_downsamples[lvl_in] / self.wsi.level_downsamples[lvl_out])

    ###

    def save_annotation_visualization(self, savedir=os.getcwd()):
        """
        Save a visualization of the annotation
        :param savedir: where to save to
        """
        size = 3000
        os.makedirs(savedir, exist_ok=1)
        file_name = os.path.join(savedir, self.fileID + '_annotation.png')
        print('\nSaving annotation visualization to {}'.format(file_name))

        annotation = self.annotation.get_thumbnail(size=(size, size)).convert('L')
        annotation = np.asarray(annotation).copy().astype(bool).astype(float)

        dilated = dilation(annotation, disk(10))
        contour = np.logical_xor(annotation, dilated).astype(np.bool)

        wsi_thumb = np.asarray(self.wsi.get_thumbnail(size=(size, size))).copy()
        wsi_thumb[contour] = 0

        pil = Image.fromarray(wsi_thumb)
        pil.save(file_name)


if __name__ == '__main__':
    data_dir = '/home/peter/Dropbox/SharedMore/WSI_sampler'
    file = os.path.join(data_dir, 'Normal_106.tif')
    tm_dir = './tissue_masks'
    annotation_dir = os.path.join(data_dir, 'annotation')

    sampler = Sampler(file, tm_dir, annotation_dir)
