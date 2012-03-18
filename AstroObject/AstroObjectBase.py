# 
#  AstroObject.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.3.1
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

__all__ = ["FITSFrame","FITSObject","BaseFrame"]

__version__ = getVersion()

LOG = logging.getLogger(__name__)

class BaseFrame(object):
    """This is the API for frame objects, that is, objects which represnet a single state of data. See :class:`AstroObjectBase.FITSFrame`. This API is generally not called by the end user, but rather is called by the parent :class:`AstroObject.AstroObjectBase.FITSObject`'s function. For an example of a parent object, see :class:`AstroObjectBase.FITSObject`.
    
    :param data: Initalizing data
    :param label: string label
    :param header: dictionary of header items or pyfits.header
    :param metadata: dictionary of arbitrary metadata
    :raises AttributeError: when the frame fails to validate. See :meth:`__valid__`
    
    """
    def __init__(self, data=None, label=None, header=None, metadata=None, **kwargs):
        super(BaseFrame, self).__init__(**kwargs)
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
            assert isinstance(self.label,(str,unicode)), "Frame requires a label, got %s" % self.label
        except AssertionError as e:
            raise AttributeError(str(e))

    def __call__(self,**kwargs):
        """Should return the data within this frame, usually as a ``numpy`` array.
        
        :returns: None
        
        :class:`AstroImage.ImageFrame` implements this method as::
            
            def __call__(self):
                return self.data
            
        """
        msg = "Abstract Data Structure %s was called, but cannot return data!" % self
        raise AbstractError(msg)
    
    def __repr__(self):
        """Returns String Representation of this frame object. Will display the class name and the label. This method does not need to be overwritten by subclasses.
        
        :returns: literal sting representation
        """
        return "<\'%s\' labeled \'%s\'>" % (self.__class__.__name__,self.label)
    
    def __valid__(self):
        """Runs a series of assertions which ensure that the data for this frame is valid
        
        :raises: :exc:`AssertionError` when frame is invalid
        :returns: ``None``"""
        assert not hasattr(self,'data'), "Abstract Class cannot accept data!"
    
    def __hdu__(self,primary=False):
        """This method returns an HDU which represents the object. The HDU should respect the object's :attr:`header` attribute, and use that dictionary to populate the headers of the HDU. 
        
        :param primary: boolean, produce a primary HDU or not
        :raises: :exc:`AbstractError` When the object cannot make a well-formed HDU
        :returns: pyfits.PrimaryHDU or pyfits.HDU
        
        If the frame cannot reasonable generate a :class:`pyFITS.PrimaryHDU`, then it should raise an :exc:`AbstractError` in that case."""
        msg = "Abstract Data Structure %s cannot be used for HDU Generation!" % (self)
        raise AbstractError(msg)

    
    def __show__(self):
        """This method should create a simple view of the provided frame. Often this is done using :mod:`Matplotlib.pyplot` to create a simple plot. The plot should have the minimum amount of work done to make a passable plot view, but still be basic enough that the end user can customize the plot object after calling :meth:`__show__`.
        
        :returns: Matplotlib plot object"""
        msg = "Abstract Data Structure %s cannot be used for plotting!" % (self)
        raise AbstractError(msg)
    
    @classmethod
    def __save__(cls,data,label):
        """This method should retun an instance of the parent class if the given data can be turned into an object of that class. If the data cannot be correctly cast, this method should throw an :exc:`AbstractError`.
        
        :param data: Data to be saved, in raw form.
        :param label: Name for the newly created frame.
        :raises: :exc:`AbstractError` when this data can't be saved.
        :returns: :class:`BaseFrame`
        
        .. Note:: Because the :meth:`__valid__` is called when an object is initialized, it is possible to check some aspects of the provided data in this initialization function. However, this would raise an :exc:`AssertionError` not an :exc:`AbstractError`. To avoid this problem, it is suggested that you wrap your initialization in a try...except block like::
                
                try:
                    Object = cls(HDU.data,label)
                except AssertionError as AE:
                    msg = "%s data did not validate: %s" % (cls.__name__,AE)
                    raise AbstractError(msg)
                
            This block simply changes the error type emitted from the __valid__ function. This trick is not a substituion for data validation before initializing the class. Just instantiating a class like this often results in bizzare errors (like :exc:`AttributeError`) which are diffult to track and diagnose without the code in :meth:`__save__`. See :meth:`AstroImage.__save__` for an example ``__save__`` function which uses this trick, but also includes some basic data validation."""
        msg = "Abstract Data Structure %s cannot be the target of a save operation!" % (cls)
        raise AbstractError(msg)
        
    
    @classmethod
    def __read__(cls,HDU,label):
        """This method should return an instance of the parent class if the given ``HDU`` can be turned into an object of that class. If this is not possible (i.e. a Table HDU is provided to an Image Frame), this method should raise an :exc:`AbstractError` with a message that describes the resaon the data could not be cast into this type of frame.
        
        :param data: HDU to be saved, as a ``pyfits.HDU``.
        :param label: Name for the newly created frame.
        :raises: :exc:`AbstractError` when this data can't be saved.
        :returns: :class:`BaseFrame`
        
        .. Note:: Because the :meth:`__valid__` is called when an object is initialized, it is possible to check some aspects of the provided data in this initialization function. However, this would raise an :exc:`AssertionError` not an :exc:`AbstractError`. To avoid this problem, it is suggested that you wrap your initialization in a try...except block like::
                
                try:
                    Object = cls(HDU.data,label)
                except AssertionError as AE:
                    msg = "%s data did not validate: %s" % (cls.__name__,AE)
                    raise AbstractError(msg)
                
            This block simply changes the error type emitted from the __valid__ function. This trick is not a substituion for data validation before initializing the class. Just instantiating a class like this often results in bizzare errors (like :exc:`AttributeError`) which are diffult to track and diagnose without the code in :meth:`__read__`. See :meth:`AstroImage.__read__` for an example ``__read__`` function which uses this trick, but also includes some basic data validation.
            
        .. Note:: It is acceptable to call the class :meth:`__save__` function here. However, the :meth:`__read__` function should also correctly handle header data."""
        msg = "Abstract Data Structure %s cannot be the target of a read operation!" % (cls)
        raise AbstractError(msg)
        

    
        

