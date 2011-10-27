# 
#  AstroImage.py
#  Astronomy ObjectModel
#  
#  Created by Alexander Rudy on 2011-04-28.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.2.0
# 

import AstroObjectBase

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
from Utilities import *

LOG = logging.getLogger(__name__)

class ImageFrame(AstroObjectBase.FITSFrame):
    """
    A single frame of a FITS image.
    Frames are known as Header Data Units, or HDUs when written to a FITS file.
    This frame accepts (generally) 2-dimensional numpy arrays (``ndarray``), and will show those arrays as images. Currently, the system makes no attempt to ensure/check the data type of your data arrays. As such, data saved will often be saved as ``np.float`` rather than more compact data types such as ``np.int16``. Pyfits handles the typing of your data automatically, so saving an array with the correct type will generate the proper FITS file.
    This object requires *array*, the data, a *label*, and can optionally take *headers* and *metadata*.
    
    """
    def __init__(self, array, label, header=None, metadata=None):
        super(ImageFrame, self).__init__(label, header, metadata)
        self.data = array # The image data
        self.size = array.size # The size of this image
        self.shape = array.shape # The shape of this image
        
    
    def __call__(self):
        """Returns the data for this frame, which should be a ``numpy.ndarray``."""
        return self.data
        
    def __hdu__(self,primary=False):
        """Retruns an HDU which represents this frame. HDUs are either ``pyfits.PrimaryHDU`` or ``pyfits.ImageHDU`` depending on the *primary* keyword."""
        if primary:
            LOG.info("Generating a primary HDU for %s" % self)
            return pyfits.PrimaryHDU(self())
        else:
            LOG.info("Generating an image HDU for %s" % self)
            return pyfits.ImageHDU(self())
            
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
        """Attempts to create a :class:`ImageFrame` object from the provided data. This requres some type checking to ensure that the provided data meets the general sense of such an image. If the data does not appear to be correct, this method will raise an :exc:`AbstractError` with a message describing why the data did not validate. Generally, this error will be intercepted by the caller, and simply provides an indication that this is not the right class for a particular piece of data.
        
        If the data is saved successfully, this method will return an object of type :class:`ImageFrame`
        
        The validation requires that the data be a type ``numpy.ndarray`` and that the data have 2 and only 2 dimensions.
        """
        LOG.debug("Attempting to save as %s" % cls)
        if not isinstance(data,np.ndarray):
            msg = "ImageFrame cannot handle objects of type %s, must be type %s" % (type(data),np.ndarray)
            raise AbstractError(msg)
        if len(data.shape) != 2:
            LOG.warning("The data appears to be %d dimensional. This object expects 2 dimensional data." % len(data.shape))
        Object = cls(data,label)
        LOG.debug("Saved %s with size %d" % (Object,data.size))
        return Object
    
    @classmethod
    def __read__(cls,HDU,label):
        """Attempts to convert a given HDU into an object of type :class:`ImageFrame`. This method is similar to the :meth:`__save__` method, but instead of taking data as input, it takes a full HDU. The use of a full HDU allows this method to check for the correct type of HDU, and to gather header information from the HDU. When reading data from a FITS file, this is the prefered method to initialize a new frame.
        """
        LOG.debug("Attempting to read as %s" % cls)
        if not isinstance(HDU,(pyfits.ImageHDU,pyfits.PrimaryHDU)):
            msg = "Must save a PrimaryHDU or ImageHDU to a %s, found %s" % (cls.__name__,type(HDU))
            raise AbstractError(msg)
        if not isinstance(HDU.data,np.ndarray):
            msg = "HDU Data must be %s for %s, found data of %s" % (np.ndarray,cls.__name__,type(HDU.data))
            raise AbstractError(msg)
        Object = cls(HDU.data,label)
        LOG.debug("Created %s" % Object)
        return Object
    


class ImageObject(AstroObjectBase.FITSObject):
    """This object tracks a number of data frames. This class is a simple subclass of :class:`AstroObjectBase.FITSObject` and usese all of the special methods implemented in that base class. This object sets up an image object class which has two special features. First, it uses only the :class:`ImageFrame` class for data. As well, it accepts an array in the initializer that will be saved immediately.
    """
    def __init__(self, array=None):
        super(ImageObject, self).__init__()
        self.dataClasses += [ImageFrame]
        self.dataClasses.remove(AstroObjectBase.FITSFrame)
        if array != None:
            self.save(array)        # Save the initializing data
            
    def loadFromFile(self,filename=None,statename=None):
        """This function can be used to load an image file (but not a FITS file) into this image frame. Image files should be formats accepatble to the Python Image Library, but that generally applies to most common image formats, such as .png and .jpg .
        This method takes a *filename* and a *statename* parameter. If either is not given, they will be generated using sensible defaults."""
        if not filename:
            filename = self.filename
        if statename == None:
            statename = os.path.basename(filename)
            LOG.debug("Set statename for image from filename: %s" % statename)
        self.save(mpimage.imread(filename),statename)
        LOG.info("Loaded Image from file: "+filename)
    


