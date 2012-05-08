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
    def write(self,stack,clobber=False):
        """Write this file to the filename"""
        raise NotImplementedError
        
    @abstractmethod
    def open(self):
        """Open this file from the filename"""
        raise NotImplementedError
    
    def validate_filename(self,filename):
        """Return true if a filename is included in the list of extensions"""
        filename, extension = os.path.splitext(filename)
        if extension.lower() not in self.__extensions__:
            msg = "Filename '%s' does not have a valid extension. (Use %r)" % (filename,self.__extensions__)
            raise NotImplementedError(msg)
        