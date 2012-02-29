# 
#  AstroSpectra.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.3.0a2
# 


import AstroObjectBase, AstroImage

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

__all__ = ["SpectraFrame","SpectraObject"]

__version__ = getVersion()

LOG = logging.getLogger(__name__)

class SpectraFrame(AstroObjectBase.FITSFrame):
    """A single frame of a spectrum. This will save the spectrum as an image, with the first row having flux, and second row having the wavelength equivalent. Further rows can accomodate further spectral frames when stored to a FITS image. However, the frame only accepts a single spectrum."""
    def __init__(self, data=None, label=None, header=None, metadata=None, **kwargs):
        self.data = data # The image data
        self.size = data.size # The size of this image
        self.shape = data.shape # The shape of this image
        super(SpectraFrame, self).__init__(label=label, header=header, metadata=metadata, **kwargs)
        
    
    def __valid__(self):
        """Validates this spectrum frame to conform to the required data shape. This function is used to determine if a passed numpy data array appears to be a spectrum. It is essentially a helper function."""
        dimensions = 2
        rows = 2
        assert self.size == self.data.size, "Members of %s appear to be inconsistent!" % self
        assert self.shape == self.data.shape, "Members of %s appear to be inconsistent!" % self
        assert self.data.ndim == dimensions , "Data of %s does not appear to be %d-dimensional! Shape: %s" % (self,dimensions,self.shape)
        assert self.shape[0] == rows, "Spectrum for %s appears to be multi-dimensional, expected %d Shape: %s" % (self,rows,self.shape)        
        return True
            
    
    def __call__(self):
        """Returns the data for this frame, which should be a ``numpy.ndarray``. The first row will be the spectral data, the second row the equivalent wavelength for this spectrum."""
        return self.data
        
    
    def __hdu__(self,primary=False):
        """Retruns an HDU which represents this frame. HDUs are either ``pyfits.PrimaryHDU`` or ``pyfits.ImageHDU`` depending on the *primary* keyword."""
        if primary:
            LOG.log(5,"Generating a primary HDU for %s" % self)
            HDU = pf.PrimaryHDU(self.data)
        else:
            LOG.log(5,"Generating an image HDU for %s" % self)
            HDU = pf.ImageHDU(self.data)
        HDU.header.update('label',self.label)
        HDU.header.update('object',self.label)
        for key,value in self.header.iteritems():
            HDU.header.update(key,value)
        return HDU
        
    
    def __show__(self):
        """Plots the image in this frame using matplotlib's ``imshow`` function. The color map is set to an inverted binary, as is often useful when looking at astronomical images. The figure object is returned, and can be manipulated further.
        
        .. Note::
            This function serves as a quick view of the current state of the frame. It is not intended for robust plotting support, as that can be easily accomplished using ``matplotlib``. Rather, it attempts to do the minimum possible to create an acceptable image for immediate inspection."""
        LOG.log(2,"Plotting %s using matplotlib.pyplot.plot" % self)
        x,y = self.data #Slice Data
        plt.plot(x,y,label=self.label)
        plt.axis(expandLim(plt.axis()))
        plt.gca().ticklabel_format(style="sci",scilimits=(3,3))
        return plt.gca()
    
    
    @classmethod
    def __save__(cls,data,label):
        """Attempts to create a :class:`ImageFrame` object from the provided data. This requres some type checking to ensure that the provided data meets the general sense of such an image. If the data does not appear to be correct, this method will raise an :exc:`AbstractError` with a message describing why the data did not validate. Generally, this error will be intercepted by the caller, and simply provides an indication that this is not the right class for a particular piece of data.
        
        If the data is saved successfully, this method will return an object of type :class:`ImageFrame`
        
        The validation requires that the data be a type ``numpy.ndarray`` and that the data have 2 and only 2 dimensions. As well, the data should pass the :meth:`validate` method."""
        LOG.log(2,"Attempting to save as %s" % cls)
        dimensions = 2
        if not isinstance(data,np.ndarray):
            msg = "%s cannot handle objects of type %s, must be type %s" % (cls.__name__,type(data),np.ndarray)
            raise AbstractError(msg)
        if data.ndim != dimensions:
            LOG.warning("The data appears to be %d dimensional. This object expects %d dimensional data." % (len(data.shape),dimensions))
        try:
            Object = cls(data,label)
        except AssertionError as AE:
            msg = "%s data did not validate: %s" % (cls.__name__,AE)
            raise AbstractError(msg)
        LOG.log(2,"Saved %s with size %d" % (Object,Object.size))
        return Object
    
    @classmethod
    def __read__(cls,HDU,label):
        """Attempts to convert a given HDU into an object of type :class:`ImageFrame`. This method is similar to the :meth:`__save__` method, but instead of taking data as input, it takes a full HDU. The use of a full HDU allows this method to check for the correct type of HDU, and to gather header information from the HDU. When reading data from a FITS file, this is the prefered method to initialize a new frame."""
        LOG.log(2,"Attempting to read as %s" % cls)
        if not isinstance(HDU,(pf.ImageHDU,pf.PrimaryHDU)):
            msg = "Must save a PrimaryHDU or ImageHDU to a %s, found %s" % (cls.__name__,type(HDU))
            raise AbstractError(msg)
        if not isinstance(HDU.data,np.ndarray):
            msg = "HDU Data must be %s for %s, found data of %s" % (np.ndarray,cls.__name__,type(HDU.data))
            raise AbstractError(msg)    
        try:
            Object = cls(HDU.data,label)        
        except AssertionError as AE:
            msg = "%s data did not validate: %s" % (cls.__name__,AE)
            raise AbstractError(msg)
        LOG.log(2,"Read %s with size %s" % (Object,Object.size))
        return Object
    

    


class SpectraObject(AstroObjectBase.FITSObject):
    """This object tracks a number of data frames. This class is a simple subclass of :class:`AstroObjectBase.FITSObject` and usese all of the special methods implemented in that base class. This object sets up an image object class which has two special features. First, it uses only the :class:`SpectraFrame` class for data. As well, it accepts an array in the initializer that will be saved immediately."""
    def __init__(self, **kwargs):
        super(SpectraObject, self).__init__(**kwargs)
        self.dataClasses += [SpectraFrame]
        self.dataClasses.remove(AstroObjectBase.FITSFrame)

        
        
        
        


            
