import os

from modules import slide_sampler

###

data_dir = '/media/peter/HDD 1/datasets_peter/Camelyon16/Train/Original/Tumor'
file = os.path.join(data_dir, 'Tumor_001.tif')
mask_file = os.path.join(data_dir, 'Mask_Tumor', 'Tumor_001.tif')

###

sampler = slide_sampler.Slide_Sampler(wsi_file=file, desired_downsampling=4, size=256)

sampler.print_slide_properties()

sampler.view_WSI()

sampler.add_background_mask(desired_downsampling=32)
sampler.view_background_mask(overlay=0)

patch = sampler.get_patch()
patch.save('./patch.png')

c = 2
