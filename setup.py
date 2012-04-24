# -*- coding: utf-8 -*-
# 
#  setup.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-04-17.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 

from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup

from distutils.command.build_py import build_py as du_build_py
from distutils.core import Command

from pkg_resources import parse_version

from AstroObject.version import version as versionstr

# Check for matplotlib:
try:
    from matplotlib import __version__ as mplversion
    assert parse_version(mplversion) >= parse_version("1.0")
except:
    print "Matplotlib does not appear to be installed correctly.\nYou must install Matplotlib 1.0 or later."

class Version(Command):
    description = "Print the module version"
    user_options = []
    def initialize_options(self):
        pass
        
    def finalize_options (self):
        pass
        
    def run(self):
        print 'version',versionstr
        return


#custom build_py overwrites version.py with a version overwriting the revno-generating version.py
class ao_build_py(du_build_py):
    def run(self):
        from os import path
        res = du_build_py.run(self)
        
        versfile = path.join(self.build_lib,'AstroObject','version.py')
        print 'freezing version number to',versfile
        with open(versfile,'w') as f: #this overwrites the actual version.py
            f.write(self.get_version_py())
        
        return res
        
    def get_version_py(self):
        import datetime
        from AstroObject.version import _frozen_version_py_template
        from AstroObject.version import version,major,minor,bugfix,isdev,devstr
        
        
        timestamp = str(datetime.datetime.now())
        t = (timestamp,version,major,minor,bugfix,isdev,devstr)
        return _frozen_version_py_template%t
        


setup(
    name = "AstroObject",
    version = versionstr,
    packages = ['AstroObject'],
    package_data = {'':['Defaults.yaml']},
    install_requires = ['distribute','pyfits>=2.4','numpy>=1.5','scipy>=0.9',"PyYAML>=3.10",'progressbar'],
    test_suite = 'tests',
    author = "Alexander Rudy",
    author_email = "dev@alexrudy.org",
    cmdclass = {
        'build_py' : ao_build_py,
        'version' : Version
    }
)
