from setuptools import setup, find_packages

setup(
    name='compay-syntax',
    version='0.4.1',
    description='Syntax - the arrangement of whole-slide-images and their image tiles to create well-formed computational pathology pipelines.',
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author='Jevgenij Gamper & Peter Byfield',
    author_email='jevgenij.gamper5@gmail.com',
    url='https://github.com/jgamper/compay-syntax',
    packages=find_packages(),
    install_requires=['numpy',
                      'openslide-python',
                      'matplotlib',
                      'jupyter-client',
                      'jupyter-core',
                      'Pillow',
                      'typeguard',
                      'pandas',
                      'scikit-image',
                      ],
    classifiers=[
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6'
    ]
)
