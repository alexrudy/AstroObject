from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup
setup(
    name = "AstroObject",
    packages = ['AstroObject'],
    package_data = {'':['VERSION']},
    install_requires = ['distribute','pyfits>=2.4','numpy>=1.5','scipy>=0.9','matplotlib>=1.0'],
    version = "0.3.0a1",
    test_suite = 'tests',
)
