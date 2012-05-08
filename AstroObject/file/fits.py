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

from . import File

class FITSFile(File):
    """A fits file implementation"""
    def __init__(self, filename=None):
        super(FITSFile, self).__init__()
        self.filename = filename
        self.validate_filename(filename)
     
    __extensions__ = ['.fit','.fits']
    
    def write(self,stack,clobber=False):
        """Write this FITS file to a file."""
        stack.writeto(self.filename,clobber = clobber)
        
    def open(self):
        """Get the HDUList for this object."""
        return pf.open(self.filename)
        