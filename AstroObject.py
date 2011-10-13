# 
#  AstroObject.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-12.
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
    """A single frame of a FITS image
    Frames are known as Header Data Units, or HDUs when written to a FITS file.
    This frame is generic. It does not legitimately implement any functions. Rather, each function implemented is a placeholder, and will generate a CRITICAL Log entry if called. Several objects inherit from this one to create HDUs which have some semantic meaning.
    This object requires a label, and can optionally take headers and metadata
    
    """
    def __init__(self, label, header=None, metadata=None):
        super(FITSFrame, self).__init__()
        self.label = label # A label for this frame, for selection in parent object
        self.header = header # A dictionary of header keys and values for use in 
        self.metadata = metadata # An optional metadata dictionary
        self.time = time.clock() # An object representing the time this object was created
        
        if self.metadata == None:
            self.metadata = {}
        if self.header == None:
            self.header = {}
    
    def __call__(self):
        """Returns the objects data"""
        LOG.critical("Object %s was called, but not instantiated as a proper data type!" % self)
        raise AbstractError("Abstract Data Structure cannot return data!")
    
    def __str__(self):
        """String Representation of an Object"""
        return "<\'%s\' labeled \'%s\'>" % (self.__class__.__name__,self.label)
    
    def __hdu__(self,primary=False):
        """Retruns a Header-Data Unit"""
        LOG.critical("Generating an Empty HDU from %s" % self)
        if primary:
            return pyfits.PrimaryHDU()
        else:
            return pyfits.ImageHDU()
    
    def __show__(self):
        """Returns a plot object for the current Frame"""
        LOG.critical("Plotting from a generic object %s is undefined" % self)
        raise AbstractError("Abstract Data Structure cannot be used for plotting!")
    
    @classmethod
    def __save__(cls,data,label):
        """A generic class method for saving to this object with data directly"""
        LOG.critical("Abstract Data Structure cannot be the target of a save operation!")
        raise AbstractError("Abstract Data Structure cannot be used for saving!")
        
class FITSObject(object):
    """Holds on to a regular numpy-formated feature list image."""
    def __init__(self,filename=None):
        super(FITSObject, self).__init__()
        # Image data variables.
        self.dataClass = FITSFrame
        self.states = {}            # Storage for all of the images
        self.statename = None       # The active state name
        self.filename = filename    # The filename to use for file loading and writing
        self.plt = plt
        self.outputData = False
        self.inputData = False
        
    
    ###############################
    # Basic Object Mode Functions #
    ###############################
    def save(self,data,statename=None):
        """Saves the given image to this object"""
        # If we were passed raw data, and the dataClass can accept it, then go for it!
        if not isinstance(data,self.dataClass):
            try:
                Object = self.dataClass.__save__(data,statename)
            except AbstractError:
                raise TypeError("Object to be saved is not of type %s" % self.dataClass)
        else:
            Object = data
            
        if statename == None:
            statename = Object.label
        else:
            Object.label = statename
        if statename in self.states:
            raise KeyError("Cannot Duplicate State Name: %s \nUse remove(\'%s\') to clear" % (statename,statename))
        # Save the actual state
        self.states[statename] = Object
        # Activate the saved state as the current state
        self.select(statename)
        LOG.debug("Saved frame %s" % Object)
    
    def data(self,statename=None):
        """Returns the numpy image for this object"""
        # Load the current stat if no state provided
        if not statename:
            statename = self.statename
        if statename != None and statename in self.states:
            return self.states[statename]()
        else:
            raise KeyError("Object not instantiated with any data...")
    
    def object(self,statename=None):
        """Returns the FITSFrame Specfied"""
        if not statename:
            statename = self.statename
        if statename != None and statename in self.states:
            return self.states[statename]
        else:
            raise KeyError("Object not instantiated with any data...")
    
    def select(self,statename):
        """Sets the default image to the given name"""
        if statename not in self.states:
            raise IndexError("Object %s does not exist!" % statename)
        self.statename = statename
        LOG.debug("Selected state %s" % statename)
        return
    
    def list(self):
        """Provides a list of the available images"""
        return self.states.keys()
    
    def remove(self,statename):
        """Removes the specified image from the object"""
        if image not in self.states:
            raise IndexError("Object %s does not exist!" % statename)
        LOG.debug("Removing Object with label %s" % (statename))
        self.states.pop(statename)
    
    def show(self,statename=None):
        """Returns the (rendered) matplotlib plot for this object"""
        # Load the current stat if no state provided
        if not statename:
            statename = self.statename
        if statename != None and statename in self.states:
            return self.states[statename].__show__()
        else:
            raise KeyError("Object not instantiated with any data...")
    
    def write(self,filename=None,states=None,primaryState=None):
        """Writes a FITS file for this object"""
        if not primaryState:
            primaryState = self.statename
        if not filename:
            if self.filename == None:
                filename = primaryState
            else:
                filename = self.filename
        filename = validate_filename(filename)
        if not states:
            states = self.list()
        if primaryState in states:
            states.remove(primaryState)
        PrimaryHDU = self.states[primaryState].__hdu__(primary=True)
        if states:
            HDUs = [self.states[state].__hdu__(primary=False) for state in states]
            HDUList = pyfits.HDUList([PrimaryHDU]+HDUs)
        else:
            HDUList = pyfits.HDUList(PrimaryHDU)
        HDUList.writeto(filename)
        
    def read(self,filename=None,statename=None):
        """This reader assumes that all HDUs are image HDUs"""
        if not filename:
            filename = self.filename
        if statename == None:
            statename = os.path.basename(filename)
            LOG.debug("Set statename for image from filename: %s" % statename)
        HDUList = pyfits.open(filename)
        Read = False
        for HDU in HDUList:
            if isinstance(HDU,pyfits.PrimaryHDU) and HDU.data == None:
                label = statename + " " + "Empty Primary"
                self.save(FITSFrame(label))
                Read = True
            else:
                LOG.warning("Skipping HDU %s, not an Empty Primary HDU" % HDU)
        if not Read:
            LOG.warning("No HDUs were saved from this FITS file")
