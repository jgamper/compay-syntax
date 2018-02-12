import os
from modules import utils
import single_sampler
import pandas as pd
import numpy as np
import pickle

import openslide

###

data_dir = '/media/peter/HDD 1/datasets_peter/Camelyon16/Train/Tumor'

file = os.path.join(data_dir, 'Tumor_004.tif')
bg_dir = os.path.join(data_dir, 'Background')
mask_dir = os.path.join(data_dir, 'Mask_Tumor')

###

sampler = single_sampler.Single_Sampler(wsi_file=file, desired_downsampling=4, size=256, background_dir=bg_dir,
                                        annotation_dir=mask_dir)

###


# mask = utils.generate_background_mask(sampler.wsi, level=5)
# np.save('./mask.npy',mask)

# sampler.pickle_load_background_mask(file='./demo/Tumor_004_bgmask.pickle')
# sampler.add_annotation_mask(annotation_mask_file=mask_file)
#
# ###
#
# wsi = sampler.wsi
# bg = sampler.background_mask.astype(np.bool)
# ann_mri = sampler.annotation_mask
#
# ###
#
# print(np.unique(bg))
# temp = np.nonzero(bg)
# coords = [(temp[0][i], temp[1][i]) for i in range(temp[0].shape[0])]
#
# ###
#
# print(ann_mri.level_downsamples[5])
#
# ann = ann_mri.read_region((0, 0), 5, ann_mri.level_dimensions[5]).convert('L')
# ann = np.asarray(ann)
# print(np.unique(ann))
# temp = np.nonzero(ann)
# coords2 = [(temp[0][i], temp[1][i]) for i in range(temp[0].shape[0])]
#
# pickling_on = open('./a.pickle', 'wb')
# pickle.dump(coords2, pickling_on)
#
# c = 2
