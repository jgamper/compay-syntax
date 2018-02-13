import os
import glob

from joblib import Parallel, delayed
import multiprocessing

from modules import single_sampler

###

data_dir = '/home/peter/Dropbox/publish-final/WSI_sampler_data'

###

downsampling = 4.
size = 256
per_class = 100

###

files = glob.glob(os.path.join(data_dir, '*.tif'))

bg_dir = os.path.join(data_dir, 'background')
mask_dir = os.path.join(data_dir, 'annotation')


###

def do_file(file):
    sampler = single_sampler.Single_Sampler(wsi_file=file, background_dir=bg_dir, annotation_dir=mask_dir, level0=40.)
    sampler.prepare_sampling(desired_downsampling=downsampling, patchsize=size)
    sampler.sample_patches(max_per_class=per_class, savedir='./patchframes', verbose=1)


num_cores = multiprocessing.cpu_count()
Parallel(n_jobs=num_cores)(delayed(do_file)(file) for file in files)
