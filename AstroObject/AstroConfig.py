# 
#  AstroConfig.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-02-08.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.3.0
# 

# Standard Python Modules
import math, copy, sys, time, logging, os,collections, re
import yaml

# Submodules from this system
from Utilities import *

class Configuration(dict):
    """Adds extra methods to dictionary for configuration"""
    def __init__(self, *args, **kwargs):
        super(Configuration, self).__init__(*args, **kwargs)
        self.log = logging.getLogger(__name__)
    
    def update(self,other,deep=True):
        """Deep update by default"""
        if deep:
            self._merge(self,other)
        else:
            super(Configuration, self).update(other)
    
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
    
    def save(self,filename,silent=True):
        """Save as a file."""
        with open(filename,"w") as stream:
            stream.write("# Configuration: %s\n" % filename)
            if re.search(r"\.yaml$",filename):
                yaml.dump(self.extract(),stream,default_flow_style=False)
            elif re.search(r"\.dat$",filename):
                stream.write(str(self))
            else:
                raise ValueError("Filename Error, not (.dat,.yaml): %s" % filename)
        
    def load(self,filename,silent=True):
        """Loads a configuration from a yaml file, and merges it into the master"""
        loaded = False
        try:
            with open(filename,"r") as stream:
                new = yaml.load(stream)
        except IOError:
            if silent:
                self.log.warning("Could not load configuration from file: %s" % filename)
            else:
                raise
        else:
            self.merge(new)
            loaded = True
        return loaded
        
    def extract(self):
        """Extract the dictionary from this object"""
        return dict(self)
        
    def __repr__(self):
        """Representation of this dictionary."""
        return repr(dict(self))    

class StructuredConfiguration(Configuration):
    """A structured configuration with some basic defaults for AstroObject-type classes"""
    def __init__(self,  *args, **kwargs):
        super(StructuredConfiguration, self).__init__(*args, **kwargs) 
        if "Configurations" not in self:
            self["Configurations"] = {}
        if "This" not in self["Configurations"]:
            self["Configurations"]["This"] = "AO.config.yaml"
        
    
    def __repr__(self):
        """Representation of this dictionary."""
        return repr(dict(self))
        
    def setFile(self,filename,name=None):
        """Set configuration file"""
        if not name:
            name = os.path.basename(filename)
        if name not in self["Configurations"]:
            self["Configurations"][name] = filename
        self["Configurations"]["This"] = self["Configurations"][name]
    
    def save(self,filename=None):
        """Load from a file"""
        if filename == None:
            filename = self["Configurations"]["This"]
            print self.extract()
        return super(StructuredConfiguration, self).save(filename)
    
        
    def load(self,filename=None,silent=True):
        """Load from a file"""
        if filename == None:
            filename = self["Configurations"]["This"]
        return super(StructuredConfiguration, self).load(filename,silent)
        
