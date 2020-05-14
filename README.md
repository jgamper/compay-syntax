<p align="center">
    <br>
    <img src="docs/source/imgs/syntax_logo_text.png" width="600"/>
    <br>
<p>

# Usage

### Generate tissue mask
```python
from syntax.slides import assign_wsi
from sytnax.transformers import TissueMask
from syntax.transformers.tissue_mask import visualise

slide = assign_slide(slide=file, level0=40, hdf5=None)
slide = TissueMask().fit_transform(X=slide)
vis = visualise(slide=slide, tissue_mask=slide.tissue_mask)
show_PIL(vis, size=8)

# Save tissue mask
slide.save_tissue_mask(path=path_to_tissue_mask)
```

### Sample tiles from whole slide image
```python
from syntax.slides import assign_wsi
from syntax.transformers.samplers import Sampler

slide = assign_slide(slide=file, level0=40, hdf5=None)
sampler = Sampler(dataset_name=dataset_name, magnification=40, tile_size=256, ignore_bg=True, max_per_class=20)
slide = sampler.fit_transform(X=slide)
show_PIL(vis, size=8)
```

### Extract neural features from whole slide image using torchvision resnet18
```python
from syntax.slides import assign_wsi
from syntax.transformers.base import StaticTransformer
from torchvision import models

class ResnetFeatureTransformer(BaseTransformer):

    def fit(X, y=None):

        resnet18 = models.resnet18(pretrained=True)

        self.model = nn.Sequential(*list(resnet18.children())[:-1])

    def transform(X, y=None):





slide = assign_slide(slide=file, level0=40, hdf5=None)

```

# Install

`pip install wsisampler`

You will need to install openslide. This is included in the dependencies so may be automatically installed. If not I found this to help:

```bash
#!/bin/bash

sudo apt-get install openslide-tools
pip install openslide-python
```

# Example usage

Please see demo.ipynb [here](https://github.com/jgamper/WholeSlideImageSampler/blob/master/demo.ipynb).
