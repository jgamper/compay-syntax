from .openslideplus import OpenSlidePlus
from .jp2plus import JP2Plus


def assign_wsi_plus(file, level0, engine=None):
    """
    Function to select if JP2Plus or OpenSlidePlus should be used for a given image.

    :param file: Path to the matlab_files format WSI
    :param level0: The 'magnification' at level 0.
    :param engine: Matlab engine object.
    """
    if engine is None:
        return OpenSlidePlus(file, level0)
    else:
        return JP2Plus(file, level0, engine)
