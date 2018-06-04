# def show_PIL(pil_im, size=5):
#     '''A function to show PIL images in the notebook.'''
#     plt.figure(figsize=(size,size))
#     plt.imshow(np.asarray(pil_im),cmap='gray')
#     plt.show()
#
# patch = slide.get_patch(w=25000, h=40000, mag=20, size=1000)
# show_PIL(patch)
#
# sampler = Sampler(path, level0=40, tissue_mask_dir=tissue_mask_dir, annotation_dir=None, engine=engine)
# sampler.prepare_sampling(magnification=20, patchsize=200)
#
# patchframe = sampler.sample_patches(max_per_class=20, savedir=os.getcwd())
# save_patchframe_patches(patchframe, './patches', engine=engine) # look in this directory

import unittest
import os
from wsisampler.slides.assign import assign_wsi_plus
from wsisampler.matlab_files.engine import get_matlab_engine
from wsisampler.sampler import Sampler
from wsisampler.tissue_mask import TissueMask
from wsisampler.utils.slide_utils import save_patchframe_patches
from wsisampler.jp2plus import JP2Plus

class TestJP2slides(unittest.TestCase):

    def setUp(self):

        # Assume testing data is in the root directory
        self.path = './G16-28741_B2LEV1-3G16-28741B21L-1-3_1.jp2'
        self.tissue_mask_dir = './mask'
        self.frames_dir = './frame'
        self.patches_dir = './patches'
        self.engine = get_matlab_engine()

    def test_assign_wsi_plus(self):

        self.slide = assign_wsi_plus(path, 20, engine)
        self.assertIsInstance(self.slide,
                              JP2Plus)

    def test_TissueMask(self):

        tissue_mask = TissueMask(tissue_mask_dir, reference_wsi=slide)
        self.assertIsInstance(tissue_mask, TissueMask)

    def test_Sampler(self):

        sampler = Sampler(self.path, level0=20, tissue_mask_dir=self.tissue_mask_dir,
                          annotation_dir=None, engine=self.engine)
        sampler.prepare_sampling(magnification=20, patchsize=200)
        patchframe = sampler.sample_patches(max_per_class=20, savedir=self.frames_dir)
        save_patchframe_patches(patchframe, self.patches_dir, engine=engine)

        self.assertIsInstance(sampler, Sampler)

if __name__=='__main__':
    unittest.main()
