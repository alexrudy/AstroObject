# 
#  AstroObject.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.2.0
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
    """A single frame of a FITS image.
    Frames are known as Header Data Units, or HDUs when written to a FITS file.
    This frame is generic. It does not legitimately implement any functions. Rather, each function implemented is a placeholder, and will generate an :exc:`AbstractError` if called. Several objects inherit from this one to create HDUs which have some semantic meaning.
    This object requires a *label*, and can optionally take *headers* and *metadata*.
    
    .. Warning::
        This is an abstract object. Methods implemented here will *likely* raise an :exc:`AbstractError` indicating that you shouldn't be using these methods. This class is provided so that users can sub-class it for their own purposes. It also serves as the base class for other Frames in this package.
    
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
        """Should return the data within this frame, usually as a *numpy* array.
        
        For an example implementation, see :class:`AstroImage.ImageFrame`."""
        msg = "Abstract Data Structure %s was called, but cannot return data!" % self
        raise AbstractError(msg)
    
    def __str__(self):
        """Returns String Representation of this frame object. Will display the class name and the label. This method does not need to be overwritten by subclasses."""
        return "<\'%s\' labeled \'%s\'>" % (self.__class__.__name__,self.label)
    
    def __hdu__(self,primary=False):
        """Retruns a Header-Data Unit PyFits object. The abstract case generates empty HDUs, which contain no data.
        Subclasses should provide a *primary* keyword argument, and if that keyword is set, the method should return a primaryHDU."""
        LOG.warning("%s: Generating an Empty HDU" % (self))
        if primary:
            return pyfits.PrimaryHDU()
        else:
            return pyfits.ImageHDU()
    
    def __show__(self):
        """Should return a plot object for the current frame, after setting up this plot in matplotlib. 
        
        In general, this method should display data nicely, but should not do too much work, so as to be flexible for use with other plotting commands. It is best to do the minimal amount of work to simply show the data. The intent is for the user to call Object.show() when they want a quick view of the data in a given frame."""
        msg = "Abstract Data Structure %s cannot be used for plotting!" % (self)
        raise AbstractError(msg)
    
    @classmethod
    def __save__(cls,data,label):
        """A class save method is called when the parent object is trying to save raw data. In this case, the save method will take raw data and attempt to cast it as an object of its own type, returning such an object. If it can't do that (because the data doesn't appear to fit, or for pretty much any other reason) it should raise an :exc:`AbstractError` which will be handled by the calling object."""
        msg = "Abstract Data Structure %s cannot be the target of a save operation!" % (cls)
        raise AbstractError(msg)
        
    
    @classmethod
    def __read__(cls,HDU,label):
        """An abstract method for reading empty data HDU Frames"""
        LOG.debug("%s: Attempting to read data" % cls)
        if not isinstance(HDU,pyfits.PrimaryHDU):
            msg = "Must save a %s to a %s, found %s" % (pyfits.PrimaryHDU.__name__,cls.__name__,HDU.__class__.__name__)
            raise AbstractError(msg)
        if not HDU.data == None:
            msg = "HDU Data must be type %s for %s, found data of type %s" % (None,cls,type(HDU.data).__name__)
            raise AbstractError(msg)
        Object = cls(label)
        LOG.debug("%s: Created %s" % (cls,Object))
        return Object
    


class FITSObject(object):
    """This object tracks a number of data frames. The :attr:`Filename` is the default filename to use when reading and writing, and the :attr:`dataClass` argument accepts a list of new data classes to be used with this object. New data classes should conform to the data class standard.
    
    
    .. Note::
        This is an abstract object. Methods implemented here *may* raise an :exc:`AbstractError` indicating that you shouldn't be using these methods. This class is provided so that users can sub-class it for their own purposes. It is often acceptalbe to use this as your Object class so long as you provide a new Frame class to hold your data in the ``dataClasses`` argument.
    """
    def __init__(self,filename=None,dataClasses=None):
        super(FITSObject, self).__init__()
        # Image data variables.
        self.dataClasses = [FITSFrame]
        if dataClasses:
            self.dataClasses += dataClasses
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
        """Saves the given data to this object. If the data is an instance of one of the acceptable :attr:`dataClasses` then this method will simply save the data. Otherwise, it will attempt to cast the data into one of the acceptable :attr:`dataClasses` using their :meth:`__save__` mehtod."""
        # If we were passed raw data, and the dataClass can accept it, then go for it!
        if not isinstance(data,tuple(self.dataClasses)):
            Object = None
            for dataClass in self.dataClasses:
                try:
                    Object = dataClass.__save__(data,statename)
                except AbstractError as AE:
                    LOG.debug("Cannot save as %s: %s" % (dataClass,AE))
                else:
                    break
            if not Object:
                raise TypeError("Object to be saved cannot be cast as %s" % self.dataClasses)
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
        """Returns the raw data for the current state. This is done through the :meth:`FITSFrame.__call__` method, which should return basic data in as raw a form as possible. The purpose of this call is to allow the user get at the most recent piece of data as easily as possible.
        
        ..Note:: I have not finished examining some issues with referencing vs. copying data that comes out of this call. Be aware that manipulating some objects produced here may actually manipulate the version saved in the Object."""
        # Load the current stat if no state provided
        if not statename:
            statename = self.statename
        if statename != None and statename in self.states:
            return self.states[statename]()
        else:
            raise KeyError("Object %s not instantiated with any data..." % self)
    
    def frame(self,statename=None):
        """Returns the FITSFrame Specfied. This method give you the raw frame object to play with, and can be useful for transferring frames around, or if your API is built to work with frames rather than raw data.
        
        ..Note:: Using frames can be advantageous as you don't rely on the Object to guess what type of frame should be used. Most times, the object will guess correctly, but Frames are a more robust way of ensuring type consistency."""
        if not statename:
            statename = self.statename
        if statename != None and statename in self.states:
            return self.states[statename]
        else:
            raise KeyError("Object %s not instantiated with any data..." % self)
    
    def object(self,statename=None):
        LOG.info("Method \".object()\" on %s has been depreciated. Please use \".frame()\" instead.")
        return self.frame(statename)
        
    def select(self,statename):
        """Sets the default frame to the given statename. Normally, the default frame is the one that was last saved."""
        if statename not in self.states:
            raise IndexError("State %s does not exist!" % statename)
        self.statename = statename
        LOG.debug("Selected state \'%s\'" % statename)
        return
    
    def list(self):
        """Provides a list of the available frames, by label."""
        return self.states.keys()
    
    def remove(self,statename):
        """Removes the specified frame from the object."""
        if statename not in self.states:
            raise IndexError("%s: Object %s does not exist!" % (self,statename))
        LOG.debug("%s: Removing Object with label %s" % (self,statename))
        self.states.pop(statename)
    
    def show(self,statename=None):
        """Returns the (rendered) matplotlib plot for this object. This is a quick way to view your current data state without doing any serious plotting work. This aims for the sensible defaults philosophy, if you don't like what you get, write a new method that uses the :meth:`data` call and plots that."""
        # Load the current stat if no state provided
        if not statename:
            statename = self.statename
        if statename != None and statename in self.states:
            return self.states[statename].__show__()
        else:
            raise KeyError("Object not instantiated with any data...")
    
    def write(self,filename=None,states=None,primaryState=None,clobber=False):
        """Writes a FITS file for this object. Generally, the FITS file will include all frames curretnly available in the system. If you specify ``states`` then only those states will be used. ``primaryState`` should be the state of the front HDU. When not specified, the latest state will be used. It uses the :attr:`dataClasses` :meth:`FITSFrame.__hdu__` method to return a valid HDU object for each Frame."""
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
        HDUList.writeto(filename,clobber=clobber)
    
    def read(self,filename=None,statename=None):
        """This reader takes a FITS file, and trys to render each HDU within that FITS file as a frame in this Object. As such, it might read multiple frames. This method will return a list of Frames that it read. It uses the :attr:`dataClasses` :meth:`FITSFrame.__read__` method to return a valid Frame object for each HDU."""
        if not filename:
            filename = self.filename
        if statename == None:
            statename = os.path.basename(filename)
            LOG.debug("Set statename for image from filename: %s" % statename)
        HDUList = pyfits.open(filename)
        Read = 0
        Labels = []
        for HDU in HDUList:
            Object = None
            for dataClass in self.dataClasses:
                if Read != 0:
                    label = statename + " Frame %d" % Read
                else:
                    label = statename
                try:
                    Object = dataClass.__read__(HDU,label)
                except AbstractError as AE:
                    LOG.debug("Cannot read as %s: %s" % (dataClass,AE))
                else:
                    break
            if not Object:
                LOG.warning("Skipping HDU %s, cannot save as valid type " % HDU)
            else:
                Read += 1
                Labels += [label]
                self.save(Object)
        if not Read:
            msg = "No HDUs were saved from FITS file %s to %s" % (filename,self)
            raise ValueError(msg)
        
        return Labels
    
