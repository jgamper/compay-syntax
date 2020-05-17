import warnings
from typeguard import typechecked
import numpy as np
from random import shuffle
import pandas as pd
from typing import Optional
from PIL import ImageDraw
from syntax.transformers.base import StaticTransformer
from syntax.slide import Slide

@typechecked
class SimpleTiling(StaticTransformer):
    """The summary line for a class docstring should fit on one line.

    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).

    Properties created with the ``@property`` decorator should be documented
    in the property's getter method.

    Attributes:
        attr1 (str): Description of `attr1`.
        attr2 (:obj:`int`, optional): Description of `attr2`.

    """

    def __init__(self,
                 magnification: int,
                 tile_size: int,
                 max_per_class: int,
                 annotation_threshold: Optional[float] = None):
        """

        Args:
            magnification:
            tile_size:
        """
        self.magnification = magnification
        self.tile_size = tile_size
        self.max_per_class = max_per_class
        self.anno_threshold = annotation_threshold
        self.rejected = 0

    def transform(self, slide: Slide, target=None):
        """
        TODO!
        Args:
            slide:
            target:

        Returns:

        """
        # Check if slide already has patch-frame if it does, then just return it as it is
        if self._check_patch_frame(slide):
            warnings.warn("{} slide already has tile_frame, yet has been passed to PatchExtractor".format(self.slide.ID))
            return slide

        # Check if has tissue mask
        self._check_tissue_mask(slide)

        # Check if has annotation mask
        self._check_annotation(slide)

        self.slide = slide

        #  Get classes and approximate coordinates to 'seed' the patch sampling process.
        self._get_classes_and_seeds()

        slide.tile_frame = self._sample_patches(self.slide.verbose)

        return slide

    @staticmethod
    def visualize(slide: Slide, size: int):
        """

        Args:
            slide:
            size:

        Returns:

        """
        wsi_thumb = slide.get_thumbnail(size=(size, size))

        xy = list(zip(slide.tile_frame.w, slide.tile_frame.h))

        for w, h in xy:
            w = int(w / pow(2, slide.level_count + 2)) + 1
            h = int(h / pow(2, slide.level_count + 2)) + 1
            mask = wsi_thumb.copy()
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rectangle(((w, h), (w + 20, h + 20)), fill=255)
            wsi_thumb.paste(mask)

        return wsi_thumb

    def _sample_patches(self, verbose=False):
        """Sample tile and return in a tile_frame"""
        frame = pd.DataFrame(data=None, columns=['tile_id', 'w', 'h', 'class', 'mag', 'size', 'parent', 'lvl0'])

        for c in self.class_list:
            index = self.class_list.index(c)
            seeds = self.class_seeds[index]
            count = 0
            for j, seed in enumerate(seeds):
                _, info = self._class_c_patch_i(c, j)
                if info is not None:
                    frame = frame.append(info, ignore_index=1)
                if isinstance(self.max_per_class, int):
                    # If not rejected increment count
                    if info is not None:
                        count += 1
                    if count >= (self.max_per_class - 1):
                        break
        if verbose:
            print('Rejected {} patches for file {}'.format(self.rejected, self.slide.ID))

        return frame

    def _get_classes_and_seeds(self):
        """Get classes and approximate coordinates to 'seed' the patch sampling process.
        Builds the objects self.class_list and self.class_seeds."""

        # Do class 0 i.e. unannotated first.
        mask = self.tissue_mask.data
        nonzero = np.nonzero(mask)
        factor = self.slide.level_downsamples[self.tissue_mask.level]
        N = nonzero[0].size
        coordinates = [(int(nonzero[0][i] * factor), int(nonzero[1][i] * factor)) for i in range(N)]
        shuffle(coordinates)
        self.class_list = [0]
        self.class_seeds = [coordinates]

        # If no annotation we're done.
        if self.annotation is None:
            return

        # Now add other classes.
        annotation_low_res, factor = self.annotation.get_low_res_numpy(self.xml_reader)
        classes = sorted(list(np.unique(annotation_low_res)))

        assert classes[0] == 0
        classes = classes[1:]

        for c in classes:
            mask = (annotation_low_res == c)
            nonzero = np.nonzero(mask)
            N = nonzero[0].size
            coordinates = [(int(nonzero[0][i] * factor), int(nonzero[1][i] * factor)) for i in range(N)]
            shuffle(coordinates)
            self.class_list.append(c)
            self.class_seeds.append(coordinates)
            
    def _class_c_patch_i(self, c, i):
        """
        Try and get the ith patch of class c. If we reject return (None, None).
        :param c: class
        :param i: index
        :return: (patch, info_dict) or (None, None) if we reject patch.
        """
        idx = self.class_list.index(c)
        h, w = self.class_seeds[idx][i]
        patch = self.slide.get_tile(w, h, self.magnification, self.tile_size)

        tissue_mask_patch = self.tissue_mask.get_tile(w, h, self.magnification, self.tile_size)
        if np.sum(tissue_mask_patch) / np.prod(tissue_mask_patch.shape) < 0.9:
            self.rejected += 1
            return None, None

        info = {
            'tile_id': i,
            'w': w,
            'h': h,
            'parent': self.slide.ID,
            'size': self.tile_size,
            'mag': self.magnification,
            'class': c,
            'lvl0': self.slide.level0
        }

        # If no annotation we're done.
        if self.annotation is None:
            return patch, info

        annotation_patch = self.annotation.get_tile(w, h, self.magnification, self.tile_size)
        annotation_patch = np.asarray(annotation_patch)
        print(annotation_patch.shape)
        pixel_pattern = self.xml_reader.label_to_pixel(c)
        mask = (annotation_patch == pixel_pattern)
        if np.sum(mask) / np.prod(mask.shape) < self.anno_threshold:
            self.rejected += 1
            return None, None

        return patch, info

    def _check_patch_frame(self, slide: Slide):
        """Check if slide already has patch frame"""
        return hasattr(slide, "tile_frame")

    def _check_tissue_mask(self, slide: Slide):
        """Checks if slide has tissue mask, if not raises an issue"""
        assert hasattr(slide, "tissue_mask"), "Slide {} does not have tissue mask!".format(slide.ID)
        self.tissue_mask = slide.tissue_mask

    def _check_annotation(self, slide: Slide):
        """Checks if has annotation and raises a warning"""
        if not hasattr(slide, "annotation"):
            self.annotation = None
            warning_string = "{} slide does not have annotation mask supplied".format(slide.ID)
            warnings.warn(warning_string)
        else:
            self.annotation = slide.annotation