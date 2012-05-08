# -*- coding: utf-8 -*-
# 
#  npy.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-05-08.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 

import os
import collections

import numpy as np
import pyfits as pf

from . import File

class NumpyFile(File):
    """A fits file implementation"""
    def __init__(self, filename=None):
        super(NumpyFile, self).__init__()
        self.validate_filename(filename)
        self.filename = filename
     
    __extensions__ = ['.npy']
    
    def write(self,stack,clobber=False):
        """Write this FITS file to a file."""
        if len(stack) > 1:
            raise TypeError(u"Can't save multiple frames to stack.")
        if not clobber and os.path.exists(self.filename):
            raise IOError(u"Can't overwrite existing file.")
        np.save(self.filename, stack[0].data)
        
    def open(self):
        """Get the HDUList for this object."""
        return pf.HDUList([pf.PrimaryHDU(np.load(self.filename))])

