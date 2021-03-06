# -*- coding: utf-8 -*-
# 
#  base.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.6.1
# 
u"""
.. _AstroObjectAPI:

:mod:`base` – AstroObject API
========================================

The API is the foundation of the :mod:`AstroObject` module. When creating new types of data, you will want to create frames for that type of data. The functions shown below are the functions which must be present in every data frame type, in order to maintain compatibility with enclosing Objects. If your class conforms to this API, then it can easily be used as data for :class:`base.BaseStack`. 


To see how easy this will make objects, examine the following code for a custom Object class which accepts :class:`FooFrame`. To create the custom :class:`base.BaseStack` which accepts your new data type :class:`FooFrame`, simply use::
    
    class FooObject(base.BaseStack):
        \"""A container for tracking FooFrames\"""
        def __init__(self, dataClasses=[FooFrame]):
            super(ImageStack, self).__init__(dataClasses = dataClasses)
            
        
    
This object will then have all of the functions provided by :class:`base.BaseStack`, but will only accept and handle data of type :class:`FooFrame`. :class:`FooFrame` should then implement all of the functions described in the API below.

To use this API, it is recommended that you sub-class :class:`base.BaseFrame`. This template class is an abstract base which will ensure that you implement all of the required methods.

The API also provides a number of Mixin classes for special cases. These mixins allow you to use incomplete, or standard implementations in certain cases. Mixins are useful when your data type cannot possibly conform to the full API provided by :class:`base.BaseFrame`. Examples of this are classes which cannot produce HDUs or FITS files, or classes which do not actually contain raw data. See :ref:`Mixins` for more information.

Module Structure
----------------

The module generally uses **stacks** and **frames** as the base structures. **Stacks** are easily implemented (as above), and **frames** are single data instances which provide all of the required methods from :class:`BaseFrame`. The structure for **Stacks** is quite simple, as there is little variance among different stacks. **Frames** each are required to implement all of the methods in :class:`BaseFrame`, with only a few of those methods implmeneted by default, and most of these require re-implementation.

The Mixin classes are provided to make the creation of certain basic methods easier, and to remove the requirement that other basic methods be implemented. See :ref:`Mixins` for more information.

.. inheritance-diagram::
    AstroObject.fits.FITSFrame
    AstroObject.fits.FITSStack
    AstroObject.image.ImageFrame
    AstroObject.image.ImageStack
    AstroObject.spectra.SpectraFrame
    AstroObject.spectra.SpectraStack
    AstroObject.hdu.HDUFrame
    AstroObject.hdu.HDUStack
    AstroObject.ndarray.NDArrayFrame
    AstroObject.ndarray.NDArrayStack
    AstroObject.anaspec.AnalyticSpectrum
    AstroObject.anaspec.CompositeSpectra
    AstroObject.anaspec.InterpolatedSpectrum
    AstroObject.anaspec.Resolver
    AstroObject.anaspec.UnitarySpectrum
    AstroObject.anaspec.FlatSpectrum
    AstroObject.anaspec.GaussianSpectrum
    AstroObject.anaspec.BlackBodySpectrum
    :parts: 1


:class:`BaseFrame` — Base Frame and Frame API Definition
--------------------------------------------------------

The :class:`BaseFrame` class provides abstract methods for all of the required frame methods. If you subclass from :class:`BaseFrame`, you will ensure that your subclass is interoperable with all of the frame and object features of this module. The :class:`BaseFrame` serves as the primary definition of the API for frames.

.. autoclass:: 
    AstroObject.base.BaseFrame
    :members:
    :special-members:

.. _Mixins:

Mixins in :mod:`base`
--------------------------------

Mixins allow certain classes to operate without all of the features required by :class:`BaseFrame`. Each class below implements certain methods and skips others. 

A summary table is below. The table has classes provided from right to left. Note that :class:`AnalyticMixin` inherits from :class:`NoHDUMixin` and :class:`NoDataMixin`. This means that objects with type :class:`AnalyticMixin` are assumed by the system to be a type of frame, but they do not implement any of the major frame methods.

================================ ==================== ========================= ====================== ===================== ========================================== ======================================
Method                            :class:`BaseFrame`   :class:`HDUHeaderMixin`   :class:`NoDataMixin`   :class:`NoHDUMixin`   :class:`AnalyticMixin`                     :class:`~.spectra.SpectraMixin`
================================ ==================== ========================= ====================== ===================== ========================================== ======================================
Class Inherits From:              :class:`Mixin`        :class:`Mixin`           :class:`Mixin`         :class:`Mixin`        :class:`NoHDUMixin` :class:`NoDataMixin`   :class:`Mixin` 
:meth:`~BaseFrame.__init__`       Implemented           *Abstract*               *Abstract*             *Abstract*            *Abstract*                                 *Abstract*
:meth:`~BaseFrame.__call__`       Abstract                                       Skipped                                      Abstract
:meth:`~BaseFrame.__setheader__`  Abstract              Implemented                                     Skipped               *Skipped*
:meth:`~BaseFrame.__getheader__`  Abstract              Implemented                                     Skipped               *Skipped*
:meth:`~BaseFrame.__getlabel__`   Abstract              Implemented                                     Skipped               *Skipped*                                                  
:meth:`~BaseFrame.__hdu__`        Abstract                                                              Skipped               *Skipped*
:meth:`~BaseFrame.__show__`       Abstract                                       Skipped                                      *Skipped*                                  Implemented
:meth:`~BaseFrame.__save__`       Abstract                                                                                    Skipped
:meth:`~BaseFrame.__read__`       Abstract                                                              Skipped               *Skipped*
================================ ==================== ========================= ====================== ===================== ========================================== ======================================

.. autoclass::
    AstroObject.base.Mixin

.. autoclass::
    AstroObject.base.HDUHeaderMixin
    
.. autoclass::
    AstroObject.base.NoDataMixin
    
.. autoclass::
    AstroObject.base.NoHDUMixin
    
.. autoclass::
    AstroObject.base.AnalyticMixin
    
.. autoclass::
    AstroObject.spectra.SpectraMixin

:class:`BaseStack` — Base Stack and Stack API Definition 
--------------------------------------------------------

The base **stack** definition provides the normal object accessor methods. It should be subclassed as shown in :ref:`AstroObjectAPI`. The API methods defined in this class should be the final methods, and no re-implementation is necessary, so long as the data frames obey the Frame API as defined by :class:`BaseFrame`.

.. autoclass::
    AstroObject.base.BaseStack
    :members:


"""

