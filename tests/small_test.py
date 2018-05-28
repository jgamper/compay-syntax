from wsisampler.sampler import Sampler
import matlab
import os
from wsisampler.utils.slide_utils import save_patchframe_patches

engine = matlab.engine.start_matlab()

path = '/media/jevjev/HDD Storage 1/ColonData/Raw/G16-28741_B2LEV1-3G16-28741B21L-1-3_1.matlab_files'
tissue_mask_dir = '/home/jevjev/Dropbox/Projects/ImageSampler/Peters/WholeSlideImage_Sampler/toydir'
# slide = assign_wsi_plus(path, 20, engine)
# tissue_mask = TissueMask(tissue_mask_dir, reference_wsi=slide)


# def show_PIL(pil_im, size=5):
#     '''A function to show PIL images in the notebook.'''
#     plt.figure(figsize=(size,size))
#     plt.imshow(np.asarray(pil_im),cmap='gray')
#     plt.show()
#
# patch = slide.get_patch(w=25000, h=40000, mag=20, size=1000)
# show_PIL(patch)

sampler = Sampler(path, level0=40, tissue_mask_dir=tissue_mask_dir, annotation_dir=None, engine=engine)
sampler.prepare_sampling(magnification=20, patchsize=200)

patchframe = sampler.sample_patches(max_per_class=20, savedir=os.getcwd())
save_patchframe_patches(patchframe, './patches', engine=engine) # look in this directory
