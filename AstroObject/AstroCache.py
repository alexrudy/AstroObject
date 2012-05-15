# -*- coding: utf-8 -*-
# 
#  AstroCache.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-12-22.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.5.3-p1
# 

# Standard Scipy Toolkits
import numpy as np
import scipy as sp

import yaml

# Standard Python Modules
import sys
from datetime import timedelta, datetime
import logging
import os
import collections
import hashlib
import shutil

# Submodules from this system
from .AstroConfig import DottedConfiguration
from .AstroObjectLogging import logging

__all__ = ["CacheManager","Cache","NumpyCache","YAMLCache"]
__log__ = logging.getLogger(__name__)

    
class Cache(object):
    """A caching object"""
    def __init__(self, regenerater, reloader, resaver, filename):
        super(Cache, self).__init__()
        self.regenerater = regenerater
        self.reloader = reloader
        self.resaver = resaver
        self.filename = filename
        self.modes = {
            "read" : "r",
            "write": "w",
        }
        self.saving = False
        self.loading = False

        
        self.reset()
    
    def reset(self):
        """docstring for reset"""
        self.data = None
        self.loaded = False
        self.generated = False
        self.saved = False
        self.ready = False
        
    def __setfilepath__(self,filepath):
        """Set the Filepath for this object"""
        self.filepath = filepath
        self.fullpath = os.path.join(self.filepath,self.filename)
        self.saving = True
        self.loading = True
        
    
    def reload(self):
        """Reload this Cache from a file."""
        if self.ready or not self.loading:
            return self.loaded
        try:
            with open(self.fullpath,self.modes["read"]) as loadstream:
                data = self.reloader(loadstream)
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
                with open(self.fullpath,self.modes["write"]) as savestream:
                    self.resaver(self.data,savestream)
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
        elif self.loading and self.reload():
            return self.data
        elif self.regenerate():
            return self.data
        else:
            raise CacheError("Unable to load cache.")
            
            
class CacheManager(collections.MutableMapping):
    """A cache management dictionary with some useful features."""
    def __init__(self,hashable,destination,expiretime=100000):
        super(CacheManager, self).__init__()
        self._caches = {}
        self._flags = {}
        self.log = __log__
        
        # Hash Setup
        _hash = hashlib.sha1()
        _hash.update(hashable)
        self._hashhex = _hash.hexdigest()
        
        # Filenames
        self._cache_basename = destination
        if not os.path.isdir(self._cache_basename):
            self.disable()
            self.log.debug("Disabling Caching, Cache Base Directory '%s' not found." % self._cache_basename)
        self._database_filename = os.path.join(self._cache_basename,"cache_database.yaml")
        self._cache_dirname = os.path.join(self._cache_basename,self.hashhex)
        if not os.path.isdir(self._cache_dirname):
            os.mkdir(self._cache_dirname)
            self.log.debug("Cache Directory Created: %s " % self._cache_dirname)
        
        
        # Timing Information
        self.timeformat = "%Y-%m-%dT%H:%M:%S"
        self._createdate = datetime.now()
        self._expiretime = datetime.now() - timedelta(0,expiretime)
        
        self.log.debug("Cache %s Created" % self.hashhex)
        
        # Database Setup
        self._database = DottedConfiguration({})
        self._database.dn = DottedConfiguration
        self._database.load(self._database_filename)
        self._database[self.hashhex+".update"] = self._createdate.strftime(self.timeformat)

        self.expire()

        self.log.debug("Added Cache to the Database: %s" % self.hashhex)

    @property
    def hashhex(self):
        """Accessor method for this cache manager's current hash."""
        return self._hashhex
        
    
    def __str__(self):
        """String for this cache"""
        return self.hashhex
    
    def __getitem__(self,key):
        """Get a keyed item"""
        return self._caches[key]()
        
    def __setitem__(self,key,value):
        """Set a keyed item"""
        if isinstance(value,Cache):
            value.__setfilepath__(self._cache_dirname)
            self._caches[key] = value
            self._database[self.hashhex+".Files."+key] = value.filename            
            for flag in self._flags:
                self.flag(flag,self._flags[flag],key)
        else:
            raise TypeError("Dictionary accepts %s, given %s" % (type(Cache),type(value)))
    
    def __delitem__(self,key):
        """Delete item"""
        del self._caches[key]
        
    def __iter__(self):
        """Dictionary iterator call."""
        return self._caches.iterkeys()
        
    def __contains__(self,item):
        """Dictionary contain testing"""
        return item in self._caches
        
    def __len__(self):
        """Length of the dictionary"""
        return len(self._caches)
    
    def flag(self,flag,value,*caches):
        """Flag all caches"""
        if len(caches) == 0:
            caches = self.keys()
            self._flags[flag] = value
        for cache in caches:
            setattr(self._caches[cache],flag,value)
    
    def reset(self):
        """Reset all caches"""
        for cache in self:
            self._caches[cache].reset()
    
    def close(self):
        """Close this cache system."""
        self._database.save(self._database_filename)
        self.log.debug("Saved Database: %s" % self._database_filename)
        
    def expire(self,*hashhexs):
        """Check for, and possibly clean, the given hashhexs"""
        if len(hashhexs) is 0:
            hashhexs = self._database.keys()
        for hashhex in hashhexs:
            if datetime.strptime(self._database[hashhex].get("update","2000-01-01T00:00:00"),self.timeformat) < self._expiretime:
                self.clear(hashhex)
    
    def clear(self,*hashhexs):
        """docstring for clean_cachespace"""
        if len(hashhexs) is 0:
            hashhexs = self._database.keys()
        for hashhex in hashhexs:
            ecpath = os.path.join(self._cache_basename,hashhex)
            if os.path.exists(ecpath):
                shutil.rmtree(ecpath)
            if hashhex == self.hashhex:
                os.mkdir(self._cache_dirname)
            else:
                del self._database[hashhex]
            
        return hashhexs
    
    def disable(self,*caches):
        """Disable this cacheing system"""
        self.flag('loading',False,*caches)
        self.flag('saving',False,*caches)
    
    def enable(self,*caches):
        """Disable this cacheing system"""
        self.flag('loading',True,*caches)
        self.flag('saving',True,*caches)
    
    
def YAMLCache(regenerator,filename):
    """Return a cache object for YAML files."""
    def resaver(data,stream):
        yaml.dump(data,stream,default_flow_style=False)
    def reloader(stream):
        return yaml.load(stream)
    return Cache(regenerator,reloader,resaver,filename)
    
def NumpyCache(regenerater,filename):
    """Return a cache object for Numpy Arrays"""
    resaver = lambda data, stream: np.save(stream,data)
    reloader = lambda stream: np.load(stream)
    return Cache(regenerater,reloader,resaver,filename)
