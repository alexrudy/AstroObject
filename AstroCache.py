# 
#  AstroCache.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-12-22.
#  Copyright 2011 Alexander Rudy. All rights reserved.
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
import math, copy, sys, time, logging, os
import argparse

# Submodules from this system
from Utilities import *

__all__ = ["CacheManager","CacheIOError"]

class CacheError(Exception):
    """Error in caching"""
    pass

class CacheIOError(CacheError):
    """Error caused when trying to load caches"""
    pass

class CacheStateError(CacheError):
    """Error caused by a cache with a state that doesn't work with the current call."""
    pass
                

class Cache(object):
    """A simple cache object"""
    def __init__(self,name=None,generate=None,load=None,stage=None,**kwargs):
        super(Cache, self).__init__()
        self.name = name
        self.cache_generate = generate
        self.cache_load = load
        self.stage = stage
        self.regenerate = False
        self.generated = False
        self.loaded = False
        self.log = logging.getLogger(__name__)
        self.data = False
        
    def load(self):
        """Load the contents of this cache into the cache object, using the load function."""
        if self.loaded:
            raise CacheStateError("Cannot doubly load cache")
        try:
            self.data = self.cache_load()
        except CacheIOError as e:
            self.cache_msg = str(e)
            self.log.debug("%(name)s Cache Load Failure. %(msg)s." % { 'name': self.name, 'msg': self.cache_msg })
            self.regenerate = True
        else:
            self.loaded = True
            self.log.log(2,"%(name)s Cache Loaded" % { 'name': self.name } )
        return self.loaded
        
    def generate(self):
        """Generate the cache files."""
        if not self.generated and self.regenerate:
            try:
                self.data = self.cache_generate()
            except CacheIOError as e:
                self.cache_msg = str(e)
                self.log.critical("%(name)s Cache Save Failure. %(msg)s." % { 'name': self.name, 'msg': self.cache_msg })
                raise
            else:
                self.log.debug("%(name)s generated Cache Files." % { 'name': self.name })
                self.regenerate = False
                self.generated = True
                self.loaded = True
        return self.generated
    
    def __call__(self):
        """Call this cache to extract data"""
        return self.data
    
    def trigger(self):
        """Trigger this cache to regenerate"""
        if self.generated:
            raise CacheStateError("Cannot trigger cache after it has already been generated...")
        if not self.regenerate:
            self.regenerate = True
            return self.regenerate
        return False
        
class NumpyCache(Cache):
    """A cache of a numpy array"""
    def __init__(self, directory = "", filename = "cache.npy", **kwargs):
        super(NumpyCache, self).__init__(**kwargs)
        self.directory = directory
        self.filename = filename
        self.cache_gen = self.cache_generate
        self.cache_get = self.cache_load
        self.cache_generate = self.write
        self.cache_load = self.read
        self.fullname = os.path.join(self.directory,self.filename)
        
    def write(self):
        """Write a numpy file for this data item"""
        if not self.generated and self.regenerate:
            try:
                self.data = self.cache_gen()
                np.save(self.fullname,self.data)
            except Exception as e:
                self.cache_msg = str(e)
                self.log.critical("%(name)s generating Cache Files: %(msg)s" % { 'name': self.name, 'msg': self.cache_msg })
                raise
            else:
                self.log.debug("%(name)s generated Cache Files" % { 'name': self.name })
                return self.data
    
    def read(self):
        """Read a numpy file for this data item"""
        try:
            self.data = np.load(self.fullname)
        except IOError as e:
            self.cache_msg = str(e)
            raise CacheIOError(self.cache_msg)
        return self.data
            

class CacheManager(object):
    """An object for maintaining caches"""
    def __init__(self,**kwargs):
        super(CacheManager, self).__init__()
        self.log = logging.getLogger(__name__)
        self.log.start()
        self.caches = {}
        self.enabled = True
        
    def registerNPY(self,name,generate=None,stage=None,directory=None,filename=None,**kwargs):
        """Register a Numpy Cache"""
        if generate == None:
            raise CacheError("Cache %s must specify generate function" % name)
        cache = NumpyCache(name=name,generate=generate,load=lambda : None,stage=stage,directory=directory, filename=filename, **kwargs)
        self.caches[name] = cache
        self.log.debug("Registered Cache %s" % name)
    
    def register(self,name,generate=None,load=None,stage=None,directory=None):
        """Register a new cache, which will then be managed by this cache manager"""
        if generate == None:
            raise CacheError("Cache %s must specify generate function" % name)
        if load == None:
            raise CacheError("Cache %s must specify load function" % name)
        cache = Cache(name,generate,load,stage=stage,directory=directory)
        self.caches[name] = cache
        self.log.debug("Registered Cache %s" % name)
    
    def didLoad(self,*caches):
        """Ask if all of the provided caches did load"""
        loaded = True
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            loaded &= self.caches[cache].loaded
        return loaded
    
    def shouldGenerate(self,*caches):
        """Ask if the caches should regenerate"""
        generate = False
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            generate |= self.caches[cache].regenerate
        return generate
    
    def generate(self,*caches):
        """Generate caches for each of the called items"""
        generated = []
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            if self.caches[cache].generate():
                generated += [cache]
        return generated
        
    def load(self,*caches):
        """Load the caches into memory"""
        loaded = []
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            if self.caches[cache].load():
                loaded += [cache]
        return loaded
        
    def trigger(self,*caches):
        """Trigger the caches to regenerate"""
        triggered = []
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            if self.caches[cache].trigger():
                triggered += [cache]
        return triggered
    
    def get(self,cache):
        """Get a particular cache"""
        if self.shouldGenerate(cache) or not ( enabled or self.caches[cache].generated ):
            self.generate(cache)
        return self.caches[cache]()
        
    
        