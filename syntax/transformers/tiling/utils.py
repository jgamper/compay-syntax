import os
from typeguard import typechecked
from typing import Any
from syntax.slide.slide import Slide

@typechecked
def get_tile_from_info_dict(slide: Slide, info: Any):
    """
    Get a tile from an info dict.
    Args:
        slide:
        info: info dict

    Returns:
        patch (PIL image)
    """
    patch = slide.get_tile(info['w'], info['h'], info['mag'], info['size'])
    return patch

@typechecked
def save_tiles(slide,  save_dir=os.path.join(os.getcwd(), 'patches')):
    """
    Save tiles in a tile_frame to disk for visualization.
    Args:
        slide: slide that has tile_frame attribute
        save_dir: where to save to

    Returns:

    """
    os.makedirs(save_dir, exist_ok=True)
    tile_frame = slide.tile_frame
    num_tiles = tile_frame.shape[0]
    print('Saving hard copies of patches in tile_frame to {}.'.format(save_dir))
    for i in range(num_tiles):
        info = tile_frame.loc[i]
        patch = get_tile_from_info_dict(slide, info)
        filename = os.path.join(save_dir, '{}_class_{}_from_{}.png'.format(info['tile_id'], info['class'], info['parent']))
        patch.save(filename)
