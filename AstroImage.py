# 
#  AstroImage.py
#  Astronomy ObjectModel
#  
#  Created by Alexander Rudy on 2011-04-28.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 

import AstroObject

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

class ImageFrame(AstroObject.FITSFrame):
    """A single frame of a FITS image"""
    def __init__(self, array, label, header=None, metadata=None):
        super(ImageFrame, self).__init__(label, header, metadata)
        self.data = array # The image data
        self.size = array.size # The size of this image
        self.shape = array.shape # The shape of this image
        
    
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
        LOG.debug("Plotting %s using matplotlib.pyplot.imshow" % self)
        return plt.imshow(self())
    
    @classmethod
    def __save__(cls,data,label):
        """A generic class method for saving to this object with data directly"""
        if not isinstance(data,np.ndarray):
            msg = "ImageFrame cannot handle objects of type %s, must be type %s" % (type(data),np.ndarray)
            LOG.critical(msg)
            raise AbstractError(msg)
        if len(data.shape) != 2:
            LOG.warning("The data appears to be %d dimensional. This object expects 2 dimensional data." % len(data.shape))
        Object = cls(data,label)
        LOG.debug("Saved %s with size %d" % (Object,data.size))
        return Object

class ImageObject(AstroObject.FITSObject):
    """docstring for ImageObject"""
    def __init__(self, array=None):
        super(ImageObject, self).__init__()
        self.dataClass = ImageFrame
        if array != None:
            self.save(array)        # Save the initializing data
            
    def loadFromFile(self,filename=None,statename=None):
        """Load a regular image file into the object"""
        if not filename:
            filename = self.filename
        if statename == None:
            statename = os.path.basename(filename)
            LOG.debug("Set statename for image from filename: %s" % statename)
        self.save(mpimage.imread(filename),statename)
        LOG.info("Loaded Image from file: "+filename)
        
    def read(self,filename=None,statename=None):
        """This reader assumes that all HDUs are image HDUs"""
        if not filename:
            filename = self.filename
        if statename == None:
            statename = os.path.basename(filename)
            LOG.debug("Set statename for image from filename: %s" % statename)
        HDUList = pyfits.open(filename)
        Read = 0
        for HDU in HDUList:
            if isinstance(HDU,pyfits.PrimaryHDU):
                label = statename + " " + "Primary"
                self.save(HDU.data,label)
                Read += 1
            elif isinstance(HDU,pyfits.ImageHDU):
                if HDU.name:
                    label = statename + " " + HDU.name
                else:
                    label = statename + "HDU %d" % READ
                self.save(HDU.data,label)
                Read += 1
            else:
                LOG.warning("Skipping HDU %s, not an ImageHDU" % HDU)
        if not Read:
            LOG.warning("No HDUs were saved from this FITS file")
            

class OLDImageObject(AstroObject.FITSObject):
    """docstring for ImageObject"""
        
    #####################
    # Loading Functions #
    #####################

    
    def loadFromFITS(self,filename=None,statename=None):
        """Load a FITS File into the image object"""
        if not filename:
            filename = self.filename
        if statename == None:
            statename = os.path.basename(filename)
            LOG.debug("Set statename for image from filename: %s" % statename)
        HDUList = pyfits.open(filename)
        self.save(HDUList[0].data,statename)
        HDUList.close()
        LOG.info("Loaded Image from FITS file: "+filename)
    
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
    

                