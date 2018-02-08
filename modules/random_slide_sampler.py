import openslide
import os
import numpy as np


class Random_Slide_Sampler(object):

    def __init__(self, wsi_file, desired_down_sampling, size, annotation_mask_file=None):
        super(Random_Slide_Sampler, self).__init__()
        self.wsi_file = wsi_file
        self.wsi = openslide.OpenSlide(self.wsi_file)
        self.desired_down_sampling = desired_down_sampling
        self.size = size

        self.get_level_and_downsampling()

        print('\nInitialized Random_Slide_Sampler for slide {}'.format(os.path.basename(self.wsi_file)))
        print('Patches will be sampled at level {0} (downsampling of {1}) with size {2} x {2}'.format(self.level,
                                                                                                      self.down_sampling,
                                                                                                      self.size))
        self.width_available = int(self.wsi.dimensions[0] - self.down_sampling * size)
        self.height_available = int(self.wsi.dimensions[1] - self.down_sampling * size)

    def get_level_and_downsampling(self, threshold=0.1):
        diffs = [abs(self.desired_down_sampling - self.wsi.level_downsamples[i]) for i in
                 range(len(self.wsi.level_downsamples))]
        minimum = min(diffs)

        if minimum > threshold:
            raise Exception(
                '\n\nLevel not found for desired downsampling.\nAvailable downsampling factors are\n{}'.format(
                    self.wsi.level_downsamples))

        self.level = diffs.index(minimum)
        self.down_sampling = self.wsi.level_downsamples[self.level]

    def print_slide_properties(self):
        print('\nSlide properties.')
        print('Dimensions as level 0:')
        print(self.wsi.dimensions)
        print('Number of levels:')
        print(self.wsi.level_count)
        print('with downsampling factors:')
        print(self.wsi.level_downsamples)

    def get_patch(self):
        w = np.random.choice(self.width_available)
        h = np.random.choice(self.height_available)
        patch = self.wsi.read_region(location=(w, h), level=self.level, size=(self.size, self.size)).convert(
            'RGB')  # returns RGBA PIL image so convert to RGB
        return patch


###

data_dir = '/media/peter/HDD 1/datasets_peter/Camelyon16/Train/Original/Tumor'
file = os.path.join(data_dir, 'Tumor_001.tif')
mask_file = os.path.join(data_dir, 'Mask_Tumor', 'Tumor_001.tif')

sampler = Random_Slide_Sampler(file, 4, 256)

patch = sampler.get_patch()
patch.show()

c = 2
