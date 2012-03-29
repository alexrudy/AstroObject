# 
#  AstroCache.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-12-22.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.3.3
# 

# Standard Scipy Toolkits
import numpy as np
import scipy as sp

import yaml

# Standard Python Modules
import math, copy, sys, time, logging, os
import argparse

# Submodules from this system
from Utilities import *

__all__ = ["CacheManager","Cache","NumpyCache","YAMLCache","ConfigCache"]


    
class Cache(object):
    """A caching object"""
    def __init__(self, regenerater, reloader, resaver):
        super(Cache, self).__init__()
        self.regenerater = regenerater
        self.reloader = reloader
        self.resaver = resaver
        self.enabled = True
        self.saving = True
        self.reset()
    
    def reset(self):
        """docstring for reset"""
        self.data = None
        self.loaded = False
        self.generated = False
        self.saved = False
        self.ready = False
        
    
    def reload(self):
        """Reload this Cache from a file."""
        if self.ready or not self.enabled:
            return self.loaded
        try:
            data = self.reloader()
        except IOError as e:
            self.loaded = False
        else:
            self.data = data
            self.loaded = True
            self.ready = True
        return self.loaded
        
    def regenerate(self):
        """Regenerate this Cache and save to a file."""
        if not self.ready:
            try:
                data = self.regenerater()
            except Exception:
                self.generated = False
                raise
            else:
                self.data = data
                self.generated = True
                self.ready = True
        
        if not self.saved and self.saving:
            try:
                self.resaver(self.data)
            except Exception as e:
                print e
                self.saved = False
            else:
                self.saved = True
            
        return self.generated
            
    def __call__(self):
        """Return the data"""
        if self.ready:
            return self.data
        elif self.enabled and self.reload():
            return self.data
        elif self.regenerate():
            return self.data
        else:
            raise CacheError("Unable to load cache.")
            
            
class CacheManager(dict):
    """A cache management dictionary with some useful features."""
    def __init__(self, *args, **kwargs):
        super(CacheManager, self).__init__()
        self.caches = dict(*args,**kwargs)

    def __getitem__(self,key):
        """Get a keyed item"""
        return self.caches[key]()
        
    def __setitem__(self,key,value):
        """Set a keyed item"""
        if isinstance(value,Cache):
            self.caches[key] = value
        else:
            raise TypeError("Dictionary accepts %s, given %s" % (type(Cache),type(value)))
    
    def __delitem__(self,key):
        """Delete item"""
        del self.caches[key]
        
    def __iter__(self):
        """Dictionary iterator call."""
        return self.caches.iterkeys()
        
    def __contains__(self,item):
        """Dictionary contain testing"""
        return item in self.caches
        
    def keys(self):
        """Dictionary keys"""
        return self.caches.keys()
    
    def flag(self,flag,value,*caches):
        """Flag all caches"""
        if caches == None:
            caches = self.list()
        for cache in caches:
            setattr(self.caches[cache],flag,value)
    
    def reset(self):
        """Reset all caches"""
        for cache in self:
            self.caches[cache].reset()
            
    def check(self,key):
        """Check a cache for validity"""
        cache = self.caches[key]
        try:
            loaded = cache.reloader()
        except IOError as e:
            return False
        generated = cache.regenerater()
        try:
            result = loaded == generated
        except Exception as e:
            return False
        return result
    
def YAMLCache(regenerator,filename):
    """Return a cache object for YAML files."""
    def resaver(data):
        with open(filename,"w") as stream:
            yaml.dump(data,stream,default_flow_style=False)
    def reloader():
        with open(filename,"r") as stream:
            return yaml.load(stream)
    return Cache(regenerator,reloader,resaver)
    
def ConfigCache(config,filename):
    """Return a cache object for AstroObject.AstroConfig.Config objects"""
    regenerater = lambda : config
    def resaver(data):
        data.save(filename)
    def reloader():
        config.load(filename,silent=False)
        return config
    return Cache(regenerater,reloader,resaver)
    
def NumpyCache(regenerater,filename):
    """Return a cache object for Numpy Arrays"""
    resaver = lambda data: np.save(filename,data)
    reloader = lambda : np.load(filename)
    return Cache(regenerater,reloader,resaver)
