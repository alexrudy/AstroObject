# -*- coding: utf-8 -*-
# 
#  npy.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-05-08.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 
u"""
:class:`file.npy.NumpyFile` — An abstraction layer for :mod:`numpy` files
=========================================================================

This module handles the writing and reading of ``.npy`` and ``.npz`` files. ``.npy`` files are single-array files, where each file will contain only one frame. ``.npz`` files are multiple-frame files. Neither format contains any metadata about the image.

.. autoclass::
    NumpyFile
    :members:
    :inherited-members:

:class:`file.numpy.NumpyZipFile` – An abstraction for compressed :mod:`numpy` files
===================================================================================

.. autoclass::
    NumpyZipFile
    :members:
    :inherited-members:
    

"""

import os
import collections

import numpy as np
import pyfits as pf

from . import File

class NumpyFile(File):
    """Simple numpy binary file writing using the :mod:`numpy` file facilities. Saves the raw data component to a binary :mod:`numpy` file.
    
    =========== =======
     extension   notes
    =========== =======
    ``.npy``
    =========== =======
    
    .. note:: Since :mod:`numpy` files only contain the raw HDU data, any information stored in FITS headers or otherwise held as object metadata will not be saved.
    """
    def __init__(self, filename=None):
        super(NumpyFile, self).__init__()
        self.validate(filename)
        self.file = filename
        
    __extensions__ = [ '.npy' ]
    __canstream__ = True
    
    def write(self,stack,clobber=False):
        """Write a stack to this file.
        
        :param HDUList stack: An HDUList to write to a file.
        :param bool clobber: Whether to overwrite the destination file.
        
        """
        if len(stack) > 1:
            raise TypeError(u"Can't save multiple frames to stack.")
        if not clobber and os.path.exists(self.filename):
            raise IOError(u"Can't overwrite existing file.")
        np.save(self.file, stack[0].data)
        
    def open(self):
        """Open this file and return the HDUList."""
        return pf.HDUList([pf.PrimaryHDU(np.load(self.file))])

class NumpyZipFile(File):
    """Simple numpy binary file writing using the :mod:`numpy` file facilities. Saves the raw data component to a binary :mod:`numpy` file.
    
    =========== =======
     extension   notes
    =========== =======
    ``.npz``
    =========== =======
    
    .. note:: Since :mod:`numpy` files only contain the raw HDU data, any information stored in FITS headers or otherwise held as object metadata will not be saved.
    """
    def __init__(self, filename=None):
        super(NumpyZipFile, self).__init__()
        self.validate(filename)
        self.filename = filename
     
    __extensions__ = [ '.npz' ]
    
    def write(self,stack,clobber=False):
        """Write a stack to this file.
        
        :param HDUList stack: An HDUList to write to a file.
        :param bool clobber: Whether to overwrite the destination file.
        
        """
        dirname, filename = os.path.split(self.filename)
        basename, extension = os.path.splitext(filename)
        
        if not clobber and os.path.exists(self.filename):
            raise IOError(u"Can't overwrite existing file.")
        np.savez(self.filename,**{ frame.header.get('label',"%s-%02d" % (basename, fnum)): frame.data for fnum,frame in enumerate(stack) })

        
        
    def open(self):
        """Open this file and return the HDUList."""
        dirname, filename = os.path.split(self.filename)
        basename, extension = os.path.splitext(filename)
        zipfile = np.load(self.filename)
        HDUList = pf.HDUList()
        for fnum,label in enumerate(zipfile):
            HDU = pf.ImageHDU(zipfile[label])
            if label != "%s-%02d" % (basename, fnum):
                HDU.header.update('label',label)
            HDUList.append(HDU)
        return HDUList
