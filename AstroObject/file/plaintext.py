# -*- coding: utf-8 -*-
# 
#  plaintext.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-05-08.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 

import numpy as np
import os
import collections

from . import File, SimpleFrame

class PlainText(File):
    """docstring for PlainText"""
    def __init__(self, filename=None, npgenkwds=None, npsavekwds=None):
        super(PlainText, self).__init__()
        
        if isinstance(npgenkwds,collections.Mapping):
            self.npgenkwds = npgenkwds
        else:
            self.npgenkwds = {
                'comments' : '#'
            }
        if isinstance(npsavekwds,collections.Mapping):
            self.npsavekwds = npsavekwds
        else:
            self.npsavekwds = {}
        
        self._stack = []
        self.label = None
        if filename is not None:
            self.__read__(filename)
     
    __extensions__ = ['.txt','.dat','.gz']    
        
    def __read__(self, filename, framename = None):
        """Read the named file."""
        if not self.validate_filename(filename):
            raise NotImplementedError("File extension %s not supported. (Must be in %r)" % (os.path.splitext(filename)[1], self.__extensions__))
        if framename is not None:
            self.label = framename
        if self.label is None:
            self.label = os.path.splitext(os.path.split(filename)[1])[0]
        self._stack = [ SimpleFrame(data = np.loadtxt(filename,**self.npgenkwds), label = self.label)]

        
    def __write__(self, filename, clobber = False):
        """Save the named file."""
        if not self.validate_filename(filename):
            raise NotImplementedError("File extension %s not supported. (Must be in %r)" % (os.path.splitext(filename)[1], self.__extensions__))
        if os.path.exists(filename) and not clobber:
            raise IOError("Can not overwrite file %s" % filename)
        if len(self._stack) == 1:
            np.savetxt( filename, self._stack[0].data )
    
    def __setstack__(self,stack):
        """Set the stack for this object."""
        assert isinstance(stack,collections.Sequence)
        assert len(stack) >= 0 and len(stack) <= 1
        try:
            self._stack = [ SimpleFrame(data = frame.hdu(primary=True).data, label = self.label) for frame in stack]
        except Exception as AE:
            raise NotImplementedError("Problem creating frames: %s" % AE)
        
        
    def __getstack__(self):
        """Return the stack for this object"""
        return self._stack
        
    stack = property(__getstack__,__setstack__)
            