# -*- coding: utf-8 -*-
# 
#  fits.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-05-08.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 

import os
import pyfits as pf
import collections

from . import File, FileFrame

class FITSFile(File):
    """A fits file implementation"""
    def __init__(self, filename=None):
        super(FITSFile, self).__init__()
        self.filename = filename
        
        self._stack = []
        self.label = None
        if filename is not None:
            self.label = os.path.splitext(os.path.split(filename)[1])[0]
            self.__read__(filename)
     
    __extensions__ = ['.fit','.fits']
    
    def __read__(self,filename):
        """Read a fits file from the filename"""
        if not self.validate_filename(filename):
            raise NotImplementedError("File extension %s not supported. (Must be in %r)" % (os.path.splitext(filename)[1], self.__extensions__))
        self._stack = pf.open(filename)
        
    def __write__(self,filename,clobber=False):
        """Write this FITS file to a file."""
        if not self.validate_filename(filename):
            raise NotImplementedError("File extension %s not supported. (Must be in %r)" % (os.path.splitext(filename)[1], self.__extensions__))
        self._stack.writeto(filename,clobber = clobber)
        
    def __setstack__(self,stack):
        """Sets this stack, given a series of frames."""
        assert isinstance(stack,collections.Sequence)
        assert len(stack) >= 0
        primary = stack.pop(0).hdu(primary=True)
        remainder = [ frame.hdu(primary=False) for frame in stack ]
        self._stack = pf.HDUList([primary] + remainder)
        
    def __getstack__(self):
        """Get the stack"""
        return self._stack
        
    stack = property(__getstack__,__setstack__)
    
FileFrame.register(pf.ImageHDU)
FileFrame.register(pf.PrimaryHDU)
        