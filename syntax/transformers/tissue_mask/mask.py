import os
import pickle
from typeguard import typechecked
from typing import Optional

@typechecked
class TissueMask(object):
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
    def __init__(self, level: int, magnification: float, ref_factor: float):
        """
        Initialise tissue mask by providing its level, magnification and reference factor
        Args:
            level:
            magnification:
            ref_factor:
        """
        self.level = level
        self.magnification = magnification
        self.ref_factor = ref_factor

    def get_tile(self, w_ref: int, h_ref: int, magnification, effective_size):
        """
        Get tile from tissue mask
        Args:
            w_ref: Width coordinate in frame of reference slide level 0.
            h_ref: Height coordinate in frame of reference slide level 0.
            magnification: Desired magnification.
            effective_size: Desired effective patchsize. \
                            NOTE: The patch returned does not have this size!

        Returns:
            tile, a numpy array
        """
        w = int(w_ref * self.ref_factor)
        h = int(h_ref * self.ref_factor)
        tile_size = int(effective_size * self.magnification / magnification)
        tile = self.data[h:h + tile_size, w:w + tile_size].astype(float)
        return tile

    def save(self, ID: str, savedir: str, verbose: Optional[bool] = False):
        """
        Pickles the tissue mask
        Args:
            ID: Name of the reference slide for which tissue mask has been computed
            savedir: Directory to save the mask
            verbose: Verbosity parameter 

        Returns:

        """
        os.makedirs(savedir, exist_ok=True)
        filename = os.path.join(savedir, ID + '_TissueMask.pickle')
        if verbose:
            print('Pickling TissueMask to {}'.format(filename))
        pickling_on = open(filename, 'wb')
        pickle.dump(self, pickling_on)
        pickling_on.close()

    def load(self, path: str):
        """
        Loads previously computed tissue mask
        Args:
            path: path to saved tissue mask

        Returns:

        """
        pickling_off = open(path, 'rb')
        tm = pickle.load(pickling_off)
        self.level = tm.level
        self.magnification = tm.magnification
        self.ref_factor = tm.ref_factor
        self.data = tm.data
        pickling_off.close()

