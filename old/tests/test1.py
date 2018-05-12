"""
Make a sampler and generate backgrounds. Visualize background and annotation.
"""

import os
import glob

import sampler

###

data_dir = '/home/peter/Dropbox/SharedMore/WSI_sampler'

###

files = glob.glob(os.path.join(data_dir, '*.tif'))

bg_dir = './backgrounds'
mask_dir = os.path.join(data_dir, 'annotation')

###

for file in files:
    sampler = sampler.Sampler(wsi_file=file, tissue_mask_dir=bg_dir, annotation_dir=mask_dir, level0=40)
    sampler.save_background_visualization(savedir='./bg_vis')
    if sampler.annotation is not None:
        sampler.save_annotation_visualization(savedir='./annotation_vis')
