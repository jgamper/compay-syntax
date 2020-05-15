<p align="center">
    <br>
    <img src="docs/source/imgs/syntax_logo_text.png" width="600"/>
    <br>
<p>

# Help building our code and community!

Add sourcerer link here.

All contributions are welcome! Please see our [Contributing Guide](https://github.com/jgamper/wsi-syntax) for more details.

Join community discussions on [gitter room]()!

# Quick Start

### Tissue mask and tiling pipeline
```python
from syntax.slide import Slide
from syntax.transformers.tissue_mask import OtsuTissueMask
from syntax.transformers.tiling import SimpleTiling
from syntax.transformers import Pipeline, visualize_pipeline_results

slide = Slide(slide_path=slide_path)
pipeline = Pipeline([OtsuTissueMask(), SimpleTiling(magnification=40,
                                                  tile_size=224,
                                                  max_per_class=10)])
slide = pipeline.fit_transform(slide)
vis = visualize_pipeline_results(slide=slide, pipeline=pipeline, size=1000)
show_PIL(vis, size=8)
```

### Resnet features and tile clustering pipeline
```python
from syntax.slide import Slide
from syntax.transformers.base import StaticTransformer
from torchvision import models

@apply_to_slide
class ResnetFeatureTransformer(BaseTransformer):

    def fit(self, *args, **kwargs):

        resnet18 = models.resnet18(pretrained=True)

        self.model = nn.Sequential(*list(resnet18.children())[:-1])

    def transform(x):

        with torch.no_grad():
            return self.model(x).data.numpy()

slide = Slide(slide_path=slide_path)
pipeline = Pipeline([ResnetFeatureTransformer(), InductiveClustering()])
slide = pipeline.fit_transform(slide)
vis = visualize_pipeline_results(slide=slide, pipeline=pipeline, size=1000)
show_PIL(vis, size=8)
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
