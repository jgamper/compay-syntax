import os
from modules import utils
import single_sampler
import pandas as pd
import numpy as np
import pickle

import openslide

###

data_dir = '/home/peter/Dropbox/publish-final/WSI_sampler_data'

file = os.path.join(data_dir, 'Tumor_004.tif')
mask_file = os.path.join(data_dir, 'Tumor_004_mask.tif')

###

# sampler = single_sampler.Single_Sampler(wsi_file=file, desired_downsampling=4, size=256)
# sampler.pickle_NumpyBackground()

###

sampler = single_sampler.Single_Sampler(wsi_file=file, desired_downsampling=4, size=256,
                                        background_file='./Tumor_004_NumpyBackground.pickle', annotation_file=mask_file)

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