class FITSFrame(BaseFrame):
    """A single frame of a FITS image.
    Frames are known as Header Data Units, or HDUs when written to a FITS file.
    This frame is generic. It does not legitimately implement any functions. Rather, each function implemented is a placeholder, and will generate an :exc:`AbstractError` if called. Several objects inherit from this one to create HDUs which have some semantic meaning.
    
    :param None data: The data to be saved.
    :param string label: A string name for this frame
    :param header: pyfits.header or dictionary of header options
    :param metadata: dictionary of arbitrary metadata
    
    .. Warning::
        This is an abstract object. Methods implemented here will *likely* raise an :exc:`AbstractError` indicating that you shouldn't be using these methods. This class is provided so that users can sub-class it for their own purposes. It also serves as the base class for other Frames in this package.
    
    """
    def __init__(self, data=None, label=None, header=None, metadata=None, **kwargs):
        super(FITSFrame, self).__init__(data=data, label=label, header=header, metadata=metadata,**kwargs)
    
    def __hdu__(self,primary=False):
        """Retruns a Header-Data Unit PyFits object. The abstract case generates empty HDUs, which contain no data.
        
        :param bool primary: Return a primary HDU
        :returns: pyfits.primaryHDU or pyfits.ImageHDU
        """
        if primary:
            HDU = pf.PrimaryHDU()
        else:
            HDU = pf.ImageHDU()
        LOG.log(8,"%s: Generating an Empty %sHDU" % (self,"primary " if primary else ""))
        HDU.header.update('label',self.label)
        HDU.header.update('object',self.label)
        for key,value in self.header.iteritems():
            HDU.header.update(key,value)
        return HDU
    
    @classmethod
    def __read__(cls,HDU,label):
        """An abstract method for reading empty data HDU Frames.
        
        :param data: HDU to be saved, as a ``pyfits.HDU``.
        :param label: Name for the newly created frame.
        :raises: :exc:`AbstractError` when this data can't be saved.
        :returns: :class:`FITSFrame`
        """
        if not isinstance(HDU,pf.PrimaryHDU):
            msg = "Must save a %s to a %s, found %s" % (pf.PrimaryHDU.__name__,cls.__name__,HDU.__class__.__name__)
            raise AbstractError(msg)
        if not HDU.data == None:
            msg = "HDU Data must be type %s for %s, found data of type %s" % (None,cls,type(HDU.data).__name__)
            raise AbstractError(msg)
        Object = cls(None,label)
        LOG.log(2,"%s: Created %s" % (cls,Object))
        return Object
    


