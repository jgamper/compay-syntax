"""
single_sampler module
"""

import openslide
import os
import numpy as np
from skimage import filters, color
from skimage.morphology import disk
from skimage.morphology import opening, dilation, closing
from PIL import Image
import pickle
import pandas as pd
from modules import utils


class Single_Sampler(object):

    def __init__(self, wsi_file, desired_downsampling, size, annotation_file=None, background_file=None):
        self.wsi_file = wsi_file
        self.desired_downsampling = desired_downsampling
        self.size = size
        self.annotation_file = annotation_file
        self.background_file = background_file

        self.wsi = openslide.OpenSlide(self.wsi_file)
        self.level, self.downsampling = utils.get_level_and_downsampling(self.wsi, desired_downsampling)