# Standard Scipy Toolkits
import numpy as np
import pyfits as pf
    
# Standard Python Modules
import logging
import os
import time
import copy
import collections

from abc import ABCMeta, abstractmethod

# Submodules from this system
from .util import getVersion, make_decorator, validate_filename, set_trace_errors
from .file import DefaultFileClasses, File

__all__ = ["BaseStack", "BaseFrame", "AnalyticMixin", "NoHDUMixin", "HDUHeaderMixin", "NoDataMixin", "Mixin"]

__version__ = getVersion()

LOG = logging.getLogger(__name__)

class Mixin(object):
    """ This is an abstract base class for any class which is a Mixin. All such objects should have the appropriate meta-class, and cannot be instantiated unless they havae thier own :meth:`__init__` method.
    
    This prevents Mixin classes from being instantiated as stand-alone entities.
    """
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def __init__(self):
        super(Mixin, self).__init__()


class BaseFrame(Mixin):
    """This is the API for frame objects, that is, objects which represnet a single state of data. See :class:`base.FITSFrame`. This API is generally not called by the end user, but rather is called by the parent :class:`AstroObject.base.BaseStack`'s function. For an example of a parent object, see :class:`base.BaseStack`.
    
    :param data: Initalizing data
    :param label: string label
    :param header: dictionary of header items or pyfits.header
    :param metadata: dictionary of arbitrary metadata
    :raises AttributeError: when the frame fails to validate. See :meth:`__valid__`
    
    """
    
    __metaclass__ = ABCMeta
        
    def __init__(self, data=None, label=None, header=None, metadata=None, **kwargs):
        super(BaseFrame, self).__init__(**kwargs)
        if data != None:
            self.data = data
        self._label = label # A label for this frame, for selection in parent object
        self.header = pf.core.Header() # Header object for HDU header items
        self.metadata = metadata # An optional metadata dictionary
        self.time = time.clock() # An object representing the time this object was created
        self._valid = None
        
        if self.metadata == None:
            self.metadata = {}
        if isinstance(header, pf.core.Header):
            self.header = header
        elif isinstance(header, collections.Mapping):
            for key, value in header.iteritems():
                self.header.update(key, value)
        else:
            assert header == None, u"%s doesn't understand the header, %s, type %s" % (self, header, type(header))
            
        try:
            self.__valid__()
            assert isinstance(self.label, (str, unicode)), u"Frame requires a label, got %s" % self.label
        except AssertionError as err:
            raise AttributeError(unicode(err))
    
    @property
    def label(self):
        """The name for this frame, an immutable property."""
        return self._label
        
    def copy(self, label=None):
        """Return a re-labeled copy of this object."""
        if label == None:
            _new_frame = copy.copy(self)
        else:
            _old_label = self.label
            self._label = label
            _new_frame = copy.copy(self)
            self._label = _old_label
        _new_frame.__valid__()
        return _new_frame
    
    @abstractmethod
    def __call__(self, **kwargs):
        """Should return the data within this frame, usually as a ``numpy`` array.
        
        :returns: The data for this object.
        
        :class:`image.ImageFrame` implements this method as::
            
            def __call__(self):
                return self.data
            
        """
        msg = u"Abstract Data Structure %s was called, but cannot return data!" % self
        raise NotImplementedError(msg)

    def __repr__(self):
        """Returns String Representation of this frame object. Will display the class name and the label. This method does not need to be overwritten by subclasses.
        
        :returns: literal sting representation
        """
        return "<\'%s\' labeled \'%s\'>" % (self.__class__.__name__, self.label)
    
    @abstractmethod
    def __valid__(self):
        """Runs a series of assertions which ensure that the data for this frame is valid
        
        :raises: :exc:`AssertionError` when frame is invalid
        :returns: ``True``"""
        return True
    
    @property
    def valid(self):
        """Whether this object is valid."""
        if self._valid == None:
            try:
                self.__valid__()
            except AssertionError:
                self._valid = False
            else:
                self._valid = True
        return self._valid
    
    def hdu(self, primary=False):
        """Retruns a Header-Data Unit PyFits object. The abstract case generates empty HDUs, which contain no data.
        
        :param bool primary: Return a primary HDU
        :returns: pyfits.primaryHDU or pyfits.ImageHDU
        """
        return self.__setheader__(self.__hdu__(primary))
    
    @abstractmethod
    def __setheader__(self, hdu):
        """Apply header values to a given HDU and return that HDU.
        
        :param pf.HDU HDU: Header-Data-Unit on which to add the header information.
        :returns: HDU with modified header attributes.
        
        """
        msg = u"Abstract Data Structure %s cannot be used for HDU Generation!" % (self)
        raise NotImplementedError(msg)

        
    @abstractmethod
    def __getheader__(self, hdu):
        """Extract header values from a given HDU and save them to this object.
        
        :param pf.HDU HDU: Header-Data-Unit from which to get the header information.
        :returns: *None*
        
        """
        msg = u"Abstract Data Structure %s cannot be used for HDU Generation!" % (self)
        raise NotImplementedError(msg)
    
    @staticmethod
    @abstractmethod
    def __getlabel__(HDU, default=None, explicit=None):
        """Extract header values from a given HDU and save them to this object.
        
        :param pf.HDU HDU: Header-Data-Unit from which to get the header information.
        :param string default: A default value for the label, if no other value can be extracted from the HDU.
        :param string explicit: An explicit value for the label which should normally override any other label option. This label may be manipulated if requried.
        :returns: A string label
        
        """
        msg = u"Abstract Data Structure cannot be used for HDU Header Manipulation!"
        raise NotImplementedError(msg)
    
    
    @abstractmethod
    def __hdu__(self, primary=False):
        """This method returns an HDU which represents the object. The HDU should respect the object's :attr:`header` attribute, and use that dictionary to populate the headers of the HDU. 
        
        :param primary: boolean, produce a primary HDU or not
        :raises: :exc:`NotImplementedError` When the object cannot make a well-formed HDU
        :returns: pyfits.PrimaryHDU or pyfits.HDU
        
        If the frame cannot reasonable generate a :class:`pyFITS.PrimaryHDU`, then it should raise an :exc:`NotImplementedError` in that case."""
        msg = u"Abstract Data Structure %s cannot be used for HDU Generation!" % (self)
        raise NotImplementedError(msg)
    
    @abstractmethod
    def __show__(self):
        """This method should create a simple view of the provided frame. Often this is done using :mod:`Matplotlib.pyplot` to create a simple plot. The plot should have the minimum amount of work done to make a passable plot view, but still be basic enough that the end user can customize the plot object after calling :meth:`__show__`.
        
        :returns: Matplotlib plot object"""
        msg = u"Abstract Data Structure %s cannot be used for plotting!" % (self)
        raise NotImplementedError(msg)
    
    @classmethod
    @abstractmethod    
    def __save__(cls, data, label):
        """This method should retun an instance of the parent class if the given data can be turned into an object of that class. If the data cannot be correctly cast, this method should throw an :exc:`NotImplementedError`.
        
        :param data: Data to be saved, in raw form.
        :param label: Name for the newly created frame.
        :raises: :exc:`NotImplementedError` when this data can't be saved.
        :returns: :class:`BaseFrame`
        
        .. Note:: Because the :meth:`__valid__` is called when an object is initialized, it is possible to check some aspects of the provided data in this initialization function. However, this would raise an :exc:`AssertionError` not an :exc:`NotImplementedError`. To avoid this problem, it is suggested that you wrap your initialization in a try...except block like::
                
                try:
                    Object = cls(HDU.data, label)
                except AssertionError as AE:
                    msg = "%s data did not validate: %s" % (cls.__name__, AE)
                    raise NotImplementedError(msg)
                
            This block simply changes the error type emitted from the __valid__ function. This trick is not a substituion for data validation before initializing the class. Just instantiating a class like this often results in bizzare errors (like :exc:`AttributeError`) which are diffult to track and diagnose without the code in :meth:`__save__`. See :meth:`image.__save__` for an example ``__save__`` function which uses this trick, but also includes some basic data validation."""
        msg = u"Abstract Data Structure %s cannot be the target of a save operation!" % (cls)
        raise NotImplementedError(msg)
        
    
    @classmethod
    @abstractmethod
    def __read__(cls, HDU, label):
        """This method should return an instance of the parent class if the given ``HDU`` can be turned into an object of that class. If this is not possible (i.e. a Table HDU is provided to an Image Frame), this method should raise an :exc:`NotImplementedError` with a message that describes the resaon the data could not be cast into this type of frame.
        
        :param data: HDU to be saved, as a ``pyfits.HDU``.
        :param label: Name for the newly created frame.
        :raises: :exc:`NotImplementedError` when this data can't be saved.
        :returns: :class:`BaseFrame`
        
        .. Note:: Because the :meth:`__valid__` is called when an object is initialized, it is possible to check some aspects of the provided data in this initialization function. However, this would raise an :exc:`AssertionError` not an :exc:`NotImplementedError`. To avoid this problem, it is suggested that you wrap your initialization in a try...except block like::
                
                try:
                    Object = cls(HDU.data, label)
                except AssertionError as AE:
                    msg = "%s data did not validate: %s" % (cls.__name__, AE)
                    raise NotImplementedError(msg)
                
            This block simply changes the error type emitted from the __valid__ function. This trick is not a substituion for data validation before initializing the class. Just instantiating a class like this often results in bizzare errors (like :exc:`AttributeError`) which are diffult to track and diagnose without the code in :meth:`__read__`. See :meth:`image.__read__` for an example ``__read__`` function which uses this trick, but also includes some basic data validation.
            
        .. Note:: It is acceptable to call the class :meth:`__save__` function here. However, the :meth:`__read__` function should also correctly handle header data."""
        msg = u"Abstract Data Structure %s cannot be the target of a read operation!" % (cls)
        raise NotImplementedError(msg)
        

