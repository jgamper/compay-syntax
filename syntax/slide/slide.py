from openslide import OpenSlide
import os
from typeguard import typechecked
from typing import Optional
from syntax._utils import misc

@typechecked
class Slide(OpenSlide):
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
                 slide_path: str,
                 level0: Optional[int] = None,
                 verbose: Optional[bool] = False):
        """

        Args:
            slide_path: Path to the WSI readable by openslide.
            level0: The 'magnification' at level 0. If 'infer' we attempt to get from metadata.
            verbose:
        """
        super(Slide, self).__init__(slide_path)
        self.verbose = verbose

        # Get slide id for reference
        self.ID = os.path.splitext(os.path.basename(slide_path))[0]

        # Add level0 magnification.
        if level0 == None:
            try:
                self.level0 = float(self.properties['openslide.objective-power'])
                if self.verbose:
                    print('Level 0 found @ {}X'.format(self.level0))
            except:
                raise Exception('Slide does not have property objective-power.')
        else:
            self.level0 = float(level0)

        # Compute level magnifications.
        self._magnification_list = [self.level0 / downsample for downsample in self.level_downsamples]

    def get_tile(self, w: int, h: int, magnification: int, size: int):
        """
        Get a tile.
        If required magnification not available will use a higher magnification and resize.
        Args:
            w: Width coordinate in level 0 frame.
            h: Height coordinate in level 0 frame.
            magnification: Desired magnification.
            size: Desired tile size (square tile).

        Returns:

        """
        assert self.level0 >= magnification, 'Magnification not available.'

        higher_mags = [self.magnifications[i] >= magnification for i in range(len(self.magnifications))]
        extraction_level = misc.index_last_non_zero(higher_mags)
        extraction_mag = self.magnifications[extraction_level]
        extraction_size = int(size * extraction_mag / magnification)

        # Make sure it's RGB (not e.g. RGBA).
        tile = self.read_region((w, h), extraction_level, (extraction_size, extraction_size)).convert('RGB')
        if extraction_size != size:
            tile.thumbnail((size, size))  # Resize inplace.
        return tile

    @property
    def magnifications(self):
        return self._magnification_list