from setuptools import setup, find_packages
setup(
    name = "AstroObject",
    version = "0.2.8",
    py_modules=["AstroObject"],
    packages = find_packages(
        exclude=['tests.*'],
        ),
    package_data = {'':['VERSION','README.md','LICENCE']},
    include_package_data = True,
    exclude_package_data = {'': ['.gitignore','bump-version.sh','distribute.sh'], 'Docs/build':['*.rst']},
    install_requires = ['pyfits>=2.4','numpy>=1.6','scipy>=0.9','matplotlib>=1.1'],
    test_suite = 'tests',
)
