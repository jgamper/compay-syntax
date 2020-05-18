from setuptools import setup, find_packages

setup(
    name='compay-syntax-test',
    version='0.0.6',
    description='Syntax - the arrangement of whole-slide-images and their image tiles to create well-formed computational pathology pipelines.',
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author='Jevgenij Gamper & Peter Byfield',
    author_email='jevgenij.gamper5@gmail.com',
    url='https://github.com/jgamper/compay-syntax',
    packages=find_packages(),
    install_requires=['numpy==1.17.4',
                      'openslide-python==1.1.1',
                      'matplotlib==3.2.1',
                      'jupyter-client==6.1.3'
                      'jupyter-core==4.6.3'
                      'Pillow==7.1.2',
                      'typeguard==2.7.1',
                      'pandas==1.0.3',
                      'scikit-image==0.17.2',
                      ],
    classifiers=[
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6'
    ]
)
