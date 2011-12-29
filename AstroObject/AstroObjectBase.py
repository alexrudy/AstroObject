# 
#  AstroObject.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.2.6
# 


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

__all__ = ["FITSFrame","FITSObject"]

__version__ = getVersion()

LOG = logging.getLogger(__name__)

class FITSFrame(object):
    """A single frame of a FITS image.
    Frames are known as Header Data Units, or HDUs when written to a FITS file.
    This frame is generic. It does not legitimately implement any functions. Rather, each function implemented is a placeholder, and will generate an :exc:`AbstractError` if called. Several objects inherit from this one to create HDUs which have some semantic meaning.
    This object requires a *label*, and can optionally take *headers* and *metadata*.
    
    .. Warning::
        This is an abstract object. Methods implemented here will *likely* raise an :exc:`AbstractError` indicating that you shouldn't be using these methods. This class is provided so that users can sub-class it for their own purposes. It also serves as the base class for other Frames in this package.
    
    """
    def __init__(self, data=None, label=None, header=None, metadata=None, **kwargs):
        super(FITSFrame, self).__init__(**kwargs)
        if data != None:
            self.data = data
        self.label = label # A label for this frame, for selection in parent object
        self.header = header # A dictionary of header keys and values for use in HDU generation
        self.metadata = metadata # An optional metadata dictionary
        self.time = time.clock() # An object representing the time this object was created
        
        if self.metadata == None:
            self.metadata = {}
        if self.header == None:
            self.header = {}
        try:
            self.__valid__()
            assert isinstance(self.label,str), "Frame requires a label, got %s" % self.label
        except AssertionError as e:
            raise AttributeError(str(e))
        
    
    def __call__(self):
        """Should return the data within this frame, usually as a *numpy* array.
        
        :class:`AstroImage.ImageFrame` implements this method as::
            
            def __call__(self):
                return self.data
            
        """
        msg = "Abstract Data Structure %s was called, but cannot return data!" % self
        raise AbstractError(msg)
    
    def __str__(self):
        """Returns String Representation of this frame object. Will display the class name and the label. This method does not need to be overwritten by subclasses."""
        return "<\'%s\' labeled \'%s\'>" % (self.__class__.__name__,self.label)
    
    def __valid__(self):
        """Runs a series of assertions which ensure that the data for this frame is valid"""
        assert not hasattr(self,'data'), "Abstract Class cannot accept data!"
    
    def __hdu__(self,primary=False):
        """Retruns a Header-Data Unit PyFits object. The abstract case generates empty HDUs, which contain no data.
        Subclasses should provide a *primary* keyword argument, and if that keyword is set, the method should return a primaryHDU."""
        if primary:
            HDU = pf.PrimaryHDU()
        else:
            HDU = pf.ImageHDU()
        LOG.warning("%s: Generating an Empty %sHDU" % (self,"primary " if primary else ""))
        HDU.header.update('label',self.label)
        HDU.header.update('object',self.label)
        for key,value in self.header.iteritems():
            HDU.header.update(key,value)
        return HDU
    
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
        if not isinstance(HDU,pf.PrimaryHDU):
            msg = "Must save a %s to a %s, found %s" % (pf.PrimaryHDU.__name__,cls.__name__,HDU.__class__.__name__)
            raise AbstractError(msg)
        if not HDU.data == None:
            msg = "HDU Data must be type %s for %s, found data of type %s" % (None,cls,type(HDU.data).__name__)
            raise AbstractError(msg)
        Object = cls(None,label)
        LOG.debug("%s: Created %s" % (cls,Object))
        return Object
    


