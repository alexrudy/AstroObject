# -*- coding: utf-8 -*-
# 
#  fits.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-05-08.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 
"""
:class:`file.fits.FITSFile` - An abstraction layer for FITS Files
=================================================================

This module provides a simple extraction layer class for FITS file writing. FITS files must have either the ``.fit`` or ``.fits`` extension to be detected by this module. The module reads and writes files using :mod:`pyfits`.

.. autoclass::
    FITSFile
    :members:
    :inherited-members:

"""


import os
import pyfits as pf
import collections
import warnings

from . import File

class FITSFile(File):
    """A fits file implementation which simply passes ``HDUs`` through to the :mod:`pyfits` API.
    
    :param string filename: The filename, which must end in ``.fit`` or ``.fits`` to be considered valid.
    
    =========== =======
     extension   notes
    =========== =======
    ``.fits``
    ``.fit``
    =========== =======
    
    
    """
    def __init__(self, thefile=None):
        super(FITSFile, self).__init__()
        self.validate(thefile)
        if isinstance(thefile,file):
            if not hasattr(thefile,'mode') or (not 'b' in thefile.mode):
                raise NotImplementedError("This file is not in binary mode!")
        self.file = thefile
             
    __extensions__ = ['.fit','.fits']
    __canstream__ = True
    
    def write(self, stack, clobber=False):
        """Write a stack to this file.
        
        :param HDUList stack: An HDUList to write to a file.
        :param bool clobber: Whether to overwrite the destination file.
        
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            stack.writeto(self.file, clobber = clobber)
        
    def open(self):
        """Open this file and return the HDUList."""
        return pf.open(self.file,ignore_missing_end=True)
        