import warnings
from typeguard import typechecked
import numpy as np
from skimage import filters, color
from skimage.morphology import disk
from skimage.morphology import opening, closing
from syntax.transformers.tissue_mask.mask import TissueMask
from syntax.transformers.base import StaticTransformer
from syntax.slide import Slide
from syntax.slide.utils import get_level

@typechecked
class OtsuTissueMask(StaticTransformer):
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

    def __init__(self):
        pass

    def transform(self, slide: Slide, target=None):
        """
        TODO!
        Args:
            slide:
            target:

        Returns:

        """
        # Check if slide already has tissue_mask if it does, then just return it as it is
        if self._check_tissue_mask(slide):
            warnings.warn("{} slide already has tissue_mask, yet has been passed to TissueMaskOtsu".format(self.slide.ID))
            return slide

        level = get_level(magnification=1.25, magnification_list=slide.magnifications, threshold=5.0)
        magnification = slide.magnifications[level]
        ref_factor = magnification / slide.level0  # Use to convert coordinates.

        # Initialise tissue mask with slide
        slide.tissue_mask = TissueMask(level, magnification, ref_factor)

        slide.tissue_mask.data = self._generate_tissue_mask_basic(slide, level)

        return slide

    @staticmethod
    def _generate_tissue_mask_basic(slide, level):
        """
        Generate a tissue mask.
        This is achieved by Otsu thresholding on the saturation channel \
        followed by morphological closing and opening to remove noise.
        :param slide:
        :param level:
        :return:
        """
        if not hasattr(slide, 'jp2'):
            low_res = slide.read_region(location=(0, 0), level=level, size=slide.level_dimensions[level]).convert('RGB') \
                # Read slide at low resolution and make sure it's RGB (not e.g. RGBA).
            low_res_numpy = np.asarray(low_res)  # Convert to numpy array.
        else:
            low_res_numpy = slide.read_region(location=(0, 0), level=level, size=slide.level_dimensions[level])
        low_res_numpy_hsv = color.convert_colorspace(low_res_numpy, 'RGB', 'HSV')  # Convert to Hue-Saturation-Value.
        saturation = low_res_numpy_hsv[:, :, 1]  # Get saturation channel.
        threshold = filters.threshold_otsu(saturation)  # Otsu threshold.
        mask = (saturation > threshold)  # Tissue is 'high saturation' region.

        # Morphological operations
        disk_radius = 10  # radius of disk for morphological operations.
        disk_object = disk(disk_radius)
        mask = closing(mask, disk_object)  # remove 'pepper'.
        mask = opening(mask, disk_object)  # remove 'salt'.
        assert mask.dtype == bool, 'Mask not Boolean'
        return mask

    def _check_tissue_mask(self, slide: Slide):
        """Check if slide already has patch frame"""
        return hasattr(slide, "tissue_mask")