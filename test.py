import os
import pickle
import time
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
print('Found files {}'.format(files))

bg_dir = os.path.join(data_dir, 'background')
mask_dir = os.path.join(data_dir, 'annotation')


def do_file(file):
    sampler = single_sampler.Single_Sampler(wsi_file=file, background_dir=bg_dir, annotation_dir=mask_dir, level0=40.)
    sampler.prepare_sampling(desired_downsampling=downsampling, patchsize=size)
    sampler.sample_patches(max_per_class=per_class, savedir='./patchframes')

###

start=time.time()
for file in files:
    do_file(file)
print('Serial time = {}'.format(time.time()-start))

###

num_cores = multiprocessing.cpu_count()

start=time.time()
Parallel(n_jobs=num_cores)(delayed(do_file)(file) for file in files)
print('Parallel time = {}'.format(time.time()-start))

###

# pickling_off = open('./Tumor_004_patchframe.pickle', 'rb')
# frame = pickle.load(pickling_off)
# pickling_off.close()
#
# print(frame.head(n=10))
