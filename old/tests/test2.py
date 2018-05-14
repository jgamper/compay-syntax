"""
Make a patchframe and visualize the patches. Also use parallel computation.
"""

import os
import glob
import pandas as pd

from joblib import Parallel, delayed
import multiprocessing

from modules import misc

###

data_dir = '/home/peter/Dropbox/publish-final/WSI_sampler_data'

###

downsampling = 4.
size = 256
per_class = 20

###

files = glob.glob(os.path.join(data_dir, '*.tif'))

bg_dir = './backgrounds'
mask_dir = os.path.join(data_dir, 'annotation')

patchframe_dir = './patchframes'


###

def do_file(file):
    sampler = sampler.Sampler(wsi_file=file, tissue_mask_dir=bg_dir, annotation_dir=mask_dir, level0=40.)
    sampler.prepare_sampling(desired_downsampling=downsampling, patchsize=size)
    sampler.sample_patches(max_per_class=per_class, savedir=patchframe_dir, verbose=1)


num_cores = multiprocessing.cpu_count()
Parallel(n_jobs=num_cores)(delayed(do_file)(file) for file in files)

###

files = glob.glob(os.path.join(patchframe_dir, '*.pickle'))

frame = pd.DataFrame()

for file in files:
    frame = frame.append(pd.read_pickle(file), ignore_index=1)

print('\n', frame.head())

###

misc.save_patchframe_patches(frame)