# -*- coding: utf-8 -*-
# 
#  AstroFITS.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-04-17.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.5-b1
# 
"""
:mod:`AstroFITS` – Empty FITS HDUs
==================================

The :class:`FITSStack` **stack** handles *empty* FITS Header-Data-Units (or HDUs). As such, it can only contain HDUs that do not have data, and should only be used when you need to write a FITS file that has only header information and no actual data. The module does serve as a good demonstration of the use and implementation of the :ref:`AstroObjectAPI`.


.. inheritance-diagram::
    AstroObject.AstroFITS.FITSStack
    AstroObject.AstroFITS.FITSFrame
    :parts: 1


:class:`FITSStack` — Empty HDU **stacks**
------------------------------------------

.. autoclass::
    AstroObject.AstroFITS.FITSStack
    :members:
    :inherited-members:
    :show-inheritance:
    

:class:`FITSFrame` — Empty HDU **frames**
-----------------------------------------

Our first example frame is the :class:`FITSFrame`. This class is a data frame which can only contain empty HDUs. As such, it does not implement all of the methods of the API, and instead uses the :class:`NoDataMixin` class.

.. autoclass:: 
    AstroObject.AstroFITS.FITSFrame
    :members:
    :inherited-members:
    :show-inheritance:
    
    .. automethod:: __call__
    
    .. automethod:: __repr__    
    
    .. automethod:: __valid__
    
    .. automethod:: __hdu__
    
    .. automethod:: __show__
    
    .. automethod:: __save__
    
    .. automethod:: __read__
"""
# Standard Scipy Toolkits
import numpy as np
import pyfits as pf
import scipy as sp

# Standard Python Modules
import math, logging, os, time
import copy
import collections

from AstroObjectBase import BaseFrame,BaseStack,HDUHeaderMixin,NoDataMixin

# Submodules from this system
from Utilities import *

__all__ = ["FITSFrame","FITSStack"]

__version__ = getVersion()

LOG = logging.getLogger(__name__)



class FITSFrame(HDUHeaderMixin,NoDataMixin,BaseFrame):
    """A single frame of a FITS image. This Frame **may not** contain any data. It can only be used to hold and manipulate empty HDUs.
    Frames are known as Header Data Units, or HDUs when written to a FITS file.
    
    :param None data: The data to be saved.
    :param string label: A string name for this frame
    :param header: pyfits.header or dictionary of header options
    :param metadata: dictionary of arbitrary metadata
    
    """
    def __init__(self, data=None, label=None, header=None, metadata=None, **kwargs):
        super(FITSFrame, self).__init__(data=data, label=label, header=header, metadata=metadata,**kwargs)
    
    def __hdu__(self,primary=False):
        """Retruns a Header-Data Unit PyFits object. The abstract case generates empty HDUs, which contain no data.
        
        :param bool primary: Return a primary HDU
        :returns: pyfits.primaryHDU or pyfits.ImageHDU
        """
        if primary:
            HDU = pf.PrimaryHDU()
        else:
            HDU = pf.ImageHDU()
        LOG.log(8,"%s: Generating an Empty %sHDU" % (self,"primary " if primary else ""))
        return HDU
    
    @classmethod
    def __read__(cls,HDU,label):
        """An abstract method for reading empty data HDU Frames.
        
        :param data: HDU to be saved, as a ``pyfits.HDU``.
        :param label: Name for the newly created frame.
        :raises: :exc:`NotImplementedError` when this data can't be saved.
        :returns: :class:`FITSFrame`
        """
        if not isinstance(HDU,(pf.PrimaryHDU,pf.ImageHDU)):
            msg = "Must save a %s to a %s, found %s" % (pf.PrimaryHDU.__name__,cls.__name__,HDU.__class__.__name__)
            raise NotImplementedError(msg)
        if not HDU.data == None:
            msg = "HDU Data must be type %s for %s, found data of type %s" % (None,cls,type(HDU.data).__name__)
            raise NotImplementedError(msg)
        Object = cls(None,label)
        LOG.log(2,"%s: Created %s" % (cls,Object))
        return Object

class FITSStack(BaseStack):
    """This **stack** tracks a number of data frames. This class is a simple subclass of :class:`AstroObjectBase.BaseStack` and usese all of the special methods implemented in that base class. This object sets up an **stack** class which uses only the :class:`FITSFrame` class for data. As such, it can only contain objects which are classes (or subclassses of) :class:`FITSFrame`.
    """
    def __init__(self,dataClasses=[FITSFrame],**kwargs):
        super(FITSStack, self).__init__(dataClasses=dataClasses,**kwargs)
