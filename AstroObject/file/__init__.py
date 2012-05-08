# -*- coding: utf-8 -*-
# 
#  __init__.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-05-08.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 


import os
from abc import ABCMeta, abstractmethod, abstractproperty

class File(object):
    """A generic file object"""
    
    __metaclass__ = ABCMeta
    
    __extensions__ = []
    
    @abstractmethod
    def __write__(self,filename,clobber=False):
        """Write this file to the filename"""
        raise NotImplementedError("Can't write an abstract file")
        
    @abstractmethod
    def __read__(self,filename,framename):
        """Open this file from the filename"""
        raise NotImplementedError("Can't read an abstract file")
        
    @abstractmethod
    def __getstack__(self):
        """Return the stack of file-frames for this file."""
        raise NotImplementedError("Can't get the stack for this file.")
        
    @abstractmethod
    def __setstack__(self,stack):
        """Sets the stack for this file."""
        raise NotImplementedError("Can't get the stack for this file.")
        
    stack = abstractproperty(__getstack__,__setstack__)
    
    def validate_filename(self,filename):
        """Return true if a filename is included in the list of extensions"""
        filename, extension = os.path.splitext(filename)
        return extension.lower() in self.__extensions__
        
    
    
class FileFrame(object):
    """An abstract file frame."""
    
    __metaclass__ = ABCMeta
    
    @abstractproperty
    def data(self):
        """Get the data for this frame"""
        raise NotImplementedError("Can't get the stack for this file.")
        
    @abstractproperty
    def label(self):
        """Get the label for this frame"""
        raise NotImplementedError("Can't get the label for this file.")
        
    @abstractproperty
    def header(self):
        """The header data for this file."""
        raise NotImplementedError("Header hasn't been implemented here.")
    
class SimpleFrame(object):
    """A very, very basic frame for things that basically only have data."""
    def __init__(self, data = None, label = None):
        super(SimpleFrame, self).__init__()
        self._data = data
        self._label = label
        self._header = {}
        
    @property
    def header(self):
        """Return the header data"""
        return self._header
    
    @property
    def data(self):
        return self._data
    
    @property
    def label(self):
        return self._label
        