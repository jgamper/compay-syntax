import os
import pickle
import time
from modules import single_sampler

###

data_dir = '/home/peter/Dropbox/publish-final/WSI_sampler_data'

file = os.path.join(data_dir, 'Tumor_004.tif')
bg_dir = os.path.join(data_dir, 'background')
mask_dir = os.path.join(data_dir, 'annotation')

###

sampler = single_sampler.Single_Sampler(wsi_file=file, background_dir=bg_dir, annotation_dir=mask_dir, level0=40)

###

sampler.prepare_sampling(desired_downsampling=4, patchsize=256)

sampler.get_tissue_seeds()