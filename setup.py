from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='syntax',
    version='0.0.3',
    description='A package for WSI sampling and annotations processing',
    long_description=readme,
    author='Jevgenij Gamper & Peter Byfield',
    author_email='jevgenij.gamper5@gmail.com',
    url='https://github.com/jgamper/WholeSlideImageSampler',
    packages=find_packages(),
    install_requires=['numpy',
                      'opencv-python',
                      'openslide-python',
                      'matplotlib',
                      'jupyter',
                      'future',
                      'cython',
                      'pandas',
                      'scikit-image',
                      'xmltodict'
                      ],
    classifiers=[
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5'
    ]
)
