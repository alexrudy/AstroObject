# -*- coding: utf-8 -*-
# 
#  plaintext.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-05-08.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 
u"""
:class:`file.plaintext.NumpyTextFile` – Plain Text File writing
===============================================================

This module handles writing simple text files. In :mod:`AstroObject`, simple text files have the extension ``.txt`` or ``.dat``. As well, since this module uses numpy to load and read text files, gzipped files can be read automatically as gzipped text files, with the ``.gz`` extension.

.. autoclass::
    NumpyTextFile
    :members:
    :inherited-members:

:class:`file.plaintext.AstroObjectTextFile` – Plain Text files with Headers
===========================================================================

This module writes plain-text files, but includes header information as text comments at the beginning.

.. autoclass::
    AstroObjectTextFile
    :members:
    :inherited-members:

"""
import os
import collections

import numpy as np
import pyfits as pf

from . import File

class NumpyTextFile(File):
    """Simple text file writing using the :mod:`numpy` text facilities. Text files write the raw data of the data component to the HDU to a simple text file.
    
    =========== =======
     extension   notes
    =========== =======
    ``.txt``
    ``.dat``
    ``.gz``      Compressed text files.
    =========== =======
    
    
    .. note:: Since text files only contain the raw HDU data, any information stored in FITS headers or otherwise held as object metadata will not be saved."""
    def __init__(self, filename=None):
        super(NumpyTextFile, self).__init__()
        self.validate_filename(filename)
        self.filename = filename

     
    __extensions__ = ['.txt','.dat','.gz']
    
    def write(self,stack,clobber=False):
        """Write a stack to this file. The stack cannot have more than one HDU element. The text file will be a text representation of the HDU's data array, and will not contain any metadata information.
        
        :param HDUList stack: An HDUList to write to a file.
        :param bool clobber: Whether to overwrite the destination file.
        
        """
        if len(stack) > 1:
            raise TypeError(u"Can't save multiple frames to stack.")
        if not clobber and os.path.exists(self.filename):
            raise IOError(u"Can't overwrite existing file.")
        np.savetxt(self.filename, stack[0].data)
        
    def open(self):
        """Open this file and return the HDUList."""
        return pf.HDUList([pf.PrimaryHDU(np.loadtxt(self.filename))])

class AstroObjectTextFile(File):
    """Simple text file writing using the :mod:`numpy` text facilities. Text files write the raw data of the data component to the HDU to a simple text file.
    
    =========== =======
     extension   notes
    =========== =======
    ``.aotxt``
    ``.aodat``
    =========== =======
    """
    def __init__(self, filename=None):
        super(AstroObjectTextFile, self).__init__()
        self.validate_filename(filename)
        self.filename = filename
    
    __extensions__ = [ ".aotxt", ".aodat" ]
    
    def write(self,stack,clobber=False):
        """Write a stack to this file. The stack cannot have more than one HDU element. The text file will be a text representation of the HDU's data array, and will not contain any metadata information.
        
        :param HDUList stack: An HDUList to write to a file.
        :param bool clobber: Whether to overwrite the destination file.
        
        """
        if len(stack) > 1:
            raise TypeError(u"Can't save multiple frames to stack.")
        if not clobber and os.path.exists(self.filename):
            raise IOError(u"Can't overwrite existing file.")
        header = "# " + "\n# ".join([str(card) for card in stack[0].header.ascardlist()]) + "\n# \n"
        with open(self.filename,'w') as stream:
            stream.write(header)
            np.savetxt(stream, stack[0].data)
        
    def open(self):
        """Open this file and return the HDUList."""
        return pf.HDUList([pf.PrimaryHDU(np.loadtxt(self.filename))])

        