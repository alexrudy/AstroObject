# -*- coding: utf-8 -*-
# 
#  AstroConfig.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-02-08.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.5-a1
# 
"""
YAML-based Configuration Dictionaries: :mod:`AstroConfig`
=========================================================

This module provides structured, YAML based, deep dictionary configuration objects. The objects have a built-in deep-update function and use deep-update behavior by default. They act otherwise like dictionaries, and handle thier internal operation using a storage dictionary. The objects also provide a YAML configuration file reading and writing interface.

.. inheritance-diagram::
    AstroObject.AstroConfig.Configuration
    AstroObject.AstroConfig.StructuredConfiguration
    :parts: 1

Basic Configurations: :class:`Configuration`
--------------------------------------------

.. autoclass::
    AstroObject.AstroConfig.Configuration
    :members:

Structured Configurations: :class:`StructuredConfiguration`
-----------------------------------------------------------

.. autoclass::
    AstroObject.AstroConfig.StructuredConfiguration
    :members:
    :inherited-members:


"""
# Standard Python Modules
import math, copy, sys, time, logging, os,collections, re
import yaml

# Submodules from this system
from Utilities import *

class Configuration(collections.MutableMapping):
    """Adds extra methods to dictionary for configuration"""
    def __init__(self, *args, **kwargs):
        super(Configuration, self).__init__()
        self.log = logging.getLogger(__name__)
        self._store = dict(*args, **kwargs)
        
    def __repr__(self):
        """String representation of this object"""
        return repr(self.store)
        
    def __str__(self):
        """String for this object"""
        return "<Configuration %r >" % repr(self)
        
    def __getitem__(self,key):
        """Dictionary getter"""
        return self._store.__getitem__(key)
        
    def __setitem__(self,key,value):
        """Dictonary setter"""
        return self._store.__setitem__(key,value)
        
    def __delitem__(self,key):
        """Dictionary delete"""
        return self._store.__delitem__(key)
        
    def __iter__(self):
        """Return an iterator for this dictionary"""
        return self._store.__iter__()
        
    def __contains__(self,key):
        """Return the contains boolean"""
        return self._store.__contains__(key)
    
    def __len__(self):
        """Length"""
        return self._store.__len__()
    
    def update(self,other,deep=True):
        """Update the dictionary using :meth:`merge`.
        
        :param dict-like other: The other dictionary to be merged.
        :param bool deep: Whether to use deep merge (:meth:`merge`) or shallow update.
        
        """
        if deep:
            self.merge(other)
        else:
            self._store.update(other)
    
    def merge(self,other):
        """Merge another configuration into this one (the master).
        
        :param dict-like other: The other dictionary to be merged.
        
        """
        self._merge(self,other)
    
    def _merge(self,d,u):
        """Recursive merging function for internal use."""
        if len(u)==0:
            return d
        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                r = self._merge(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d
    
    def save(self,filename,silent=True):
        """Save this configuration as a YAML file. YAML files generally have the ``.yaml`` or ``.yml`` extension. If the filename ends in ``.dat``, the configuration will be saved as a raw dictionary literal.
        
        :param string filename: The filename on which to save the configuration.
        :param bool silent: Unused.
        
        """
        with open(filename,"w") as stream:
            stream.write("# Configuration: %s\n" % filename)
            if re.search(r"(\.yaml|\.yml)$",filename):
                yaml.dump(self.store,stream,default_flow_style=False)
            elif re.search(r"\.dat$",filename):
                stream.write(str(self.store))
            else:
                raise ValueError("Filename Error, not (.dat,.yaml,.yml): %s" % filename)
        
    def load(self,filename,silent=True):
        """Loads a configuration from a yaml file, and merges it into the master configuration.
        
        :param string filename: The filename to load from.
        :param bool silent: Silence IOErrors which might arise due to a non-existant configuration file. If this is the case, the failure to find a configuration file will be logged, will not raise an error.
        :raises IOError: if the file can't be found.
        :returns: boolean, whether the file was loaded.
        """
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
    
    @property
    def store(self):
        """Dictionary representing this configuration. This property should be used if you wish to have a 'true' dictionary object. It is used internally to write this configuration to a YAML file.
        """
        return self._store
        
    def extract(self):
        """Extract the dictionary from this object.
        
        .. deprecated:: 0.4
            use :attr:`store`
        
        """
        return self._store

class StructuredConfiguration(Configuration):
    """A structured configuration with some basic defaults for AstroObject-type classes"""
    def __init__(self,  *args, **kwargs):
        super(StructuredConfiguration, self).__init__(*args, **kwargs) 
        if "Configurations" not in self:
            self["Configurations"] = {}
        if "This" not in self["Configurations"]:
            self["Configurations"]["This"] = "AO.config.yaml"
        
    def setFile(self,filename=None,name=None):
        """Set the default/current configuration file for this configuration.
        
        The configuration file set by this method will be used next time :meth:`load` or :meth:`save` is called with no filename.
        
        :param string filename: The filename to load from.
        :param string name: The name key for the file.
        
        """
        if not filename:
            if not name:
                raise ValueError("Must provide name or filename")
            if name not in self["Configurations"]:
                raise KeyError("Key %s does not represent a configuration file." % name)
        else:
            if not name:
                name = os.path.basename(filename)
        if name not in self["Configurations"]:
            self["Configurations"][name] = filename
        self["Configurations"]["This"] = self["Configurations"][name]
    
    def save(self,filename=None):
        """Save the configuration to a YAML file. If ``filename`` is not provided, the configuration will use the file set by :meth:`setFile`.
        
        :param string filename: Destination filename.
        
        Uses :meth:`Configuration.save`.
        """
        if filename == None:
            filename = self["Configurations"]["This"]
        return super(StructuredConfiguration, self).save(filename)
    
        
    def load(self,filename=None,silent=True):
        """Load the configuration to a YAML file. If ``filename`` is not provided, the configuration will use the file set by :meth:`setFile`.
        
        :param string filename: Target filename.
        :param bool silent: Whether to raise an error if the target file cannot be found.
        
        Uses :meth:`Configuration.load`."""
        if filename == None:
            filename = self["Configurations"]["This"]
        return super(StructuredConfiguration, self).load(filename,silent)
        
