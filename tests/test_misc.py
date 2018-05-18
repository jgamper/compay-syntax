from wsisampler.misc import *


def test_index_last_non_zero():
    x = [2, 5, 4, 3, 0, 0]
    assert index_last_non_zero(x) == 3
    x = [2, 5, 4, 3, 7, 0]
    assert index_last_non_zero(x) == 4
