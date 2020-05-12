<p align="center">
    <br>
    <img src="docs/source/imgs/syntax_logo_text.png" width="600"/>
    <br>
<p>

# Usage

### Generate tissue mask
```python
from syntax.slides import assign_wsi
from sytnax.tissuemask import TissueMask

slide = assign_slide(slide=file, level0=40, frame=None)
tissue_mask = TissueMask(save_path=path_to_save_tissue_mask, reference_slide=slide)
vis = tissue_mask.visualize(reference_slide=slide)
show_PIL(vis, size=8)
```

### View ASAP annotation
```python
from syntax.slides import assign_wsi
from syntax.annotation import Annotation
from syntax.annotation.xml import Asap

slide = assign_slide(slide=file, level0=40, frame=None)
asap_handler = Asap(xml_file)
annotation = Annotation(reference_slide=slide,
                      annotation_handler=asap_handler)
vis = annotation.visualize(reference_slide=slide)
show_PIL(vis, size=8)
```

### Sample from whole slide image
```python
from syntax.slides import assign_wsi
from syntax.sample import Sampler
from syntax.annotation import Annotation
from syntax.annotation.xml import Asap

slide = assign_slide(slide=file, level0=40, frame=None)
asap_handler = Asap(xml_file)
annotation = Annotation(reference_slide=slide,
                      annotation_handler=asap_handler)
vis = annotation.visualize(reference_slide=slide)
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