def semiabstractmethod(txt):
    """Convert semi-abstract-methods into raisers for NotImplementedErrors"""
    if callable(txt):
        func = txt
        txt = u"Abstract method %s.%s() cannot be called."
    def decorator(func):
        def raiser(self, *args, **kwargs):
            msg = txt % (self, func.__name__)
            raise NotImplementedError(msg)
        newfunc = make_decorator(func)(raiser)
        return newfunc
    return decorator
        

class HDUHeaderMixin(Mixin):
    """Mixin to provide the default :meth:`~BaseFrame.__setheader__` and :meth:`~BaseFrame.__getheader__` functions. These functions are not provided by default in :class:`BaseFrame`.
    
    :meth:`~BaseFrame.__setheader__` applies the **frame** label to the "label" and "object" keywords, then applies all of the existing keywords to the header.
    
    :meth:`~BaseFrame.__getheader__` retrieves the pyfits HDU for storage in the frame.
    
    :meth:`~BaseFrame.__getlabel__` collects label information from a provided HDU.
    """
    
    def __setheader__(self, HDU):
        """Apply header values to a given HDU and return that HDU.
        
        :param pf.HDU HDU: Header-Data-Unit on which to add the header information.
        :returns: HDU with modified header attributes.
        
        """
        HDU.header.update('label', str(self.label))
        HDU.header.update('object', str(self.label))
        HDU.header.update(self.header)
        return HDU
        
    def __getheader__(self, HDU):
        """Extract header values from a given HDU and save them to this object.
        
        :param pf.HDU HDU: Header-Data-Unit from which to get the header information.
        :returns: *None*
        
        """
        self.header = HDU.header
    
    @staticmethod
    def __getlabel__(HDU, default=None, explicit=None):
        """Extract a label from an HDU, used when no other label is provided."""
        if isinstance(explicit,(str,unicode)):
            return explicit
        if 'label' in HDU.header:
            return HDU.header['label']
        else:
            return default