class OLDImageObject(AstroObjectBase.FITSObject):
    """docstring for ImageObject"""
    
    ##########################
    # File Writing Functions #
    ##########################
    
    def FITS(self,filename=None,statename=None):
        """Generates a FITS file of the specified filename, and returns that filename for convenience. This function will only include the specified statename."""
        if not statename:
            statename = self.statename
        if not filename:
            if self.filename == None:
                filename = statename
                LOG.warning("Setting Filename from statename %s. No filename validation was performed." % filename)
            else:
                filename = self.filename
                LOG.warning("Setting filename from default %s. No filename validation was performed" % filename)
        
        filename = validate_filename(filename)
        LOG.debug("Generating FITS File from state %s with filename %s" % (statename,filename))
        HDU = pyfits.PrimaryHDU(self.states[statename]()    )
        HDUList = pyfits.HDUList([HDU])
        HDUList.writeto(filename)
        LOG.info("Wrote FITS File %s" % filename)
        return filename
    
    def outFITS(self,filename=None,statename=None):
        """This creates a FITS file designed for output from an IRAF function.
        This function creates the FITS file, and requests that at the next opportune moment,
        the object should re-read the created FITS file, re-incorportating it in the object
        model and deleting the original file."""
        
        if not statename:
            statename = self.statename
        if not filename:
            if self.filename == None:
                filename = statename
                LOG.warning("Setting Filename from statename %s. No filename validation was performed." % filename)
            else:
                filename = self.filename
                LOG.warning("Setting filename from default %s. No filename validation was performed" % filename)
                
        filename = validate_filename(filename)
        if os.access(filename,os.F_OK):
            LOG.critical("FITS File %s Exists, and is scheduled to be over-written..." % filename)
        
        if not self.outputData:
            self.outputData = []
        self.outputData += [(filename,statename)]
        
        return filename
    
    def inFITS(self,filename=None,statename=None):
        """similar to outFITS, handles fits files used for IRAF routines"""
        filename = self.FITS(filename,statename)
        if not self.inputData:
            self.inputData = []
        self.inputData += [filename]
        
        return filename
    
    def reloadFITS(self):
        """Reloads the last created temporary FITS file from an action."""
        if self.outputData:
            for filename,statename in self.outputData:
                self.outputData = False
                self.loadFromFITS(filename,statename)
                if os.access(filename,os.F_OK):
                    os.remove(filename)
                    LOG.info("Deleted FITS file %s" % filename)
        if self.inputData:
            for filename in self.inputData:
                self.inputData = False
                if os.access(filename,os.F_OK):
                    os.remove(filename)
                    LOG.info("Deleted FITS file %s" % filename)
                
    
    
    ##########################
    # Manipulating Functions #
    ##########################
    def mask(self,left,top,right=None,bottom=None):
        """Masks the image by the distances provided"""
        if not right:
            right = left
        if not bottom:
            bottom = top
        shape  = self.states[self.statename].shape
        masked = self.states[self.statename].data[left:shape[0]-right,top:shape[1]-bottom]
        LOG.debug("Masked masked and saved image")
        self.save(masked,"Masked")
    
    def crop(self,x,y,xsize,ysize=None):
        """Crops the provided image to twice the specified size, centered around the x and y coordinates provided."""
        if not ysize:
            ysize = xsize
        cropped = self.states[self.statename].data[x-xsize:x+xsize,y-ysize:y+ysize]
        LOG.debug("Cropped and Saved Image")
        self.save(cropped,"Cropped")
    
    
    ######################
    # Plotting Functions #
    ######################
    def show(self):
        """Shows the image"""
        plt.imshow(self.states[self.statename].data,interpolation="nearest")
        plt.colorbar()
        LOG.debug("Plot Image using IMSHOW: %s" % self.statename)
    
    def show3D(self):
        """Shows a 3D contour of the image"""
        X = np.arange(self.states[self.statename].shape[0])
        Y = np.arange(self.states[self.statename].shape[1])
        X,Y = np.meshgrid(X,Y)
        Z = self.states[self.statename].data
        LOG.debug("3D Plotting: Axis Size %s %s %s" % (X.size, Y.size, Z.size))
        ax = plt.gca(projection='3d')
        surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.jet, linewidth=0, antialiased=False)
        plt.colorbar(surf, shrink=0.5, aspect=5)
        LOG.debug("Plot Image in 3D: %s" % self.statename)
    

                
