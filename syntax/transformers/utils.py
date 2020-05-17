from typeguard import typechecked
from typing import List, Any, Optional
import numpy as np
import matplotlib.pyplot as plt
from syntax.slide.slide import Slide

@typechecked
def visualize_pipeline_results(slide: Slide,
                               transformer_list: List[Any],
                               title_list: Optional[List[str]] = None,
                               size: int = 1000):
    """
    Visualise results of the pipeline
    Args:
        slide:
        transformer_list:
        size:

    Returns:

    """
    num_steps = len(transformer_list)
    fig, axes = plt.subplots(1, num_steps+1, figsize=(5*num_steps, 5))

    if title_list:
        title_list = ['Slide'] + title_list

    pil = slide.get_thumbnail(size=(size, size))
    for i, ax in enumerate(axes):
        if i > 0:
            pil2 = transformer_list[i-1].visualize(slide, size)
            pil.paste(pil2)
        ax.axis("off")
        ax.imshow(np.asarray(pil), cmap="gray")
        if title_list:
            ax.set_title(title_list[i])



