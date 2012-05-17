# -*- coding: utf-8 -*-
# 
#  __init__.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-05-08.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 
"""
:mod:`file` - File IO
=====================

This module provides the support in AstroObject for arbitrary file format input and output. File-type objects are created which validate a filename internally, then read (open) or write files of varying formats. In their most basic forms, file-type objects should validate the viability of a file when they are initialized (check that the path exists, and that the filename has the proper extension), raising an :exc:`NotImplementedError` if some feature of this file will not be able to be saved. File objects must also have a :meth:`write` and :meth:`open` to write to files.


.. autoclass::
    File
    :members:
    
    
.. automodule::
    AstroObject.file.fits
    
.. automodule::
    AstroObject.file.plaintext
    
.. automodule::
    AstroObject.file.npy
    
.. automodule::
    AstroObject.file.fileset

"""

import os
from abc import ABCMeta, abstractmethod, abstractproperty

class File(object):
    """A generic file object meant to facilitate writing and reading HDULists from a particular type of file. This abstract base class should be used as a template for other file writing objects."""
    
    __metaclass__ = ABCMeta
    
    __extensions__ = []
    """Extensions which can be used for this file type."""
    
    @abstractmethod
    def write(self, stack, clobber=False):
        """Write this file using the HDUList provided.
        
        :param HDUList stack: A pyfits HDU list which should be written to a file.
        :param bool clobber: Whether to overwrite the file on output
        
        """
        raise NotImplementedError
        
    @abstractmethod
    def open(self):
        """Open this file and return an HDUList."""
        raise NotImplementedError
    
    def validate_filename(self, filename):
        """Raise an :exc:`NotImplementedError` if the filename is not acceptalbe to this file type. Else return true.
        
        :param string filename: The filename to check.
        :raises: :exc:`NotImplementedError` when the filename is not valid for this filetype.
        :returns: True for valid extensions.
        :var __extensions__: The internal array of acceptable extensions.
        
        """
        filename, extension = os.path.splitext(filename)
        if extension.lower() not in self.__extensions__:
            msg = "Filename '%s' does not have a valid extension. (Use %r)" % (filename, self.__extensions__)
            raise NotImplementedError(msg)
        return True
        
from .fits import FITSFile
from .npy import NumpyFile, NumpyZipFile
from .plaintext import NumpyTextFile, AstroObjectTextFile

DefaultFileClasses = [ FITSFile, NumpyFile, NumpyZipFile, NumpyTextFile, AstroObjectTextFile ]
        