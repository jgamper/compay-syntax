import numpy as np
import os
from PIL import Image

from syntax._utils import misc
from syntax.slides.utils import get_level

try:
    import matlab
    from matlab import engine
except ImportError:
    raise ImportError('No MATLAB engine found - will not be able to read jp2 images.')