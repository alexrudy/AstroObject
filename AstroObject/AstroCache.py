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
from .AstroConfig import Configuration
from .AstroObjectLogging import logging
from .file.fileset import FileSet, HashedFileSet

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
            data = self.reloader(self.fullpath)
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
                self.resaver(self.data,self.fullpath)
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
    def __init__(self, destination,  hashable, enabled=True, expiretime=100000, autodiscover=True, dbfilebase=".AOCacheDB.yml"):
        super(CacheManager, self).__init__()
        self._caches = {}
        self._flags = {}
        self._filesets = {}
        self._autodiscover_value = autodiscover
        self.log = __log__
        
        # Timing Information
        self.timeformat = "%Y-%m-%dT%H:%M:%S"
        self._createdate = datetime.now()
        self._expiretime = datetime.now() - timedelta(0,expiretime)
        
        
        # Filenames
        self._cache_basename = os.path.relpath(os.path.join(destination,""))
        self._dbfilebase = dbfilebase
        self._dbfilename = os.path.join(self._cache_basename,self._dbfilebase)
        
        if (not os.path.isdir(self._cache_basename)) or (not enabled):
            self.disable()
            self.log.debug("Disabling Caching, Cache Base Directory '%s' not found." % self._cache_basename)
        
        # Database Setup
        self._database = Configuration({})
        self._database.dn = Configuration
        if self.enabled:
            self._database.load(self._dbfilename)
        
        # Main Hashed Fileset
        self._fileset = HashedFileSet( base = self._cache_basename, hashable = hashable, isopen = self.enabled, persist = True, autodiscover = self._autodiscover_value, dbfilebase = self._dbfilebase, timeformat = self.timeformat)
        self.log.debug("Cache FileSet Created: %s " % self._fileset.hash)
        self._filesets[self._fileset.hash] = self._fileset
        self._database[self._fileset.hash] = self._fileset.date.strftime(self.timeformat)
        self._reload_db_filesets()
        self.log.debug("Cache %s Created" % self.hash)
        

        
        self.expire()
        
        self.log.debug("Added Cache to the Database: %s" % self.hash)
    
    
    def __str__(self):
        """String for this cache"""
        return self.hash
    
    def __getitem__(self,key):
        """Get a keyed item"""
        return self._caches[key]()
        
    def __setitem__(self,key,value):
        """Set a keyed item"""
        if isinstance(value,Cache):
            value.__setfilepath__(self.set.directory)
            self._caches[key] = value
            if value.filename not in self.set:
                self.set.register(value.filename)
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
    
    def _reload_db_filesets(self):
        """Get the already-created hashed file-sets which are in the base directory."""
        for filepath in self._database:
            if os.path.isdir(filepath) and filepath not in self._filesets:
                self._filesets[filepath] = FileSet( base = self._cache_basename, name = filepath, persist = True, autodiscover = self._autodiscover_value, dbfilebase = self._dbfilebase, timeformat = self.timeformat )
                self._database[filepath] = self._filesets[filepath].date.strftime(self.timeformat)
        self._database.save(self._dbfilename)
        
    @property
    def enabled(self):
        """Check whether this fileset is enabled."""
        return self._flags.get('loading',True) or self._flags.get('saving',True)
    
    @property
    def hash(self):
        """Accessor for set's hash method"""
        return self.set.hash
    
    @property
    def set(self):
        """File set for the current hash."""
        return self._fileset
    
    def flag(self,flag,value,*caches):
        """Flag all caches"""
        if len(caches) == 0:
            caches = self.keys()
            self._flags[flag] = value
        for cache in caches:
            setattr(self._caches[cache],flag,value)
    
    def reset(self,*caches):
        """Reset all caches"""
        if len(caches) == 0:
            caches = self.keys()
        for cache in caches:
            self._caches[cache].reset()
    
    def close(self):
        """Close this cache system."""
        self.expire()
        for fs in self._filesets:
            self._filesets[fs].close(clean = False, check = False)
        self._database.save(self._dbfilename)
        self.log.debug("Saved Database: %s" % self._dbfilename)
        
    def expire(self,*hashhexs):
        """Check for, and possibly clean, the given hashhexs"""
        if len(hashhexs) is 0:
            hashhexs = self._database.keys()
        for hashhex in hashhexs:
            if datetime.strptime(self._database[hashhex],self.timeformat) < self._expiretime:
                self.clear(hashhex)
        self._database.save(self._dbfilename)
    
    def clear(self,*hashhexs):
        """docstring for clean_cachespace"""
        if len(hashhexs) is 0:
            hashhexs = self._database.keys()
        for hashhex in hashhexs:
            self._filesets[hashhex].close(clean = hashhex == self.hash, check = False)
            del self._database[hashhex]
        self._database.save(self._dbfilename)
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
    def resaver(data,filename):
        with open(filename,'w') as stream:
            yaml.dump(data,stream,default_flow_style=False)
    def reloader(filename):
        with open(filename,'r') as stream:
            return yaml.load(stream)
    return Cache(regenerator,reloader,resaver,filename)
    
def NumpyCache(regenerater,filename):
    """Return a cache object for Numpy Arrays"""
    resaver = lambda data, stream: np.save(stream,data)
    reloader = lambda stream: np.load(stream)
    return Cache(regenerater,reloader,resaver,filename)