class FITSObject(object):
    """This object tracks a number of data frames. The :attr:`Filename` is the default filename to use when reading and writing, and the :attr:`dataClass` argument accepts a list of new data classes to be used with this object. New data classes should conform to the data class standard.
    
    
    .. Note::
        This is object only contains Abstract data objects. In order to use this class properly, you should set the dataClasses keyword for use when storing data.
    """
    def __init__(self,filename=None,dataClasses=None,**kwargs):
        super(FITSObject, self).__init__(**kwargs)
        # Image data variables.
        self.dataClasses = [FITSFrame]
        if dataClasses:
            self.dataClasses += dataClasses
        self.states = {}            # Storage for all of the images
        self.statename = None       # The active state name
        self.filename = filename    # The filename to use for file loading and writing
        self.plt = plt
        self.clobber = False
        self.name = False
        
    def __str__(self):
        """String representation of this object"""
        if self.name:
            return "<\'%s\' labeled \'%s\'>" % (self.__class__.__name__,self.name)
        else:
            return super(FITSObject, self).__str__()
    
    ###############################
    # Basic Object Mode Functions #
    ###############################
    def save(self,data,statename=None,clobber=False):
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
        if statename in self.states and not (clobber or self.clobber):
            raise KeyError("Cannot Duplicate State Name: %s \nUse remove(\'%s\') to clear" % (statename,statename))
        elif statename in self.states:
            LOG.debug("Overwiting the frame %s" % statename)
        # Save the actual state
        self.states[statename] = Object
        LOG.info("Saved frame %s" % Object)
        # Activate the saved state as the current state
        self.select(statename)
    
    def data(self,statename=None):
        """Returns the raw data for the current state. This is done through the :meth:`FITSFrame.__call__` method, which should return basic data in as raw a form as possible. The purpose of this call is to allow the user get at the most recent piece of data as easily as possible.
        
        .. Warning::
            I have not finished examining some issues with referencing vs. copying data that comes out of this call. Be aware that manipulating some objects produced here may actually manipulate the version saved in the Object. The current implementation which protects this call relies on the numpy copy command, ``np.copy(state())``, which might fail when used with data objects that do not return numpy arrays.
        """
        # Load the current stat if no state provided
        if not statename:
            statename = self.statename
        if statename != None and statename in self.states:
            return np.copy(self.states[statename]())
        else:
            raise KeyError("Object %s not instantiated with any data..." % self)
    
    def frame(self,statename=None):
        """Returns the FITSFrame Specfied. This method give you the raw frame object to play with, and can be useful for transferring frames around, or if your API is built to work with frames rather than raw data.
        
        .. Warning::
            Unlike with the :meth:`FITSObject.data` call, the object returned here should be treated as roughly immutable. That is, it is not advisable to re-use the data frame here, as Python has returned a reference to all examples of this data frame in your code::
                
                >>> obj = FITSObject()
                >>> obj.save(FITSFrame(None,"Label"))
                >>> Frame = obj.frame()
                >>> Frame.label = "Other"
                >>> obj.frame().label
                "Other"
                
        
        .. Note:: 
            Using frames can be advantageous as you don't rely on the Object to guess what type of frame should be used. Most times, the object will guess correctly, but Frames are a more robust way of ensuring type consistency"""
        if not statename:
            statename = self.statename
        if statename != None and statename in self.states:
            return self.states[statename]
        else:
            raise KeyError("Object %s not instantiated with any data..." % self)
    
    def object(self,statename=None):
        LOG.info("Method \".object()\" on %s has been depreciated. Please use \".frame()\" instead." % self)
        return self.frame(statename)
        
    def select(self,statename):
        """Sets the default frame to the given statename. Normally, the default frame is the one that was last saved."""
        if statename not in self.states:
            raise IndexError("State %s does not exist!" % statename)
        self.statename = statename
        LOG.info("Selected state \'%s\'" % statename)
        return
    
    def list(self):
        """Provides a list of the available frames, by label."""
        return self.states.keys()
    
    def _default_state(self,states=None):
        """Returns the default state name. If the currently selected state exists, it's state name will return. If not, the system will search for the newest state."""
        if states == None:
            states = self.list()
        if self.statename in states:
            return self.statename
        if [] == states:
            return None
        Ages = [ time.clock() - self.frame(name).time for name in states ]
        youngest = states[np.argmin(Ages)]
        return youngest
    
    def clear(self):
        """Clears all states from this object. Returns an empty list representing the currently known states."""
        self.states = {}
        self.statename = self._default_state()
        LOG.info("%s: Cleared all states. Remaining: %s" % (self,self.list()))
        return self.list()
    
    
    def keep(self,*statenames):
        """Removes all states except the specified frame(s) in the object"""
        oldStates = self.states
        newStates = {}
        for statename in statenames:
            if statename not in self.states:
                raise IndexError("%s: Object %s does not exist!" % (self,statename))
            newStates[statename] = oldStates[statename]
        LOG.info("%s: Kept states %s" % (self,list(statenames)))
        self.states = newStates
        self.statename = self._default_state()
        return self.list()
    
    def remove(self,*statenames):
        """Removes the specified frame(s) from the object."""
        removed = []
        for statename in statenames:
            if statename not in self.states:
                raise IndexError("%s: Object %s does not exist!" % (self,statename))
            self.states.pop(statename)
            removed += [statename]
        self.statename = self._default_state()
        LOG.info("%s: Removed states %s" % (self,removed))
        return self.list()
    
    def show(self,statename=None):
        """Returns the (rendered) matplotlib plot for this object. This is a quick way to view your current data state without doing any serious plotting work. This aims for the sensible defaults philosophy, if you don't like what you get, write a new method that uses the :meth:`data` call and plots that."""
        # Load the current stat if no state provided
        if not statename:
            statename = self._default_state()
        if statename != None and statename in self.states:
            return self.states[statename].__show__()
        else:
            raise KeyError("Object not instantiated with any data...")
    
    def write(self,filename=None,states=None,primaryState=None,clobber=False):
        """Writes a FITS file for this object. Generally, the FITS file will include all frames curretnly available in the system. If you specify ``states`` then only those states will be used. ``primaryState`` should be the state of the front HDU. When not specified, the latest state will be used. It uses the :attr:`dataClasses` :meth:`FITSFrame.__hdu__` method to return a valid HDU object for each Frame."""
        if not states:
            states = self.list()
            LOG.debug("Saving all states: %s" % states)
        if not primaryState:
            primaryState = self._default_state(states)
            LOG.debug("Set primary statename to default state %s" % primaryState)
        if primaryState in states:
            states.remove(primaryState)
        if not filename:
            if self.filename == None:
                filename = primaryState
                LOG.debug("Set Filename from Primary State. Filename: %s" % filename)
            else:
                filename = self.filename
                LOG.debug("Set filename from Object. Filename: %s" % filename)
        filename = validate_filename(filename)
        PrimaryHDU = self.states[primaryState].__hdu__(primary=True)
        if len(states) > 0:
            HDUs = [self.states[state].__hdu__(primary=False) for state in states]
            HDUList = pf.HDUList([PrimaryHDU]+HDUs)
        else:
            HDUList = pf.HDUList([PrimaryHDU])
        HDUList.writeto(filename,clobber=clobber)
        LOG.info("Wrote state %s (primary) and states %s to FITS file %s" % (primaryState,states,filename))
    
    def read(self,filename=None,statename=None):
        """This reader takes a FITS file, and trys to render each HDU within that FITS file as a frame in this Object. As such, it might read multiple frames. This method will return a list of Frames that it read. It uses the :attr:`dataClasses` :meth:`FITSFrame.__read__` method to return a valid Frame object for each HDU.
        
        ::
            
            >>> obj = FITSObject()
            >>> obj.read("SomeImage.fits")
            >>> obj.list()
            ["SomeImage","SomeImage Frame 1","SomeImage Frame 2"]
            
        """
        if not filename:
            filename = self.filename
        if statename == None:
            statename = os.path.basename(filename)
            LOG.debug("Set statename for image from filename: %s" % statename)
        HDUList = pf.open(filename)
        Read = 0
        Labels = []
        for HDU in HDUList:
            Object = None
            for dataClass in self.dataClasses:
                if "label" in HDU.header:
                    label = HDU.header["label"]
                elif Read != 0:
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
        
        LOG.info("Saved states %s" % Labels)
        return Labels
    
