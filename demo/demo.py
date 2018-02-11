import os
from modules import slide_sampler, utils
import pandas as pd

###

data_dir = '/home/peter/Dropbox/publish-final/WSI_sampler_data'

file = os.path.join(data_dir, 'Tumor_004.tif')
mask_file = os.path.join(data_dir, 'Tumor_004_mask.tif')

###

sampler = slide_sampler.Slide_Sampler(wsi_file=file, desired_downsampling=4, size=256)

###

sampler.print_slide_properties()

# sampler.save_WSI_thumbnail()

# sampler.generate_background_mask(desired_downsampling=32)
# sampler.pickle_background_mask()

sampler.pickle_load_background_mask(file='./Tumor_004_bgmask.pickle')
# sampler.save_background_mask_visualization() # Slow!

sampler.add_annotation_mask(annotation_mask_file=mask_file)
# sampler.save_annotation_thumbnail()

###

# patch_class0, _ = sampler.get_classed_patch(patch_class=0, verbose=1)
# patch_class0.save('./class0_1.png')
# patch_class0, _ = sampler.get_classed_patch(patch_class=0, verbose=1)
# patch_class0.save('./class0_2.png')
# patch_class0, _ = sampler.get_classed_patch(patch_class=0, verbose=1)
# patch_class0.save('./class0_3.png')
#
# patch_class1, _ = sampler.get_classed_patch(patch_class=1, verbose=1)
# patch_class1.save('./class1_1.png')
# patch_class1, _ = sampler.get_classed_patch(patch_class=1, verbose=1)
# patch_class1.save('./class1_2.png')
# patch_class1, _ = sampler.get_classed_patch(patch_class=1, verbose=1)
# patch_class1.save('./class1_3.png')

###

sampler.get_basic_patchframe(number_patches=100, save=1)

frame = pd.read_pickle(path='./Tumor_004_patchframe.pickle')

print('\npatchframe head:')
print(frame.head())

utils.save_patchframe_patches(input=frame, save_dir='./patches')