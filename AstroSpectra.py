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
    def __init__(self, array, label, header=None, metadata=None):
        super(SpectraFrame, self).__init__(label, header, metadata)
        self.data = array # The image data
        self.size = array.size # The size of this image
        self.shape = array.shape # The shape of this image
    
    def validate(self):
        """Validates this spectrum object"""
        dimensions = 2
        rows = 2
        try:
            assert self.size == self.data.size
            assert self.shape == self.data.shape
        except AssertionError:
            raise AssertionError("Members of %s appear to be inconsistent!" % self)
        try:
            assert self.data.ndim == dimensions
        except AssertionError:
            raise AssertionError("Data of %s does not appear to be %d-dimensional! Shape: %s" % (self,dimensions,self.shape))
        try:
            assert self.shape[0] == rows
        except AssertionError:
            raise AssertionError("Spectrum for %s appears to be multi-dimensional, expected %d Shape: %s" % (self,rows,self.shape))
    
    def __call__(self):
        """Call this frame, returning the data array"""
        return self.data
        
    
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
        dimensions = 2
        if not isinstance(data,np.ndarray):
            msg = "%s cannot handle objects of type %s, must be type %s" % (cls.__name__,type(data),np.ndarray)
            raise AbstractError(msg)
        if data.ndim != dimensions:
            LOG.warning("The data appears to be %d dimensional. This object expects %d dimensional data." % (len(data.shape),dimensions))
        Object = cls(data,label)
        try:
            Object.validate()
        except AssertionError as AE:
            msg = "%s data did not validate: %s" % (cls.__name__,AE)
            raise AbstractError(msg)
        LOG.debug("Saved %s with size %d" % (Object,Object.size))
        return Object
    
    @classmethod
    def __read__(cls,HDU,label):
        """An abstract method for reading empty data HDU Frames"""
        LOG.debug("Attempting to read as %s" % cls)
        if not isinstance(HDU,(pyfits.ImageHDU,pyfits.PrimaryHDU)):
            msg = "Must save a PrimaryHDU or ImageHDU to a %s, found %s" % (cls.__name__,type(HDU))
            raise AbstractError(msg)
        if not isinstance(HDU.data,np.ndarray):
            msg = "HDU Data must be %s for %s, found data of %s" % (np.ndarray,cls.__name__,type(HDU.data))
            raise AbstractError(msg)
        Object = cls(HDU.data,label)
        try:
            Object.validate()
        except AssertionError as AE:
            msg = "%s data did not validate: %s" % (cls.__name__,AE)
            raise AbstractError(msg)
        LOG.debug("Read %s with size %s" % (Object,Object.size))
        return Object
    

    


class SpectraObject(AstroObject.FITSObject):
    """A subclass of FITS image with specific facilites for displaying spectra"""
    def __init__(self, array=None):
        super(SpectraObject, self).__init__()
        self.dataClasses += [SpectraFrame]
        self.dataClasses.remove(AstroObject.FITSFrame)
        if array != None:
            self.save(array)        # Save the initializing data
        
        
        
        


            