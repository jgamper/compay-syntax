"""
Sampler module.
"""

import os
import numpy as np
import pandas as pd
from random import shuffle

from .slides.assign import assign_wsi_plus
from .tissuemask import TissueMask
from .annotation import Annotation
from wsisampler.utils.misc_utils import item_in_directory


class Sampler(object):

    def __init__(self, wsi_file, level0, tissue_mask_dir, annotation_dir=None, engine=None):
        """
        Sampler object.

        :param wsi_file: path to a WSI file
        :param level0: 'Magnification' at level 0 (often 40X). If 'infer' we attempt to get from metadata.
        :param tissue_mask_dir: directory where we do/will store tissue masks.
        :param annotation_dir: directory where we keep annotations. \
            NOTE: We can specify a value even if no annotation is present for this particular slide.
        """
        self.wsi_file = wsi_file
        self.wsi = assign_wsi_plus(wsi_file, level0, engine)
        self.tissue_mask_dir = tissue_mask_dir
        self.annotation_dir = annotation_dir

        # Add tissue mask.
        self.tissue_mask = TissueMask(search_dir=tissue_mask_dir, reference_wsi=self.wsi)

        # Add annotation, if present
        if annotation_dir is None:
            self.annotation = None
        else:
            truth, filename = item_in_directory(self.wsi.ID, self.annotation_dir)
            if not truth:
                print('No annotation mask found. Skipping.')
                self.annotation = None
            elif truth:
                print('Annotation mask found. Loading.')
                self.annotation = Annotation(filename, self.wsi)

    def prepare_sampling(self, magnification, patchsize):
        """
        Prepare to sample patches.

        :param magnification:
        :param patchsize:
        :return:
        """
        self.mag = magnification
        self.patchsize = patchsize

        self.rejected = 0  # to count how many patches we reject.

        self._get_classes_and_seeds()  # get classes and approximate coordinates to 'seed' the patch sampling process.

    def sample_patches(self, max_per_class=100, savedir=os.getcwd()):
        """
        Sample patches and save in a patchframe.

        :param max_per_class: maximum number of patches per class
        :param savedir: where to save patchframe
        """
        frame = pd.DataFrame(data=None, columns=['id', 'w', 'h', 'class', 'mag', 'size', 'parent', 'lvl0'])

        for i, c in enumerate(self.class_list):
            seeds = self.class_seeds[i]
            for j, seed in enumerate(seeds):
                _, info = self._class_c_patch_i(c, j)
                if info is not None:
                    frame = frame.append(info, ignore_index=1)
                if j >= (max_per_class - 1):
                    break

        print('Rejected {} patches for file {}'.format(self.rejected, self.wsi.ID))

        os.makedirs(savedir, exist_ok=1)
        filename = os.path.join(savedir, self.wsi.ID + '_patchframe.pickle')
        print('Saving patchframe to {}'.format(filename))
        frame.to_pickle(filename)

        return frame

    ###

    def _get_classes_and_seeds(self):
        """
        Get classes and approximate coordinates to 'seed' the patch sampling process.
        Builds the objects self.class_list and self.class_seeds.
        """
        # Do class 0 i.e. unannotated first.
        mask = self.tissue_mask.data
        nonzero = np.nonzero(mask)
        factor = self.wsi.level_downsamples[self.tissue_mask.level]
        N = nonzero[0].size
        coordinates = [(int(nonzero[0][i] * factor), int(nonzero[1][i] * factor)) for i in range(N)]
        shuffle(coordinates)
        self.class_list = [0]
        self.class_seeds = [coordinates]

        # If no annotation we're done.
        if self.annotation is None:
            return

        # Now add other classes.
        annotation_low_res, factor = self.annotation.get_low_res_numpy()
        classes = sorted(list(np.unique(annotation_low_res)))

        assert classes[0] == 0
        classes = classes[1:]

        for c in classes:
            mask = (annotation_low_res == c)
            nonzero = np.nonzero(mask)
            N = nonzero[0].size
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
        patch = self.wsi.get_patch(w, h, self.mag, self.patchsize)

        tissue_mask_patch = self.tissue_mask.get_patch(w, h, self.mag, self.patchsize)
        if np.sum(tissue_mask_patch) / np.prod(tissue_mask_patch.shape) < 0.9:
            self.rejected += 1
            return None, None

        info = {
            'w': w,
            'h': h,
            'parent': self.wsi_file,
            'size': self.patchsize,
            'mag': self.mag,
            'class': c,
            'id': self.wsi.ID,
            'lvl0': self.wsi.level0
        }

        # If no annotation we're done.
        if self.annotation is None:
            return patch, info

        annotation_patch = self.annotation.get_patch(w, h, self.mag, self.patchsize)
        annotation_patch = np.asarray(annotation_patch)
        mask = (annotation_patch == c).astype(float)
        if np.sum(mask) / np.prod(mask.shape) < 0.9:
            self.rejected += 1
            return None, None

        return patch, info
