from openslide import open_slide
from PIL import Image
import numpy as np
import os
import cv2

from .slides.slide import OpenSlidePlus
from .slides.jp2plus import JP2Plus
from ._utils.slide_utils import get_level
from .xml.xml_utils import generate_annotation_mask
from .xml.xml_utils import XMLDirectoryMissing, XMLFileMissing
from ._utils.misc import item_in_directory


class Annotation(object):

    def __init__(self, search_dir, reference_wsi, xml_reader, xml_dir):
        """
        An extension to the OpenSlide class for internal_objtations.
        So far only works with free hand annotations.
        :param search_dir: directory to search annotation mask
        :param reference_wsi: reference whole slide image
        :param xml_dir: file to search for xml file
        :param xml_reader: an object to deal with XML file
        """
        assert isinstance(reference_wsi, OpenSlidePlus) or isinstance(reference_wsi, JP2Plus), 'Reference WSI should be OpenSlidePlus or JP2Plus.'
        assert xml_reader != None, 'You did not provide XML reader'

        truth, filename = item_in_directory(reference_wsi.ID, search_dir)
        if truth:
            print('Annotation found, initialising')
            self._initialise(filename, reference_wsi)
        # If not attempt to create an annotation mask
        else:
            print('Ready annotation mask is not found')
            self._xml_initialise(search_dir, xml_dir, reference_wsi, xml_reader)
            print('Annotation mask has been made, saved, and loaded')
            truth, filename = item_in_directory(reference_wsi.ID, search_dir)
            self._initialise(filename, reference_wsi)

    def get_patch(self, w_ref, h_ref, mag, size):
        """
        Get a patch.
        If required magnification not available will use nearby magnification and resize.
        :param w_ref: Width coordinate in frame of reference WSI level 0.
        :param h_ref: Height coordinate in frame of reference WSI level 0.
        :param mag: Desired magnification.
        :param size: Desired patch size (square patch).
        :return:
        """
        w = int(w_ref * self.ref_factor)
        h = int(h_ref * self.ref_factor)
        if len(self.mags) > 1:
            extraction_level = get_level(mag, self.mags, threshold=5.0)
            extraction_mag = self.mags[extraction_level]
        else:
            extraction_level = 0
            extraction_mag = self.mags[extraction_level]
        extraction_size = int(size * extraction_mag / mag)

        patch = self.internal_obj.read_region((w, h), extraction_level, (extraction_size, extraction_size)).convert('RGB')
        if extraction_size != size:
            patch.thumbnail((size, size))  # Resize inplace.
        return patch

    def get_low_res_numpy(self, xml_reader):
        """
        Get a low resolution version as numpy array.
        Also returns a factor for converting lengths back to reference WSI level 0 frame.
        :return:
        """
        level = get_level(mag=1.25, mags=self.mags, threshold=5.0)
        size = self.internal_obj.level_dimensions[level]
        low_res = self.internal_obj.read_region((0, 0), level, size).convert('RGB').copy()
        low_res_np = np.asarray(low_res)
        low_res_np.setflags(write=1)
        # Convert to labels
        unique = np.unique(low_res_np.reshape(-1, low_res_np.shape[2]), axis=0)
        for i in range(unique.shape[0]):
            pixel = unique[i,:]
            mask = ( low_res_np == pixel).all(axis=2)
            label = xml_reader.pixel_to_label(tuple(pixel))
            low_res_np[mask] = [label, label, label]
        # Get factor
        factor = self.internal_obj.level_downsamples[level] / self.ref_factor  # Factor for converting lengths back to reference WSI level 0 frame.
        return low_res_np[:,:,0], factor

    def visualize(self, reference_wsi, code_legend=None):
        """
        # TODO: ADD COLOR CODE LEGEND

        Visualize the internal_objtations.
        :param reference_wsi:
        :param code_legend: dictionary with integers as keys, and values as the name of the class
        :return:
        """
        assert isinstance(reference_wsi, OpenSlidePlus) or isinstance(reference_wsi, JP2Plus), 'Reference WSI should be OpenSlidePlus or JP2Plus.'
        size = 3000
        anno = self.internal_obj.get_thumbnail((size, size)).convert('RGBA')

        wsi_thumb = reference_wsi.get_thumbnail(size=(size, size)).convert('RGBA') # Copy to avoid read-only issue.

        return Image.blend(wsi_thumb, anno, alpha=0.5)

    ### Hidden ugly methods

    def _initialise(self, filename, reference_wsi):
        """
        Initialises annotation object if mask is available
        :param filename: name of the file storing the annotations mask
        """
        # Assign either OpenSlide or ImageSlide objects
        self.internal_obj = open_slide(filename)

        self.ref_factor = self.internal_obj.level_dimensions[0][0] / reference_wsi.level_dimensions[0][0] \
            # Use to convert coordinates.
        # Get level 0.
        self.level0 = reference_wsi.level0 * self.ref_factor
        # Get level magnifications.
        self.mags = [self.level0 / downsample for downsample in self.internal_obj.level_downsamples]

    def _xml_initialise(self, search_dir, xml_dir, reference_wsi, xml_reader):
        """
        Checks if xml directory exists and if file is present. If so
        starts the construction of the annotation mask.
        :param search_dir: directory to search annotation mask
        :param xml_dir: directory where xml files are stored
        :param reference_wsi: reference whole slide image
        :param xml_reader: an object to deal with XML file
        """
        if xml_dir is None:
            # Catching this exception can be used for processing in batch
            raise XMLDirectoryMissing('XML directory not provided')
        if xml_dir is not None:
            # Check if corresponding xml exists
            truth, filename = item_in_directory(reference_wsi.ID, xml_dir)
            if truth:
                generate_annotation_mask(filename, search_dir, reference_wsi, xml_reader)
            else:
                # Catching this exception can be used for processing in batch
                raise XMLFileMissing('XML file for wsi {} cannot be found'.format(reference_wsi.ID))
