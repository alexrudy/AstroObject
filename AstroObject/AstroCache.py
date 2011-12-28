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
    def __init__(self,name=None,generate=None,load=None,save=None,stage=None,autosave=True,enabled=True,filename=None,directory=None,**kwargs):
        super(Cache, self).__init__()
        self.name = name
        self.cache_generate = generate
        self.cache_save = save
        self.cache_load = load
        self.stage = stage
        self.autosave = autosave
        self.enabled = enabled
        
        if filename == None:
            filename = self.name.replace(" ","")
        self.filename = os.path.basename(filename)
        if filename == "":
            raise CacheError("Filename is invalid: %s" % filename)
        if not self.filename.endswith(".cache"):
            self.filename += ".cache"
        
        if directory == None:
            directory = "Caches"
        if not os.path.isdir(directory):
            raise CacheError("Specified directory is invalid: %s" % directory)
        self.directory = directory
        self.fullname = os.path.join(self.directory,self.filename)
        
        
        # State Variables
        self.regenerate = False
        self.generated = False
        self.loaded = False
        self.ready = False
        self.saved = False
        
        self.log = logging.getLogger(__name__)
        
        self.data = None
        
    def load(self):
        """Load the contents of this cache into the cache object, using the load function."""
        if self.ready:
            return self.loaded
        try:
            with file(self.fullname,'r') as stream:
                self.data = self.cache_load(stream)
        except (IOError,CacheIOError) as e:
            self.cache_msg = str(e)
            self.log.debug("%(name)s Cache Load Failure. %(msg)s." % { 'name': self.name, 'msg': self.cache_msg })
            self.regenerate = True
        else:
            self.loaded = True
            self.ready = True
            self.log.log(2,"%(name)s Cache data loaded" % { 'name': self.name } )
        return self.loaded
        
    def generate(self,save=True):
        """Generate the cache data."""
        if self.ready:
            return self.generated
        if self.regenerate:
            try:
                self.data = self.cache_generate()
            except (IOError,CacheError) as e:
                self.cache_msg = str(e)
                self.log.critical("%(name)s Cache Generate Failure. %(msg)s." % { 'name': self.name, 'msg': self.cache_msg })
                raise
            else:
                self.log.debug("%(name)s generated Cache data." % { 'name': self.name })
                self.regenerate = False
                self.generated = True
                self.ready = True
        if self.autosave and save and self.enabled:
            self.generated &= self.save()
        return self.generated
    
    def save(self):
        """Save the cache files"""
        if not self.enabled or not self.ready:
            return False
        if self.ready and not self.regenerate:
            try:
                with file(self.fullname,'w') as stream:
                    self.cache_save(stream,self.data)
            except (IOError,CacheIOError) as e:
                self.cache_msg = str(e)
                self.log.critical("%(name)s Cache Save Failure. %(msg)s." % { 'name': self.name, 'msg': self.cache_msg })
                raise
            else:
                self.log.debug("%(name)s saved Cache Files." % { 'name': self.name })
                self.saved = True
        else:
            raise CacheStateError("Data needs to be %s" % ("regenerated" if self.regenerate else "generated"))
        return self.saved
        
    def clear(self):
        """Clear the cache file"""
        if self.loaded:
            self.data = None
            self.loaded = False
            self.ready = False
        if self.saved:
            self.saved = False
        if os.access(self.fullname,os.W_OK):
            os.remove(self.fullname)
            self.log.debug("Removed File %s" % self.fullname)
    
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
    def __init__(self, **kwargs):
        super(NumpyCache, self).__init__(**kwargs)
        if self.cache_load != None:
            raise CacheError("Function provided for LOAD in NPY cache... hmmm")
        self.cache_save = self.write
        self.cache_load = self.read
        
    def write(self,stream,data):
        """Write a numpy file for this data item"""
        try:
            self.log.log(2,"Writing NPY Cache to %s" % self.fullname)
            np.save(stream,data)
        except Exception as e:
            self.cache_msg = str(e)
            self.log.critical("%(name)s writing Cache Files: %(msg)s" % { 'name': self.name, 'msg': self.cache_msg })
            raise
        else:
            self.log.debug("%(name)s writing Cache Files" % { 'name': self.name })
    
    def read(self,stream):
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
        if directory == None and self.directory != None:
            directory = self.directory            
        cache = NumpyCache(name=name,generate=generate,stage=stage,directory=directory, filename=filename, **kwargs)
        self.caches[name] = cache
        self.log.debug("Registered Cache %s" % name)
    
    def register(self,name,generate=None,load=None,save=None,stage=None,directory=None,**kwargs):
        """Register a new cache, which will then be managed by this cache manager"""
        if generate == None:
            raise CacheError("Cache %s must specify generate function" % name)
        if load == None:
            raise CacheError("Cache %s must specify load function" % name)
        if save == None:
            raise CacheError("Cache %s must specify save function" % name)
        if directory == None and self.directory != None:
            directory = self.directory
        cache = Cache(name,generate,load,save,stage=stage,directory=directory,**kwargs)
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
        
    def save(self,*caches):
        """Save the caches to files"""
        saved = []
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            if self.caches[cache].save():
                saved += [cache]
        return saved
    
    def clear(self,*caches):
        """Save the caches to files"""
        cleared = []
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            if self.caches[cache].clear():
                cleared += [cache]
        return cleared
    
        
    def trigger(self,*caches):
        """Trigger the caches to regenerate"""
        triggered = []
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            if self.caches[cache].trigger():
                triggered += [cache]
        return triggered
        
    def disable(self,*caches):
        """Disable Caching"""
        disabled = []
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            if self.caches[cache].enabled:
                disabled += [cache]
            self.caches[cache].enabled = False
        return disabled
        
    def enabled(self,*caches):
        """Enable caching"""
        enabled = []
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            if self.caches[cache].enabled:
                enabled += [cache]
            self.caches[cache].enabled = True
        return enabled
        
    def get(self,cache):
        """Get a particular cache"""
        if self.shouldGenerate(cache):
            self.generate(cache)
        return self.caches[cache]()
        
    
        