class NoDataMixin(Mixin):
    """Mixin to allow for frames which **cannot** contain data. This mixin allows the developer to not implement :meth:`~BaseFrame.__call__` and :meth:`~BaseFrame.__show__`, both of which are only sensible methods for actual data.
    
    Due to the validity of empty HDUs, it is possible to have an object which doesn't contain data, but can still produce HDUs.
    """
    
    @semiabstractmethod(u"Cannot call %s.%s() as this frame cannot contain data.")
    def __call__(self):
        """Return data"""
        return None
        
    @semiabstractmethod(u"Cannot call %s.%s() as this frame cannot contain data.")
    def __show__(self):
        """Show no data... NotImplemented"""
        pass
    
    @classmethod    
    @semiabstractmethod(u"Cannot call %s.%s() as this frame cannot contain data.")
    def __save__(cls, data, label):
        """Show no data... NotImplemented"""
        pass
    
        
    def __valid__(self):
        """Require no data"""
        if hasattr(self, 'data'):
            assert self.data == None, u"The frame %s cannot accept data, found data with type %s" % (self, type(self.data))
        return super(NoDataMixin, self).__valid__()

    
        
class NoHDUMixin(Mixin):
    """Mixin to allow for frames which **cannot** produce FITS Header-Data-Units (HDUs) and as such **cannot** produce FITS files.
    
    This mixin allows the developer to not implement :meth:`~BaseFrame.__getheader__`, :meth:`~BaseFrame.__setheader__`, :meth:`~BaseFrame.__hdu__`, and :meth:`~BaseFrame.__read__`.
    """
    
    @semiabstractmethod(u"Cannot call %s.%s() as this frame cannot read HDUs.")
    def __getheader__(self):
        pass
    
    @semiabstractmethod(u"Cannot call %s.%s() as this frame cannot create HDUs.")
    def __setheader__(self):
        pass
        
    @staticmethod
    @semiabstractmethod(u"Cannot call %s.%s() as this frame cannot read HDUs.")
    def __getlabel__(HDU, default=None, explicit=None):
        pass
    
    @semiabstractmethod(u"Cannot call %s.%s() as this frame cannot create HDUs.")
    def __hdu__(self, primary=False):
        pass

    @classmethod    
    @semiabstractmethod(u"Cannot call %s.%s() as this frame cannot read HDUs.")
    def __read__(cls, HDU, label):
        pass


class AnalyticMixin(NoHDUMixin, NoDataMixin):
    """Mixin for purely-analytic frames. These frames do not contain actual raw data, and cannot produce HDUs. However, they are callable (and their call signature should accept a ``wavelengths`` keyword, see e.g. :class:`~.anaspec.FlatSpectrum`).
    
    This mixin allows the developer to not implement :meth:`~BaseFrame.__getheader__`, :meth:`~BaseFrame.__setheader__`, :meth:`~BaseFrame.__hdu__`, :meth:`~BaseFrame.__read__`, :meth:`~BaseFrame.__save__`, and :meth:`~BaseFrame.__show__`. It requires that developers implement :meth:`~BaseFrame.__call__` to access data."""
    
    @abstractmethod
    def __call__(self):
        pass
    
    @classmethod
    @semiabstractmethod(u"Cannot call %s.%s() as this frame cannot be the target of a save operation.")
    def __save__(cls, data, label):
        pass
    

