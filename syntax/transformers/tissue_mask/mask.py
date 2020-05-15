import os
import pickle

class TissueMask(object):

    def __init__(self, level, magnification, ref_factor):
        """
        An object for computing and storing tissue masks.
        :param search_dir: Where we store tissue masks.
        :param reference_wsi:
        """
        self.level = level
        self.mag = magnification
        self.ref_factor = ref_factor

    def get_tile(self, w_ref, h_ref, mag, effective_size):
        """
        Get a patch.
        :param w_ref: Width coordinate in frame of reference WSI level 0.
        :param h_ref: Height coordinate in frame of reference WSI level 0.
        :param mag: Desired magnification.
        :param effective_size: Desired effective tile_size. \
            NOTE: The patch returned does not have this size!
        :return:
        """
        w = int(w_ref * self.ref_factor)
        h = int(h_ref * self.ref_factor)
        tile_size = int(effective_size * self.mag / mag)
        patch = self.data[h:h + tile_size, w:w + tile_size].astype(float)
        return patch

    def save(self, ID, savedir, verbose=False):
        """
        Save (pickle) the TissueMask.
        :param ID:
        :param savedir: where to save to
        """
        os.makedirs(savedir, exist_ok=True)
        filename = os.path.join(savedir, ID + '_TissueMask.pickle')
        if verbose:
            print('Pickling TissueMask to {}'.format(filename))
        pickling_on = open(filename, 'wb')
        pickle.dump(self, pickling_on)
        pickling_on.close()

    def load(self, path):
        """
        Load TissueMask object.
        :return:
        """
        pickling_off = open(path, 'rb')
        tm = pickle.load(pickling_off)
        self.level = tm.level
        self.mag = tm.mag
        self.ref_factor = tm.ref_factor
        self.data = tm.data
        pickling_off.close()