class FITSObject(dict):
    """This object tracks a number of data frames. The :attr:`Filename` is the default filename to use when reading and writing, and the :attr:`dataClass` argument accepts a list of new data classes to be used with this object. New data classes should conform to the data class standard.
    
    :param filename: String name of default file for reading and writing with :meth:`read` and :meth:`write`.
    :param dataClasses: An array of classes which constitute valid save classes for this object.
    
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
        
    def __repr__(self):
        """String representation of this object.
        
        :returns: string
        """
        if self.name:
            return "<\'%s\' labeled \'%s\'>" % (self.__class__.__name__,self.name)
        else:
            return super(FITSObject, self).__repr__()
    
    def __getitem__(self,key):
        """Dictionary access to frames in the Object"""
        return self.frame(key)
        
    def __setitem__(self,key,value):
        """Dictionary assignment of frames in the Object"""
        self.save(value,key,clobber=True)
        
    def __delitem__(self,key):
        """Dictionary deletion of frames in the Object"""
        self.remove(key)
        
    def __iter__(self):
        """Dictionary iterator call."""
        return self.states.iterkeys()
        
    def __contains__(self,item):
        """Dictionary contain testing"""
        return item in self.states
        
    def keys(self):
        """Dictionary keys.
        
        :returns: list"""
        return self.states.keys()
        
    ###############################
    # Basic Object Mode Functions #
    ###############################
    def save(self,data,statename=None,clobber=False):
        """Saves the given data to this object. If the data is an instance of one of the acceptable :attr:`dataClasses` then this method will simply save the data. Otherwise, it will attempt to cast the data into one of the acceptable :attr:`dataClasses` using their :meth:`__save__` mehtod.
        
        :param data: Data, typed like one of the data classes, or data which could initialize one of those classes.
        :param string statename: The label name to use for this data.
        :param bool clobber: Whether to overwrite the destination label or raise an error.
        :raises: :exc:`TypeError` when the data cannot be cast as any dataClass
        :raises: :exc:`KeyError` when the data would overwrite an existing frame.
        
        """
        # If we were passed raw data, and the dataClass can accept it, then go for it!
        if not isinstance(data,tuple(self.dataClasses)):
            Object = None
            for dataClass in self.dataClasses:
                try:
                    Object = dataClass.__save__(data,statename)
                except AbstractError as AE:
                    LOG.log(2,"Cannot save as %s: %s" % (dataClass,AE))
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
            raise KeyError("Cannot Duplicate State Name: \'%s\' Use this.remove(\'%s\') or clobber=True" % (statename,statename))
        elif statename in self.states:
            LOG.log(2,"Overwiting the frame %s" % statename)
        # Save the actual state
        self.states[statename] = Object
        LOG.log(5,"Saved frame %s" % Object)
        # Activate the saved state as the current state
        self.select(statename)
    
    def data(self,statename=None,**kwargs):
        """Returns the raw data for the current state. This is done through the :meth:`FITSFrame.__call__` method, which should return basic data in as raw a form as possible. The purpose of this call is to allow the user get at the most recent piece of data as easily as possible.
        
        :param string statename: the name of the state to be retrieved.
        :param kwargs: arguments to be passed to the data call.
        :returns: np.array of called data
        
        .. Warning::
            I have not finished examining some issues with referencing vs. copying data that comes out of this call. Be aware that manipulating some objects produced here may actually manipulate the version saved in the Object. The current implementation which protects this call relies on the numpy copy command, ``np.copy(state())``, which might fail when used with data objects that do not return numpy arrays.
        """
        # Load the current stat if no state provided
        if not statename:
            statename = self.statename
        if statename != None and statename in self.states:
            return np.copy(self.states[statename](**kwargs))
        else:
            raise KeyError("%s: State %s does not exist" % (self,statename))
    
    def frame(self,statename=None):
        """Returns the FITSFrame Specfied. This method give you the raw frame object to play with, and can be useful for transferring frames around, or if your API is built to work with frames rather than raw data.
        
        :param string statename: the name of the state to be retrieved.
        :returns: dataClass instance for this object
        
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
            raise KeyError("%s: State %s does not exist" % (self,statename))
    
    def object(self,statename=None):
        LOG.log(5,"Method \".object()\" on %s has been depreciated. Please use \".frame()\" instead." % self)
        return self.frame(statename)
        
    def select(self,statename):
        """Sets the default frame to the given statename. Normally, the default frame is the one that was last saved.
        
        :param string statename: the name of the state to be selected.
        
        """
        if statename not in self.states:
            raise IndexError("%s: State %s does not exist" % (self,statename))
        self.statename = statename
        LOG.log(5,"Selected state \'%s\'" % statename)
        return
    
    def list(self):
        """Provides a list of the available frames, by label.
        
        :returns: list
        
        """
        return self.states.keys()
    
    def _default_state(self,states=None):
        """Returns the default state name. If the currently selected state exists, it's state name will return. If not, the system will search for the newest state.
        
        :param tuple states: Tuple of state names from which to select the default. If not given, will use all states.
        :returns: string statename
        
        """
        if states == None:
            states = self.list()
        if self.statename in states:
            return self.statename
        if [] == states:
            return None
        Ages = [ time.clock() - self.frame(name).time for name in states ]
        youngest = states[np.argmin(Ages)]
        return youngest
    
    def clear(self,delete=False):
        """Clears all states from this object. Returns an empty list representing the currently known states.
        
        :param bool delete: whether to explicitly delete states or just stop referencing dictionary.
        :returns: list of states remaining
        
        """
        if delete:
            for state in self.states.keys():
                del self.states[state]
            del self.states
        self.states = {}
        self.statename = self._default_state()
        LOG.log(5,"%s: Cleared all states. Remaining: %s" % (self,self.list()))
        return self.list()
    
    
    def keep(self,*statenames,**kwargs):
        """Removes all states except the specified frame(s) in the object.
        
        :param statenames: the statenames to be kept.
        :param bool delete: whether to explicitly delete stages.
        :returns: list of states remaining.
        
        """
        oldStates = self.states
        newStates = {}
        for statename in statenames:
            if statename not in self.states:
                raise IndexError("%s: State %s does not exist!" % (self,statename))
            newStates[statename] = oldStates[statename]
        LOG.log(5,"%s: Kept states %s" % (self,list(statenames)))
        if "delete" in kwargs and kwargs["delete"]:
            for state in self.states.keys():
                if state not in statenames:
                    del self.states[state]
            del self.states
        self.states = newStates
        self.statename = self._default_state()
        return self.list()
    
    def remove(self,*statenames,**kwargs):
        """Removes the specified frame(s) from the object.
        
        :param statenames: the statenames to be deleted.
        :param bool delete: whether to explicitly delete stages.
        :returns: list of states remaining.
        
        """
        if "clobber" in kwargs and kwargs["clobber"]:
            clobber = True
        else:
            clobber = False
        if "delete" in kwargs and kwargs["delete"]:
            delete = True
        else:
            delete = False
        removed = []
        LOG.log(2,"%s: Requested remove %s" % (self,statenames))
        for statename in statenames:
            if statename not in self.states:
                if clobber:
                    LOG.info("%s: Not removing state %s as it does not exist" % (self,statename))
                else:
                    raise IndexError("%s: Object %s does not exist!" % (self,statename))
            if delete:
                del self.states[statename]
            else:
                self.states.pop(statename)
            removed += [statename]
        self.statename = self._default_state()
        LOG.log(5,"%s: Removed states %s" % (self,removed))
        return self.list()
    
    def show(self,statename=None):
        """Returns the (rendered) matplotlib plot for this object. This is a quick way to view your current data state without doing any serious plotting work. This aims for the sensible defaults philosophy, if you don't like what you get, write a new method that uses the :meth:`data` call and plots that.
        
        :param string statename: the name of the state to be retrieved.
        
        """
        # Load the current stat if no state provided
        if not statename:
            statename = self._default_state()
        if statename != None and statename in self.states:
            return self.states[statename].__show__()
        else:
            raise KeyError("State %s does not exist" % statename)
    
    def write(self,filename=None,states=None,primaryState=None,clobber=False):
        """Writes a FITS file for this object. Generally, the FITS file will include all frames curretnly available in the system. If you specify ``states`` then only those states will be used. ``primaryState`` should be the state of the front HDU. When not specified, the latest state will be used. It uses the :attr:`dataClasses` :meth:`FITSFrame.__hdu__` method to return a valid HDU object for each Frame.
        
        :param string filename: the name of the file for saving.
        :param list states: A list of states to include in the file. If ``None``, save all states.
        :param string primaryState: The state to become the front of the FITS file. If none, uses :meth:`_default_state`
        :param bool clobber: Whether to overwrite the destination file or not.
        
        """
        if not states:
            states = self.list()
            LOG.log(2,"Saving all states: %s" % states)
        if not primaryState:
            primaryState = self._default_state(states)
            LOG.log(2,"Set primary statename to default state %s" % primaryState)
        if primaryState in states:
            states.remove(primaryState)
        if not filename:
            if self.filename == None:
                filename = primaryState
                LOG.log(2,"Set Filename from Primary State. Filename: %s" % filename)
            else:
                filename = self.filename
                LOG.log(2,"Set filename from Object. Filename: %s" % filename)
        filename = validate_filename(filename)
        PrimaryHDU = self.states[primaryState].__hdu__(primary=True)
        if len(states) > 0:
            HDUs = [self.states[state].__hdu__(primary=False) for state in states]
            HDUList = pf.HDUList([PrimaryHDU]+HDUs)
        else:
            HDUList = pf.HDUList([PrimaryHDU])
        HDUList.writeto(filename,clobber=clobber)
        LOG.log(5,"Wrote state %s (primary) and states %s to FITS file %s" % (primaryState,states,filename))
    
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
            LOG.log(2,"Set statename for image from filename: %s" % statename)
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
                    LOG.log(2,"Cannot read as %s: %s" % (dataClass,AE))
                else:
                    break
            if not Object:
                LOG.log(8,"Skipping HDU %s, cannot save as valid type " % HDU)
            else:
                Read += 1
                Labels += [label]
                self.save(Object)
        if not Read:
            msg = "No HDUs were saved from FITS file %s to %s" % (filename,self)
            raise ValueError(msg)
        
        LOG.log(5,"Saved states %s" % Labels)
        return Labels
    
