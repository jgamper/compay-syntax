<p align="center">
    <br>
    <img src="docs/source/imgs/syntax_logo_text.png" width="600"/>
    <br>
<p>

Tools for sampling patches from Whole-Slide-Images (WSIs) readable by [openslide](https://openslide.org/) using Python ('tested' on 3.5).

If matlab engine is setup, then all of the same functionality applies to `jp2` WSIs.

Including objects to handle xml files produced by ASAP, or other annotation tools.


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
