from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='wsisampler',
    version='0.0.2',
    description='A package for WSI sampling.',
    long_description=readme,
    author='Peter Byfield',
    author_email='byfield554@gmail.com',
    url='https://github.com/Peter554/WholeSlideImageSampler',
    packages=find_packages(),
    install_requires=['numpy',
                      'opencv-python',
                      'openslide-python',
                      'matplotlib',
                      'jupyter',
                      'future',
                      'cython',
                      'pandas',
                      'scikit-image'
                      ],
    classifiers=[
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5'
    ]
)