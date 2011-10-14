# 
#  AstroSpectra.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 


import AstroObject, AstroImage
from Utilities import *

import matplotlib.pyplot as plt
import matplotlib.image as mpimage
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
from scipy import ndimage
from scipy.spatial.distance import cdist
from scipy.linalg import norm
import numpy as np
import pyfits
import math, copy, sys, time, logging, os

LOG = logging.getLogger(__name__)

class SpectraFrame(AstroObject.FITSFrame):
    """A simple spectral frame"""
    def __init__(self, array, label, ordinate, header=None, metadata=None):
        super(SpectraFrame, self).__init__(label, header, metadata)
        self.data = array # The image data
        self.size = array.size # The size of this image
        self.shape = array.shape # The shape of this image
        self.ordinate = ordinate # Usually wavelength
    
    def validate(self):
        """Validates this spectrum object"""
        try:
            assert self.size == self.data.size
            assert self.shape == self.data.shape
        except AssertionError:
            raise AssertionError("Members of %s appear to be inconsistent!" % self)
        try:
            assert len(self.shape) == 1
            assert self.shape[0] == self.size
        except AssertionError:
            raise AssertionError("Data of %s does not appear to be 1-dimensional! Shape: %s" % (self,self.shape))
        try:
            assert len(self.ordinate.shape) == 1
            assert self.ordinate.shape[0] == self.ordinate.size
        except AssertionError:
            raise AssertionError("Ordinate of %s does not appear to be 1-dimensional! Shape: %s" % (self,self.ordinate.shape))
    
    def __call__(self):
        """Call this frame, returning the data array"""
        return np.array([self.ordinate,self.data])
        
    
    def __hdu__(self,primary=False):
        """Retruns an HDU for this frame"""
        if primary:
            LOG.info("Generating a primary HDU for %s" % self)
            return pyfits.PrimaryHDU(self())
        else:
            LOG.info("Generating an image HDU for %s" % self)
            return pyfits.ImageHDU(self())
        
    
    def __show__(self):
        """Returns the plot object for this image"""
        LOG.debug("Plotting %s using matplotlib.pyplot.plot" % self)
        x,y = self.data #Slice Data
        axis = get_padding((x,y))
        plt.plot(x,y,'k-')
        plt.axis(axis)
        plt.gca().ticklabel_format(style="sci",scilimits=(3,3))
        
    
    
    @classmethod
    def __save__(cls,data,label):
        """A generic class method for saving to this object with data directly"""
        LOG.debug("Attempting to save as %s" % cls)
        if not isinstance(data,np.ndarray):
            msg = "ImageFrame cannot handle objects of type %s, must be type %s" % (type(data),np.ndarray)
            LOG.debug(msg)
            raise AbstractError(msg)
        if len(data.shape) != 2:
            LOG.warning("The data appears to be %d dimensional. This object expects 2 dimensional data." % len(data.shape))
        Object = cls(data,label)
        LOG.debug("Saved %s with size %d" % (Object,data.size))
        return Object
    
    @classmethod
    def __read__(cls,HDU,label):
        """An abstract method for reading empty data HDU Frames"""
        LOG.debug("Attempting to read as %s" % cls)
        if not isinstance(HDU,(pyfits.ImageHDU,pyfits.PrimaryHDU)):
            msg = "Must save a PrimaryHDU or ImageHDU to a %s, found %s" % (cls.__name__,type(HDU))
            LOG.debug(msg)
            raise AbstractError(msg)
        if not isinstance(HDU.data,np.ndarray):
            msg = "HDU Data must be %s for %s, found data of %s" % (np.ndarray,cls.__name__,type(HDU.data))
            LOG.debug(msg)
            raise AbstractError(msg)
        Object = cls(HDU.data,label)
        LOG.debug("Created %s" % Object)
        return Object
    

    


class SpectraObject(AstroImage.ImageObject):
    """A subclass of FITS image with specific facilites for displaying spectra"""
    def __init__(self, array=None):
        super(ImageObject, self).__init__()
        self.dataClasses += [SpectrumFrame]
        self.dataClasses.remove(AstroObject.FITSFrame)
        LOG.debug("Initialized %s, data classes %s" % (self,self.dataClasses))
        if array != None:
            self.save(array)        # Save the initializing data
        
        
        
    def showSpectrum(self):
        """Shows a 2-D plot of a spectrum"""
        x,y = self.data() #Slice Data
        axis = get_padding((x,y))
        plt.plot(x,y,'k-')
        plt.axis(axis)
        plt.gca().ticklabel_format(style="sci",scilimits=(3,3))
        


            