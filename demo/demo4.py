import os
from modules import slide_sampler,utils
import pandas as pd

###

data_dir = '/home/peter/Dropbox/publish-final/WSI_sampler_data'

file = os.path.join(data_dir, 'Tumor_004.tif')
mask_file = os.path.join(data_dir, 'Tumor_004_bgmask.tif')

###

sampler = slide_sampler.Slide_Sampler(wsi_file=file, desired_downsampling=4, size=256)

###

sampler.pickle_load_background_mask(file='./bgmask.pickle')

sampler.add_annotation_mask(annotation_mask_file=mask_file)

###

sampler.get_basic_patchframe(number_patches=100)

frame = pd.read_pickle(path='./patchframe.pickle')

print(frame.head(n=10))

###

utils.save_patchframe_patches(frame_path='./patchframe.pickle',save_dir='./patches')