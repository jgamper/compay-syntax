from typeguard import typechecked
from syntax.slide.slide import Slide
from typing import List

@typechecked
def level_converter(slide: Slide, coordinate: int, level_in: float, level_out: float) -> int:
    """
    # TODO! might be moved to slide object
    Converts a coordinate from level_in to level_out
    Args:
        slide: syntax Slide object
        coordinate:
        level_in:
        level_out:

    Returns:
        Converted coordinate from level_in to level_out
    """
    return int(coordinate * slide.level_downsamples[level_in] / slide.level_downsamples[level_out])

@typechecked
def get_level(magnification: float, magnification_list: List[float], threshold: float=0.01):
    """
    Get the level closest to a specified magnification.
    Args:
        magnification:
        magnification_list:
        threshold:

    Returns:
        # TODO! update
    """
    diffs = [abs(magnification - magnification_list[i]) for i in range(len(magnification_list))]
    minimum = min(diffs)
    assert minimum < threshold, 'Suitable level not found.'
    level = diffs.index(minimum)
    return level