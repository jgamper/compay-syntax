import os
from modules import slide_sampler

###

data_dir = '/home/peter/Dropbox/publish-final/WSI_sampler_data'

file = os.path.join(data_dir, 'Tumor_004.tif')
mask_file = os.path.join(data_dir, 'Tumor_004_bgmask.tif')

###

sampler = slide_sampler.Slide_Sampler(wsi_file=file, desired_downsampling=4, size=256)

# sampler.print_slide_properties()

sampler.save_WSI_thumbnail()

# sampler.generate_background_mask(desired_downsampling=32)
# sampler.pickle_background_mask()

sampler.pickle_load_background_mask(file='./bgmask.pickle')
# sampler.save_background_mask_visualization()

sampler.add_annotation_mask(annotation_mask_file=mask_file)
sampler.save_annotation_thumbnail()

done = 0
while not done:
    patch, info = sampler.get_classed_patch(verbose=1)
    if info['class'] == 1:
        done = 1
