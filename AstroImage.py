# 
#  AstroImage.py
#  Astronomy ObjectModel
#  
#  Created by Alexander Rudy on 2011-04-28.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 
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

class FITSFrame(object):
    """A single frame of a FITS image"""
    def __init__(self, array, label, header=None, metadata=None):
        super(FITSFrame, self).__init__()
        self.data = array # The image data
        self.label = label # A label for this frame, for selection in parent object
        self.size = array.size # The size of this image
        self.shape = array.shape # The shape of this image
        self.header = header # A dictionary of header keys and values for use in 
        self.metadata = metadata # An optional metadata dictionary
        self.time = time.strftime("%Y-%m-%dT%H:%M:%S")
        
        
        if self.metadata == None:
            self.metadata = {}
        if self.header == None:
            self.header = {}
        
        return
    


class FITSImage(object):
    """Holds on to a regular numpy-formated feature list image."""
    def __init__(self,dimensions=2,array=None,filename=None):
        super(FITSImage, self).__init__()
        # Image data variables.
        self.DIMEN = dimensions     # Total number of dimensions, i.e. x and y, or wavelength
        self.states = {}            # Storage for all of the images
        self.statename = None       # The active state name
        self.filename = filename    # The filename to use for file loading and writing
        self.plt = plt
        self.outputData = False
        self.inputData = False
        
        
        if array != None:
            self.save(array)        # Save the initializing data
    
    
    ##############################
    # Basic Image Mode Functions #
    ##############################
    def save(self,array,statename="Original"):
        """Saves the given image to this object"""
        # Error checking for provided arguments
        if statename in self.states:
            raise IndexError("Cannot Duplicate State Name: %s \nUse remove(\'%s\') to clear" % (statename,statename))
        if type(array) != np.ndarray:
            raise TypeError("Array to be saved is not a numpy array \nCheck that you are saving a numpy image array \nType: %s" % type(array))
        
        # Save the actual state
        self.states[statename] = FITSFrame(array,statename)
        # Activate the saved state as the current state
        self.select(statename)
        LOG.debug("Saved image of size %d with label %s" % (self.states[statename].size,statename))
    
    def data(self,statename=None):
        """Returns the numpy image for this object"""
        # Load the current stat if no state provided
        if not statename:
            statename = self.statename
        if statename != None and statename in self.states:
            return self.states[statename].data
        else:
            raise KeyError("Image not instantiated with any data...")
    
    def object(self,statename=None):
        """Returns the FITSFrame Specfied"""
        if not statename:
            statename = self.statename
        if statename != None and statename in self.states:
            return self.states[statename]
        else:
            raise KeyError("Image not instantiated with any data...")
    
    def select(self,statename):
        """Sets the default image to the given name"""
        if statename not in self.states:
            raise IndexError("Image %s does not exist!" % statename)
        self.statename = statename
        LOG.debug("Selected state %s" % statename)
        return
    
    def list(self):
        """Provides a list of the available images"""
        return self.states.keys()
    
    def remove(self,statename):
        """Removes the specified image from the object"""
        if image not in self.states:
            raise IndexError("Image %s does not exist!" % statename)
        LOG.debug("Removing image with label %s" % (statename))
        self.states.pop(statename)
    
    
    #####################
    # Loading Functions #
    #####################
    def loadFromFile(self,filename=None,statename=None):
        """Load a regular image file into the object"""
        if not filename:
            filename = self.filename
        if statename == None:
            statename = os.path.basename(filename)
            LOG.debug("Set statename for image from filename: %s" % statename)
        self.save(mpimage.imread(filename),statename)
        LOG.info("Loaded Image from file: "+filename)
    
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
        HDU = pyfits.PrimaryHDU(self.states[statename].data)
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
            LOG.critical("FITS File %s Exists, and is scheduled to be over-written...")
        
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
    

                