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

import yaml

# Standard Python Modules
import math, copy, sys, time, logging, os
import argparse

# Submodules from this system
from Utilities import *

__all__ = ["CacheManager","CacheIOError","YAMLCache"]

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
            self.log.debug("%(name)s Cache Load Unecessary: already %(result)s." % { 'name': self.name, 'result': "loaded" if self.loaded else "generated" })
            return self.loaded
        if not self.enabled:
            self.regenerate = True
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
        if self.generated:
            self.log.debug("%(name)s Cache Generate Unecessary: already %(result)s." % { 'name': self.name, 'result': "loaded" if self.loaded else "generated" })
            return self.generated
        else:
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
            self.log.log(2,"Cache not saved because it is not %s" % "enabled" if not self.enabled else "ready")
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
                self.log.debug("%(name)s saved Cache Files to %(fn)s." % { 'name': self.name ,'fn':self.fullname})
                self.saved = True
        else:
            raise CacheStateError("Data needs to be %s" % ("regenerated" if self.regenerate else "generated"))
        return self.saved
       
    def reset(self):
        """Reset the cache object to its starting state"""
        self.regenerate = False
        self.generated = False
        self.loaded = False
        self.ready = False
        self.saved = False
        self.data = None
        
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

class YAMLCache(Cache):
    """A cached YAML document"""
    def __init__(self, **kwargs):
        super(YAMLCache, self).__init__(**kwargs)
        if self.cache_load != None:
            raise CacheError("Function provided for LOAD in YAML cache... hmmm")
        self.cache_save = self.write
        self.cache_load = yaml.load
        
    def write(self,stream,data):
        """Write the cache"""
        yaml.dump(data,stream,default_flow_style=False)
        
        
           

class CacheManager(object):
    """An object for maintaining caches"""
    def __init__(self,name=None,**kwargs):
        super(CacheManager, self).__init__()
        if name == None:
            self.name = self.__class__.__name__
        else:
            self.name = name
        self.log = logging.getLogger(__name__)
        self.caches = {}
        self.enabled = True
        self.directory = None
        
    def registerCustom(self,name,kind=Cache,directory=None,**kwargs):
        """Register a custom type of caching object"""
        if directory == None and self.directory != None:
            directory = self.directory
        cache = kind(name=name,directory=directory,**kwargs)
        self.caches[name] = cache
        self.log.debug("Registered Cache %s of kind %s" % (name,kind))
        
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
    
    def check(self,*caches,**kwargs):
        """docstring for check"""
        self.load()
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        check = self.shouldGenerate(*caches)
        if "master" in kwargs:
            check |= not self.checkCache(kwargs["master"])
        if check:
            self.trigger()
            self.log.info("Caches appear out of date. Regenerating.")
        return check
    
    def checkCache(self,*caches):
        """Checks to see if the cache is the same as the generated output."""
        cached = True
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            cacheObject = self.caches[cache]
            cacheObject.reset()
            if not cacheObject.load():
                cached = False
                self.log.log(2,"Manager thinks %(cache)s %(result)s need regenerating, because it couldn't be loaded" % {'cache':cache,'result':"does"})
            else:
                saved = cacheObject()
                cacheObject.reset()
                cacheObject.generate(save=False)
                gened = cacheObject()
                cacheObject.reset()
                result = saved == gened
                cached &= result
                if not result:
                    with open("Partials/CACHETEST.dat",'w') as stream:
                        stream.write(str(saved)+"\n\n\n"+str(gened))
                self.log.log(2,"Manager thinks %(cache)s %(result)s need regenerating" % {'cache':cache,'result':"doesn't" if result else "does"})
        self.log.log(5,"Manager %(action)s the caches %(list)s" % {'action': "checked",'list': str(caches) })
        return cached
    
    def generate(self,*caches):
        """Generate caches for each of the called items"""
        generated = []
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            if self.caches[cache].generate():
                generated += [cache]
        self.log.log(5,"Manager %(action)s the caches %(list)s" % {'action': "generated",'list': str(generated) })
        return generated
        
    def load(self,*caches):
        """Load the caches into memory"""
        loaded = []
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            if self.caches[cache].load():
                loaded += [cache]
        self.log.log(5,"Manager %(action)s the caches %(list)s" % {'action': "loaded",'list': str(loaded) })
        return loaded
        
    def save(self,*caches):
        """Save the caches to files"""
        saved = []
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            if self.caches[cache].save():
                saved += [cache]
        self.log.log(5,"Manager %(action)s the caches %(list)s" % {'action': "saved",'list': str(saved) })
        return saved
    
    def reset(self):
        """docstring for reset"""
        reset = []
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            self.caches[cache].reset()
            reset += [cache]
        self.log.log(5,"Manager %(action)s the caches %(list)s" % {'action': "reset",'list': str(reset) })
        return reset
        
    
    
    def clear(self,*caches):
        """Save the caches to files"""
        cleared = []
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            if self.caches[cache].clear():
                cleared += [cache]
        self.log.log(5,"Manager %(action)s the caches %(list)s" % {'action': "cleared",'list': str(cleared) })
        return cleared
    
        
    def trigger(self,*caches):
        """Trigger the caches to regenerate"""
        triggered = []
        if len(caches) == 0:
            caches = tuple(self.caches.keys())
        for cache in caches:
            if self.caches[cache].trigger():
                triggered += [cache]
        self.log.log(5,"Manager %(action)s the caches %(list)s" % {'action': "triggered",'list': str(triggered) })
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
        self.log.log(5,"Manager %(action)s the caches %(list)s" % {'action': "disabled",'list': str(disabled) })
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
        self.log.log(5,"Manager %(action)s the caches %(list)s" % {'action': "enabled",'list': str(enabled) })
        return enabled
        
    def get(self,cache):
        """Get a particular cache"""
        if self.shouldGenerate(cache):
            self.generate(cache)
        return self.caches[cache]()
        
    
        
