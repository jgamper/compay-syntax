<p align="center">
    <br>
    <img src="https://raw.githubusercontent.com/jgamper/compay-syntax/master/docs/source/imgs/syntax_logo_text.png?token=ADDZO4PH6CJSK5XTSC2ZLXK6ZPXRY" width="600"/>
    <br>
<p>
<p align="center">
    <a href="https://github.com/jgamper/compay-syntax/blob/master/LICENSE">
        <img alt="GitHub" src="https://img.shields.io/github/license/jgamper/compay-syntax.svg?color=blue">
    </a>
    <a href="https://jgamper.github.io/compay-syntax/">
        <img alt="Documentation" src="https://img.shields.io/website/http/jgamper.github.io/syntax.svg?down_color=red&down_message=offline&up_message=online">
    </a>
    <a href="https://github.com/jgamper/compay-syntax/releases">
        <img alt="GitHub release" src="https://img.shields.io/github/release/jgamper/compay-syntax.svg">
    </a>
</p>

# Help building our code and community!

[![](https://sourcerer.io/fame/jgamper/jgamper/compay-syntax/images/0)](https://sourcerer.io/fame/jgamper/jgamper/compay-syntax/links/0)[![](https://sourcerer.io/fame/jgamper/jgamper/compay-syntax/images/1)](https://sourcerer.io/fame/jgamper/jgamper/compay-syntax/links/1)[![](https://sourcerer.io/fame/jgamper/jgamper/compay-syntax/images/2)](https://sourcerer.io/fame/jgamper/jgamper/compay-syntax/links/2)[![](https://sourcerer.io/fame/jgamper/jgamper/compay-syntax/images/3)](https://sourcerer.io/fame/jgamper/jgamper/compay-syntax/links/3)[![](https://sourcerer.io/fame/jgamper/jgamper/compay-syntax/images/4)](https://sourcerer.io/fame/jgamper/jgamper/compay-syntax/links/4)[![](https://sourcerer.io/fame/jgamper/jgamper/compay-syntax/images/5)](https://sourcerer.io/fame/jgamper/jgamper/compay-syntax/links/5)[![](https://sourcerer.io/fame/jgamper/jgamper/compay-syntax/images/6)](https://sourcerer.io/fame/jgamper/jgamper/compay-syntax/links/6)[![](https://sourcerer.io/fame/jgamper/jgamper/compay-syntax/images/7)](https://sourcerer.io/fame/jgamper/jgamper/compay-syntax/links/7)

All contributions are welcome! Please raise an issue for a bug, feature or pull request!

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
visualize_pipeline_results(slide=slide,
                           transformer_list=pipeline.transformers,
                           title_list=['Tissue Mask', 'Random Tile Sampling'])
```
<p align="center">
    <img src="https://raw.githubusercontent.com/jgamper/compay-syntax/master/docs/source/imgs/simple_pipeline.png?token=ADDZO4ISOOTTRG4MMPNYCXS6ZPXPS" width="600"/>
<p>

# Install

`pip install compay-syntax`

You will need to install openslide. This is included in the dependencies so may be automatically installed. If not I found this to help:

```bash
#!/bin/bash

sudo apt-get install openslide-tools
pip install openslide-python
```
