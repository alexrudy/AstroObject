# -*- coding: utf-8 -*-
# 
#  AstroNDArray.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-04-18.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.5-b2
# 
u"""
:mod:`AstroNDArray` – Numpy Array Frames
========================================

This module implements a **frame** as a subclass of NDArray. This eliminates the difference between the :attr:`~AstroOBject.AstroObjectBase.BaseStack.d` attribute and the :attr:`~AstroOBject.AstroObjectBase.BaseStack.f`.

.. inheritance-diagram::
    AstroObject.AstroNDArray.NDArrayStack
    AstroObject.AstroNDArray.NDArrayFrame
    :parts: 1

:class:`NDArrayStack` – Numpy Array **Stacks**
----------------------------------------------

.. autoclass::
    AstroObject.AstroNDArray.NDArrayStack
    :members:
    :inherited-members:


:class:`NDArrayFrame` – Numpy Array **Frames**
----------------------------------------------

.. autoclass::
    AstroObject.AstroNDArray.NDArrayFrame
    :members:
    :special-members:

"""

# Standard Scipy Toolkits
import numpy as np
import pyfits as pf
import scipy as sp

# Standard Python Modules
import math, logging, os, time
import copy
import collections

from AstroObjectBase import BaseFrame,BaseStack,HDUHeaderMixin

# Submodules from this system
from Utilities import *

__all__ = ["BaseStack","BaseFrame","AnalyticMixin","NoHDUMixin","HDUHeaderMixin","NoDataMixin"]

__version__ = getVersion()

LOG = logging.getLogger(__name__)

class NDArrayFrame(HDUHeaderMixin,BaseFrame,np.ndarray):
    """A frame based on np.ndarray"""
    def __init__(self,*args, **kwargs):
        super(NDArrayFrame, self).__init__(*args, **kwargs)
        
    def __new__(cls, data, label=None, header=None, metadata=None):
        obj = np.asarray(data).view(cls)
        if isinstance(header,collections.Mapping):
            obj.header = pf.core.Header()
            for key,value in header.iteritems():
                obj.header.update(key,value)
        elif isinstance(header,pf.core.Header):
            obj.header = header
        else:
            assert header == None, "%s doesn't understand the header, %s, type %s" % (self,header,type(header))
        if isinstance(metadata,collections.Mapping):
            obj.metadata = metadata
        else:
            obj.metadata = {}
        if not hasattr(obj,'time'):
            obj.time = time.clock()
            LOG.log(2,"Saving NDArrayFrame at time %r" % obj.time)
        obj.__setlabel__(label)
        try:
            obj.__valid__()
        except AssertionError as e:
            raise AttributeError(str(e))
        LOG.log(2,"Created NDArrayFrame labeled %r" % obj.label)
        return obj
    
    def __array_finalize__(self,obj):
        """Finalize this array's initialization"""
        if obj is not None:
            self.header = getattr(obj,'header',pf.core.Header())
            self.metadata = getattr(obj,'metadata',{})
            self._label = getattr(obj,'label',None)
            self.time = getattr(obj,'time',None)
        if not hasattr(self,'time') or self.time is None:
            self.time = time.clock()
            LOG.log(2,"Setting NDArrayFrame at time %r" % self.time)
        if isinstance(self.header,pf.core.Header):
            #Nothing to do when we are already with the correct header type.
            pass
        elif isinstance(self.header,collections.Mapping):
            _header = self.header
            self.header = pf.core.Header()
            for key,value in _header.iteritems():
                self.header.update(key,value)
        elif not isinstance(self.header,pf.core.Header):
            assert self.header == None, "%s doesn't understand the header, %s, type %s" % (self,self.header,type(self.header))
        try:
            self.__valid__()
        except AssertionError as e:
            raise AttributeError(str(e))
        LOG.log(2,"Initialized NDArrayFrame labeled %r" % self.label)
        
    def __setlabel__(self,label):
        """One use function to set the label"""
        if label == None:
            return
        if getattr(self,'label',None) == None:
            self._label = label
        elif getattr(self,'label',None) == label:
            return
        else:
            raise NotImplementedError("Cannot change label twice! %s -> %s" % (found_label,label))
            
    def __call__(self):
        """Simply returns this data item."""
        return self
        
    def __str__(self):
        """String representation of this object."""
        return BaseFrame.__str__(self)
        
    def __valid__(self):
        """Check this item for validity"""
        assert self.size > 0, "Must be an array with elements in it!"
        assert self.ndim > 0, "Array must have non-zero dimensions."
        super(NDArrayFrame, self).__valid__()
        
    def __hdu__(self,primary=False):
        """Returns an HDU for this object"""
        if primary:
            return pf.PrimaryHDU(self.view(np.ndarray))
        else:
            return pf.ImageHDU(self.view(np.ndarray))
            
    def __show__(self):
        """Plots the image in this frame using matplotlib's ``imshow`` function. The color map is set to an inverted binary, as is often useful when looking at astronomical images. The figure object is returned, and can be manipulated further.
        
        .. Note::
            This function serves as a quick view of the current state of the frame. It is not intended for robust plotting support, as that can be easily accomplished using ``matplotlib``. Rather, it attempts to do the minimum possible to create an acceptable image for immediate inspection.
        """
        LOG.log(2,"Plotting %s using matplotlib.pyplot.imshow" % self)
        import matplotlib as mpl
        import matplotlib.pyplot as plt
        figure = plt.imshow(self())
        figure.set_cmap('binary_r')
        return figure
    
    @classmethod
    def __save__(cls,data,label):
        """Save some data to this class"""
        LOG.log(2,"Attempting to save as %s" % cls)
        if not isinstance(data,np.ndarray):
            msg = "NDArrayFrame cannot handle objects of type %s, must be type %s" % (type(data),np.ndarray)
            raise NotImplementedError(msg)
        try:
            Object = cls.__new__(cls,data,label)
        except AttributeError as AE:
            msg = "%s data did not validate: %s" % (cls.__name__,AE)
            raise NotImplementedError(msg)
        LOG.log(2,"Created %s" % Object)
        return Object
        
    @classmethod
    def __read__(cls,HDU,label):
        """Read some data for this class from a HDU"""
        LOG.log(2,"Attempting to read as %s" % cls)
        if not isinstance(HDU,(pf.ImageHDU,pf.PrimaryHDU)):
            msg = "Must save a PrimaryHDU or ImageHDU to a %s, found %s" % (cls.__name__,type(HDU))
            raise NotImplementedError(msg)
        try:
            Object = cls(HDU.data,label)
        except AttributeError as AE:
            msg = "%s data did not validate: %s" % (cls.__name__,AE)
            raise NotImplementedError(msg)
        LOG.log(2,"Created %s" % Object)
        return Object

class NDArrayStack(BaseStack):
    """This object tracks a number of data frames. This class is a simple subclass of :class:`AstroObjectBase.BaseStack` and usese all of the special methods implemented in that base class. This object sets up an image object class which has two special features. First, it uses only the :class:`NDArrayFrame` class for data. As well, it accepts an array in the initializer that will be saved immediately.
    """
    def __init__(self,dataClasses=[NDArrayFrame],**kwargs):
        super(NDArrayStack, self).__init__(dataClasses=dataClasses,**kwargs)
