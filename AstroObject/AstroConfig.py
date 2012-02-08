# 
#  AstroConfig.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-02-08.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.3.0a1
# 

# Standard Scipy Toolkits
import numpy as np
import pyfits as pf
import scipy as sp

# Scipy Extras
from scipy import ndimage
from scipy.spatial.distance import cdist
from scipy.linalg import norm

# Standard Python Modules
import math, copy, sys, time, logging, os,collections
import yaml

# Submodules from this system
from Utilities import *

class Configuration(dict):
    """Adds extra methods to dictionary for configuration"""
    def __init__(self, *args, **kwargs):
        super(Configuration, self).__init__(*args, **kwargs)
        self.log = logging.getLogger(__name__)
    
    def merge(self,other):
        """Merge another configuration into this (the master)"""
        self._merge(self,other)
        
    def _merge(self,d,u):
        """Recursive merging function"""
        if len(u)==0:
            return d
        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                r = update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d
        
    def load(self,filename,silent=True):
        """Loads a configuration from a yaml file, and merges it into the master"""
        loaded = False
        try:
            with open(filename,'r') as stream:
                new = yaml.load(stream)
        except IOError:
            if silent:
                self.log.warning("Could not load configuration from file:")
            else:
                raise
        else:
            self.merge(new)
            loaded = True
        return loaded
    

class StructuredConfiguration(Configuration):
    """A structured configuration with some basic defaults for AstroObject-type classes"""
    def __init__(self,  *args, **kwargs):
        super(StructuredConfiguration, self).__init__(*args, **kwargs) 
        self["Configurations"] = {}
        self["Configurations"]["This"] = "AO.config.yaml"
        
    def setFile(self,name,filename=None):
        """Set configuration file"""
        if name not in self["Configurations"]:
            self["Configurations"][name] = filename
        self["Configurations"]["This"] = self["Configurations"][name]
        
    def load(self,filename=None,silent=True):
        """Load from a file"""
        if filename == None:
            filename = self["Configurations"]["This"]
        return super(StructuredConfiguration, self).load(filename,silent)
        