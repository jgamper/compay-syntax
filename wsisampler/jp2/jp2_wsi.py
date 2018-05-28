import numpy as np
import os
try:
    import matlab
    from matlab import engine
except ImportError:
    raise ImportError('You do not have matlab engine, buddy!')

class OpenJP2(object):

    def __init__(self, wsi_file, engine):
        """
        :param wsi_file: path to a WSI file
        :param m_path: path to where matlab functions are
        """
        call_path = os.path.dirname(os.path.realpath(__file__))
        self.wsi_file = wsi_file
        self.jp2 = True
        self.engine = engine
        self.engine.addpath(r'{}'.format(call_path),nargout=0)
        self.load_wsi_properties()

    def load_wsi_properties(self):
        level_dim, level_downsamples, level_count = self.engine.JP2Image(self.wsi_file, nargout=3)
        level_dim = np.int32(level_dim)
        self.level_downsamples = tuple(i[0] for i in np.float32(level_downsamples))
        self.level_dimensions = []
        for i in range(int(level_count)):
            self.level_dimensions.append(tuple([level_dim[i, 1], level_dim[i, 0]]))
        self.level_dimensions = tuple(self.level_dimensions)

    def read_region(self, location, level, size):

        y1 = int(location[0] / pow(2, level)) + 1
        x1 = int(location[1] / pow(2, level)) + 1
        y2 = int(y1 + size[0] -1)
        x2 = int(x1 + size[1] -1)
        patch = self.engine.read_region(self.wsi_file,
                                        level, matlab.int32([x1,x2,y1,y2]))
        patch = np.array(patch._data).reshape(patch.size, order='F')

        return patch

def ReturnEngine():
    """
    Returns matlab engine with path to functions for WSI
    :param m_path: path to where matlab functions are
    """
    matlab_dir = os.path.dirname(__file__)
    eng = engine.start_matlab()
    eng.cd(r'{}'.format(matlab_dir), nargout=0)
    return eng