class BaseStack(collections.MutableMapping):
    """This object tracks a number of data frames. The :attr:`Filename` is the default filename to use when reading and writing, and the :attr:`dataClass` argument accepts a list of new data classes to be used with this object. New data classes should conform to the data class standard.
    
    :param filename: String name of default file for reading and writing with :meth:`read` and :meth:`write`.
    :param dataClasses: An array of classes which constitute valid save classes for this object.
    
    *Stacks* have special attribute characteristics which allow them to reach the full *frame* API. *Stacks* can call methods defined within *frames*. Most frames define a :meth:`~BaseFrame.__show__`. This method can be called using :meth:`show` with the following syntax::
            
        >>> Stack.show("SomeFrameName")
            
    The special syntax can take as many framenames as desired as arguments, and will call the named method on each one. So::
            
        >>> Stack.show("FrameA","FrameB","FrameC")
            
    will call the :meth:`~BaseFrame.__show__` method on each frame.
    
    .. Note::
        This is object only contains Abstract data objects. In order to use this class properly, you should set the dataClasses keyword for use when storing data.
    """
    def __init__(self, filename=None, dataClasses=None, fileClasses=DefaultFileClasses, **kwargs):
        super(BaseStack, self).__init__(**kwargs)
        # Image data variables.
        self._frames = {}            # Storage for all of the images
        self._framename = None       # The active frame name
        self.filename = filename     # The filename to use for file loading and writing
        self.clobber = False
        self.name = False
        self._dataClasses = []
        
        if isinstance(dataClasses, list):
            self._dataClasses += dataClasses
        elif dataClasses:
            raise AttributeError(u"Can't understand data classes")
        if len(self._dataClasses) < 1:
            raise NotImplementedError(u"Instantiating %s without any valid data classes!" % self)
        self._fileClasses = []
        if isinstance(fileClasses, list):
            self._fileClasses += fileClasses
        elif fileClasses:
            raise AttributeError(u"Can't understand file classes")
        if len(self._fileClasses) < 1:
            raise NotImplementedError(u"Instantiating %s without any valid file classes!" % self)
        
        canstream = []
        for fileClass in self._fileClasses:
            if not issubclass(fileClass,File):
                raise TypeError("File class %s invalid!" % fileClass)
            if fileClass.__canstream__:
                canstream += [fileClass]
        if len(canstream) == 1:
            self._can_load_stream = True
        else:
            self._can_load_stream = False
        
    def __repr__(self):
        """String representation of this object.
        
        :returns: string
        """
        if self.name:
            return "<\'%s\' labeled \'%s\'>" % (self.__class__.__name__, self.name)
        else:
            return "<\'%s\' with %d frames at \'%s\'>" % (self.__class__.__name__,len(self),hex(id(self)))
    
    def __str__(self):
        """String label for this object."""
        
        return self.__repr__()
    
    def __getitem__(self, key):
        """Dictionary access to frames in the Object"""
        return self.frame(key)
        
    def __setitem__(self, key, value):
        """Dictionary assignment of frames in the Object"""
        self.save(value, key, clobber=True)
        
    def __delitem__(self, key):
        """Dictionary deletion of frames in the Object"""
        self.remove(key)
        
    def __iter__(self):
        """Dictionary iterator call."""
        return self._frames.iterkeys()
        
    def __contains__(self, item):
        """Dictionary contain testing"""
        return item in self._frames
        
    def __len__(self):
        """Dictionary length.
        
        :returns: integer"""
        return len(self._frames.keys())
    
    @property
    def framename(self):
        """Current frame name. This will normally be the last saved **frame**, but there are some exceptions. First, explicitly using :meth:`select` will change the framename. Also, deleting the most recent frame will by default change the selected frame to the second oldest. Using the :meth:`save` function with ``save(data, select=False)`` will skip the selection of that added frame.
        """
        return self._default_frame()
        
    @property
    def framenames(self):
        """Return a list of all framenames in this object."""
        return self.list()
    
    @property
    def d(self):
        """The data for the selected FITS frame. Equivalent to::
            
            >>> Stack.data()
            
        """
        return self.data()
    
    @property
    def f(self):
        """The selected FITS frame. This frame is usually the last modified frame in the system. Equivalent to::
        
            >>> Stack.frame()
            
        
        """
        return self.frame()
    
    def __getattr__(self,name):
        """Provides a passthrough for functions that we haven't named yet.
        
        This allows *stacks* to call methods defined within *frames*. Most frames define a :meth:`~BaseFrame.__show__`. This method can be called using :meth:`show` with the following syntax::
            
            >>> Stack.show("SomeFrameName")
            
        The special syntax can take as many framenames as desired as arguments, and will call the named method on each one. So::
            
            >>> Stack.show("FrameA","FrameB","FrameC")
            
        will call the :meth:`~BaseFrame.__show__` method on each frame.
        
        """
        
        if name.startswith("_"):
            raise AttributeError("%s has no attribute %s." %
             (self.__class__.__name__,name))
        
        def __attr_method(*framenames):
            # Set up frame method name (as string)
            method = '__' + name + '__'
            # Initialize return values
            rvals = []
            
            framenames = list(framenames)
            if len(framenames) < 1:
                framenames = [self._default_frame()]
                
            # Execute the desired method everywhere
            for framename in framenames:
                if framename != None and framename in self:
                    try:
                        rvals += [ getattr(self[framename],method)() ]
                    except AttributeError:
                        raise AttributeError("%s has no attribute %s, and %s has no attribute %s." % 
            (self.__class__.__name__,name,self.f.__class__.__name__,'__'+name+'__'))
                else:
                    self._key_error(framename)
            
            # Return the appropriate value
            if len(rvals) == 1:
                return rvals[0]
            elif len(rvals) == 0:
                return None
            else:
                return tuple(rvals)
                
        return __attr_method
    
    @property
    def data_classes(self):
        """The list of acceptable data classes. This is a"""
        return self._dataClasses
    
    def add_data_class(self,data_class):
        """Insert a data class into the list of acceptable data classes for this object."""
        self._dataClasses += [data_class]
        
    ###############################
    # Basic Object Mode Functions #
    ###############################
    @set_trace_errors(KeyError,TypeError)
    def save(self, data, framename=None, clobber=False, select=True):
        """Saves the given data to this object. If the data is an instance of one of the acceptable :attr:`dataClasses` then this method will simply save the data. Otherwise, it will attempt to cast the data into one of the acceptable :attr:`dataClasses` using their :meth:`__save__` mehtod.
        
        :param data: Data, typed like one of the data classes, or data which could initialize one of those classes.
        :param string framename: The label name to use for this data.
        :param bool clobber: Whether to overwrite the destination label or raise an error.
        :param bool select: Select this frame as the default reading frame.
        :raises: :exc:`TypeError` when the data cannot be cast as any dataClass
        :raises: :exc:`KeyError` when the data would overwrite an existing frame.
        :returns string: Label of the saved frame.
        
        """
        # If we were passed raw data, and the dataClass can accept it, then go for it!
        if not isinstance(data, tuple(self._dataClasses)):
            Object = None
            for dataClass in self._dataClasses:
                try:
                    Object = dataClass.__save__(data, framename)
                except NotImplementedError as AE:
                    LOG.log(2, u"Cannot save as %s: %s" % (dataClass, AE))
                else:
                    break
            if Object is None:
                raise TypeError(u"Object to be saved cannot be cast as %s" % self._dataClasses)
        elif framename is not None:
            Object = data.copy(label=framename)
        else:
            Object = data
            
        if framename == None:
            framename = Object.label
        else:
            assert Object.label == framename, u"Object label improperly set by constructor"
            
        if framename in self and not (clobber or self.clobber):
            raise KeyError(u"Cannot Duplicate State Name: \'%s\' Use this.remove(\'%s\') or clobber=True" % (framename, framename))
        elif framename in self._frames:
            LOG.log(2, u"Overwiting the frame %s" % framename)
        # Save the actual frame
        self._frames[framename] = Object
        LOG.log(5, u"Saved frame %s" % Object)
        # Activate the saved frame as the current frame
        if select:
            self._select(framename)
        return framename
    
    @set_trace_errors(KeyError)
    def data(self, framename=None, **kwargs):
        """Returns the raw data for the current frame. This is done through the :meth:`FITSFrame.__call__` method, which should return basic data in as raw a form as possible. The purpose of this call is to allow the user get at the most recent piece of data as easily as possible.
        
        :param string framename: the name of the frame to be retrieved.
        :param kwargs: arguments to be passed to the data call.
        :returns: np.array of called data
        
        .. Warning::
            I have not finished examining some issues with referencing vs. copying data that comes out of this call. Be aware that manipulating some objects produced here may actually manipulate the version saved in the Object. The current implementation which protects this call relies on the numpy copy command, ``np.copy(frame())``, which might fail when used with data objects that do not return numpy arrays.
        """
        # Load the current stat if no frame provided
        if not framename:
            framename = self.framename
        if framename != None and framename in self:
            return np.copy(self._frames[framename](**kwargs))
        else:
            self._key_error(framename)
    

    @set_trace_errors(KeyError)
    def frame(self, framename=None):
        """Returns the FITSFrame Specfied. This method give you the raw frame object to play with, and can be useful for transferring frames around, or if your API is built to work with frames rather than raw data.
        
        :param string framename: the name of the frame to be retrieved.
        :returns: dataClass instance for this object
        
        .. Warning::
            Unlike with the :meth:`BaseStack.data` call, the object returned here should be treated as roughly immutable. That is, it is not advisable to re-use the data frame here, as Python has returned a reference to all examples of this data frame in your code::
                
                >>> obj = BaseStack()
                >>> obj.save(FITSFrame(None, "Label"))
                >>> Frame = obj.frame()
                >>> Frame.label = "Other"
                >>> obj.frame().label
                "Other"
                
        
        .. Note:: 
            Using frames can be advantageous as you don't rely on the Object to guess what type of frame should be used. Most times, the object will guess correctly, but Frames are a more robust way of ensuring type consistency"""
        if not framename:
            framename = self.framename
        if framename != None and framename in self:
            return self._frames[framename]
        else:
            self._key_error(framename)
    
    def object(self, framename=None):
        LOG.log(5, u"Method \".object()\" on %s has been depreciated. Please use \".frame()\" instead." % self)
        return self.frame(framename)
    
    def _select(self, framename):
        """Private, silent select mode. The parent select() function will issue messages for everything. This one wont."""
        if framename is None:
            self._framename = None # Unselect frame
            framename = self._default_frame()
        elif framename not in self:
            self._key_error(framename)
        self._framename = framename
        return self.framename
    
    @set_trace_errors(KeyError)    
    def select(self, framename):
        """Sets the default frame to the given framename. Normally, the default frame is the one that was last saved.
        
        :param string framename: the name of the frame to be selected.
        
        If ``framename=None``, then this method will select the most recently modified frame.
        
        """
        if framename is None:
            LOG.log(2, u"Setting frame by cancelling selection and asking for default frame.")
        self._select(framename)
        LOG.log(5, u"Selected frame \'%s\'" % self.framename)
        return self.framename
    
    def list(self):
        """Provides a list of the available frames, by label.
        
        :returns: list
        
        """
        return self._frames.keys()
    
    def _key_error(self, framename):
        """Throw a keyError for the given framename."""
        if len(self.list()) < 1:
            msg = u"%s: Stack does not have any frames." % (self)
        else:
            msg = u"%s: Frame %r does not exist. Frames: %s" % (self, framename, self.list())
        raise KeyError(msg)
    
    def _default_frame(self, frames=None):
        """Returns the default frame name. If the currently selected frame exists, it's frame name will return. If not, the system will search for the newest frame. If no frames exist, this function will return None.
        
        :param tuple frames: Tuple of frame names from which to select the default. If not given, will use all frames.
        :returns: string framename
        
        """
        if frames == None:
            frames = self.list()
        if self._framename is not None and self._framename in frames:
            return self._framename
        if [] == frames:
            return None
        Ages = [ time.clock() - self.frame(name).time for name in frames ]
        youngest = frames[np.argmin(Ages)]
        return youngest
    
    def clear(self, delete=False):
        """Clears all frames from this object. Returns an empty list representing the currently known frames.
        
        :param bool delete: whether to explicitly delete frames or just stop referencing dictionary.
        :returns: list of frames remaining
        
        """
        if delete:
            for frame in self._frames.keys():
                del self._frames[frame]
            del self._frames
        self._frames = {}
        self._framename = self._default_frame()
        LOG.log(5, u"%s: Cleared all frames. Remaining: %s" % (self, self.list()))
        return self.list()
    
    @set_trace_errors(KeyError)
    def keep(self, *framenames, **kwargs):
        """Removes all frames except the specified frame(s) in the object.
        
        :param framenames: the framenames to be kept.
        :param bool delete: whether to explicitly delete stages.
        :returns: list of frames remaining.
        
        """
        newStates = {}
        for framename in framenames:
            if framename not in self:
                self._key_error(framename)
            newStates[framename] = self[framename]
        LOG.log(5, u"%s: Kept frames %s" % (self, list(framenames)))
        if kwargs.get('delete', False):
            for frame in self.keys():
                if frame not in framenames:
                    del self._frames[frame]
            del self._frames
        self._frames = newStates
        self._framename = self._default_frame()
        return self.list()
    
    @set_trace_errors(KeyError)
    def remove(self, *framenames, **kwargs):
        """Removes the specified frame(s) from the object.
        
        :param framenames: the framenames to be deleted.
        :param bool delete: whether to explicitly delete stages.
        :returns: list of frames remaining.
        
        """
        removed = []
        LOG.log(2, u"%s: Requested remove %s" % (self, framenames))
        for framename in framenames:
            if framename not in self:
                if kwargs.get('clobber', False):
                    LOG.info(u"%s: Not removing frame %s as it does not exist" % (self, framename))
                else:
                    self._key_error(framename)
            elif kwargs.get('delete', False):
                del self._frames[framename]
            else:
                self._frames.pop(framename)
            removed += [framename]
        self._framename = self._default_frame()
        LOG.log(5, u"%s: Removed frames %s" % (self, removed))
        return self.list()
    
    def _setup_file(self, filename = None, filetype = None):
        """Sets up a file object for reading or writing, given a file-like object and optionally a filetype."""
        if filename is None:
            filename = self.filename
        
        if isinstance(filename,file) and filetype is None and not self._can_load_stream:
            raise TypeError(u"Stack cannot read streams without explicit file type.")
        elif isinstance(filename,file) and filetype is not None:
            if isinstance(filetype,tuple(self._fileClasses)):
                fileClasses = [filetype]
            elif filetype in [ fc.__name__ for fc in self._fileClasses ]:
                fileClasses = [{fc.__name__:fc for fc in self._fileClasses}[filetype]]
            else:
                raise TypeError(u"Cannot understand File Type %r" % filetype)
        elif isinstance(filename,(str,unicode)):
            fileClasses = self._fileClasses
        else:
            raise TypeError(u"Cannot understand filename %r" % filename)    
        
        FileObject = None
        for fileClass in fileClasses:
            try:
                FileObject = fileClass(filename)
            except NotImplementedError as AE:
                LOG.log(2, u"Cannot save as %s: %s" % (fileClass, AE))
            else:
                break
        if FileObject is None:
            raise TypeError(u"Object to be saved cannot be cast as %s" % self._fileClasses)
        return FileObject
        
    
    @set_trace_errors(TypeError)
    def write(self, filename=None, frames=None, primaryFrame=None, clobber=False, singleFrame=False, filetype = None):
        """Writes a FITS file for this object. Generally, the FITS file will include all frames curretnly available in the system. If you specify ``frames`` then only those frames will be used. ``primaryFrame`` should be the frame of the front HDU. When not specified, the latest frame will be used. It uses the :attr:`dataClasses` :meth:`FITSFrame.__hdu__` method to return a valid HDU object for each Frame.
        
        :param string filename: the name of the file for saving.
        :param list frames: A list of frames to include in the file. If ``None``, save all frames.
        :param string primaryFrame: The frame to become the front of the FITS file. If none, uses :meth:`_default_frame`
        :param bool clobber: Whether to overwrite the destination file or not.
        :param bool singleFrame: Whether to save only a single frame.
        :returns: Tuple of (PrimaryFrame, Frames, Filename)
        
        ::  
            >>> obj.write(filename="Test.fits")
            ('MainFrame',['OtherFrame-1','OtherFrame-2'],'Test.fits')
        
        """
        if not frames:
            frames = self.list()
            LOG.log(2, u"Saving all frames: %s" % frames)
        if not primaryFrame:
            primaryFrame = self._default_frame(frames)
            LOG.log(2, u"Set primary framename to default frame %s" % primaryFrame)
        if primaryFrame in frames:
            frames.remove(primaryFrame)
        if singleFrame:
            frames = []
        if not filename:
            if self.filename == None:
                filename = primaryFrame
                LOG.log(2, u"Set Filename from Primary State. Filename: %s" % filename)
        
        # Move the stack trace up one notch
        FileObject = self._setup_file(filename=filename,filetype=filetype)
        
        PrimaryHDU = self[primaryFrame].hdu(primary=True)
        HDUs = [self[frame].hdu(primary=False) for frame in frames]
        HDUList = pf.HDUList([PrimaryHDU]+HDUs)
        FileObject.write(HDUList, clobber=clobber)
        LOG.log(5, u"Wrote frame %s (primary) and frames %s to FITS file %s" % (primaryFrame, frames, filename))
        return primaryFrame, frames, filename

    @set_trace_errors(TypeError,IOError)
    def read(self, filename=None, framename=None, filetype=None, clobber=False, select=True):
        """This reader takes a FITS file, and trys to render each HDU within that FITS file as a frame in this Object. As such, it might read multiple frames. This method will return a list of Frames that it read. It uses the :attr:`dataClasses` :meth:`FITSFrame.__read__` method to return a valid Frame object for each HDU.
        
        :param string|stream filename: The file or filestream to read from. Should be supported by :mod:`~AstroObject.file`.
        :param string framename: The framename to use (overrides the filename-as-framename, but not the 'LABEL' FITS keyword.)
        :param bool clobber: Whether to overwrite existing frames. Default ``False``.
        :param bool select: Whether to make the imported frames the selected ones. Default ``True``.
        
        ::
            
            >>> obj = BaseStack()
            >>> obj.read("SomeImage.fits")
            ["SomeImage", "SomeImage-1", "SomeImage-2"]
            
        """
        FileObject = self._setup_file(filename=filename,filetype=filetype)
        HDUList = FileObject.open()
        Read = 0
        Labels = []
        for HDU in HDUList:    
            Object = None # Target variable
            # Iterate through our potential data classes
            for dataClass in self._dataClasses:
                try:
                    label = dataClass.__getlabel__(HDU,os.path.basename(FileObject.name),framename)
                    if label in Labels:
                        # We don't allow repeat loading of labels
                        label = label + "-%d" % Read
                        LOG.log(2, u"Incrementing label for multi-frame images: %s" % label)
                    label = unicode(label)
                    Object = dataClass.__read__(HDU, label)
                    Object.__getheader__(HDU)
                except NotImplementedError as AE:
                    LOG.log(2, u"Cannot read as %s: %s" % (dataClass, AE))
                else:
                    break
            if Object == None:
                LOG.log(8, u"Skipping HDU %s, cannot save as valid type " % HDU)
            else:
                Read += 1
                Labels += [label]
                self.save(Object, clobber=clobber, select=select)
        if not Read:
            msg = u"No HDUs were saved from FITS file %s to %s" % (filename, self)
            raise ValueError(msg)
        
        LOG.log(5, u"Saved frames %s" % Labels)
        return Labels
    
    def readAtFile(self, atfile, framename=None, clobber=False, select=True):
        """Read an atfile into this object. The name of the atfile can include a starting "@" which is stripped. The file is then loaded, and each line is assumed to contain a single fully-qualified part-name.
        
        :param string atfile: The @file to read from. Filename can start with ``@`` which will be stripped, automatically.
        :param string framename: The framename to use (overrides the filename-as-framename, but not the 'LABEL' FITS keyword.)
        :param bool clobber: Whether to overwrite existing frames. Default ``False``.
        :param bool select: Whether to make the imported frames the selected ones. Default ``True``.
        
        """
        filename = atfile.lstrip("@")
        labels = []
        with open(filename, 'r') as stream:
            for line in stream:
                labels += self.read(line.rstrip(" \n\t"), framename=framename, clobber=clobber, select=select)
        return labels
    
    @classmethod
    def fromAtFile(self, filename, framename=None):
        """Return a new object create from an @file. This method is a factory shortcut for :meth:`readAtFile`.
        
        :param string filename: The @file to be read into the object. Should be supported by :mod:`~AstroObject.file`.
        :param string framename: The framename to use (overrides the filename-as-framename, but not the 'LABEL' FITS keyword.)
        
        """
        Object = cls()
        Object.readAtFile(atfile, framename=framename)
        return Object
      
    @classmethod  
    def fromFile(cls, filename, framename=None):
        """Retrun a new object created from a filename. This method is a shortcut factory for :meth:`read`.
        
        :param string filename: The file to be read into the object. T
        :param string framename: The framename to use (overrides the filename-as-framename, but not the 'LABEL' FITS keyword.)
        
        
        ::
            
            >>> obj = BaseStack.fromFile("SomeImage.fits")
            >>> obj.list()
            ["SomeImage", "SomeImage-1", "SomeImage-2"]
            
        
        """
        Object = cls()
        Object.read(filename, framename=framename)
        return Object

class FrameStack(BaseStack):
    """This stack accepts any type of frame, and overrides data-saving style save methods by calling the BaseFrame save method by default, which will fail because it isn't implemented."""
    def __init__(self):
        super(FrameStack, self).__init__(dataClasses=[BaseFrame])
        
    
        

