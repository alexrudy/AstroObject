# 
#  AstroFITS.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-11-08.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.3.6
# 

# Parent Modules
import AstroObjectBase

# Standard Scipy Toolkits
import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt

# Matplolib Extras
import matplotlib.image as mpimage
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter

# Scipy Extras
from scipy import ndimage
from scipy.spatial.distance import cdist
from scipy.linalg import norm

# Standard Python Modules
import math, copy, sys, time, logging, os

# Submodules from this system
from Utilities import *

__version__ = getVersion()

LOG = logging.getLogger(__name__)

class HDUFrame(AstroObjectBase.FITSFrame,pf.ImageHDU):
    """
    A single frame of a FITS image.
    Frames are known as Header Data Units, or HDUs when written to a FITS file. This frame simply stores the HDU.
    This frame accepts (generally) 2-dimensional numpy arrays (``ndarray``), and will show those arrays as images. Currently, the system makes no attempt to ensure/check the data type of your data arrays. As such, data saved will often be saved as ``np.float`` rather than more compact data types such as ``np.int16``. Pyfits handles the typing of your data automatically, so saving an array with the correct type will generate the proper FITS file.
    This object requires *array*, the data, a *label*, and can optionally take *headers* and *metadata*.
    
    """
    def __init__(self, data=None, label=None, header=None, metadata=None, **kwargs):
        self.data = data
        super(HDUFrame, self).__init__(data=None, label=label, header=header, metadata=metadata, **kwargs)
        if not isinstance(self.header,pf.Header):
            self.header = pf.PrimaryHDU().header
        self.data = data
        try:
            self.__valid__()
        except AssertionError as e:
            raise AttributeError(str(e))
        
    
    def __call__(self):
        """Returns the data for this frame, which should be a ``numpy.ndarray``."""
        return self.data
        
    def __valid__(self):
        """Runs a series of assertions which ensure that the data for this frame is valid"""
        assert (isinstance(self.data,np.ndarray) or self.data==None), "Frame data is not correct type: %s" % type(self.data)
        
    
    def __hdu__(self,primary=False):
        """Retruns an HDU which represents this frame. HDUs are either ``pyfits.PrimaryHDU`` or ``pyfits.ImageHDU`` depending on the *primary* keyword."""
        if primary and isinstance(self,pf.ImageHDU):
            LOG.info("Generating a primary HDU for %s" % self)
            return pf.PrimaryHDU(self.data,self.header)
        elif (not primary) and isinstance(self,pf.PrimaryHDU):
            LOG.info("Generating an image HDU for %s" % self)
            return pf.ImageHDU(self.data,self.header)
        elif primary and isinstance(self,pf.PrimaryHDU):
            LOG.info("Returning a primary HDU for %s" % self)
            return pf.PrimaryHDU(self.data,self.header)
        elif (not primary) and isinstance(self,pf.ImageHDU):
            LOG.info("Returning an image HDU for %s" % self)
            return pf.ImageHDU(self.data,self.header)
            
    def __show__(self):
        """Plots the image in this frame using matplotlib's ``imshow`` function. The color map is set to an inverted binary, as is often useful when looking at astronomical images. The figure object is returned, and can be manipulated further.
        
        .. Note::
            This function serves as a quick view of the current state of the frame. It is not intended for robust plotting support, as that can be easily accomplished using ``matplotlib``. Rather, it attempts to do the minimum possible to create an acceptable image for immediate inspection.
        """
        LOG.debug("Plotting %s using matplotlib.pyplot.imshow" % self)
        figure = plt.imshow(self())
        figure.set_cmap('binary_r')
        return figure
    
    @classmethod
    def __save__(cls,data,label):
        """Attempts to create a :class:`ImageFrame` object from the provided data. This requres some type checking to ensure that the provided data meets the general sense of such an image. If the data does not appear to be correct, this method will raise an :exc:`NotImplementedError` with a message describing why the data did not validate. Generally, this error will be intercepted by the caller, and simply provides an indication that this is not the right class for a particular piece of data.
        
        If the data is saved successfully, this method will return an object of type :class:`ImageFrame`
        
        The validation requires that the data be a type ``numpy.ndarray`` and that the data have 2 and only 2 dimensions.
        """
        LOG.debug("Attempting to save as %s" % cls)
        if not isinstance(data,np.ndarray):
            msg = "ImageFrame cannot handle objects of type %s, must be type %s" % (type(data),np.ndarray)
            raise NotImplementedError(msg)
        try:
            Object = cls(data=data,label=label)
        except AssertionError as AE:
            msg = "%s data did not validate: %s" % (cls.__name__,AE)
            raise NotImplementedError(msg)
        LOG.debug("Saved %s" % (Object))
        return Object
    
    @classmethod
    def __read__(cls,HDU,label):
        """Attempts to convert a given HDU into an object of type :class:`ImageFrame`. This method is similar to the :meth:`__save__` method, but instead of taking data as input, it takes a full HDU. The use of a full HDU allows this method to check for the correct type of HDU, and to gather header information from the HDU. When reading data from a FITS file, this is the prefered method to initialize a new frame.
        """
        LOG.debug("Attempting to read as %s" % cls)
        if not isinstance(HDU,(pf.ImageHDU,pf.PrimaryHDU)):
            msg = "Must save a PrimaryHDU or ImageHDU to a %s, found %s" % (cls.__name__,type(HDU))
            raise NotImplementedError(msg)
        if not (isinstance(HDU.data,np.ndarray) or HDU.data==None):
            msg = "HDU Data must be %s for %s, found data of %s" % (np.ndarray,cls.__name__,type(HDU.data))
            raise NotImplementedError(msg)
        try:
            # Swizzle:
            HDU.__class__ = HDUFrame
            HDU.label = label
            Object = HDU
            # Object = cls(data=HDU.data,label=label,header=HDU.header)
        except AssertionError as AE:
            msg = "%s data did not validate: %s" % (cls.__name__,AE)
            raise NotImplementedError(msg)
        LOG.debug("Created %s" % Object)
        return Object
    


class HDUObject(AstroObjectBase.FITSObject):
    """This object tracks a number of HDU frames. This class is a simple subclass of :class:`AstroObjectBase.FITSObject` and usese all of the special methods implemented in that base class. This object sets up an image object class which has two special features. It uses only the :class:`HDUFrame` class for data.
    """
    def __init__(self, filename=None):
        super(HDUObject, self).__init__()
        self.dataClasses += [HDUFrame]
        self.dataClasses.remove(AstroObjectBase.FITSFrame)
        if filename != None:
            self.read(filename)        # Save the initializing data
            
