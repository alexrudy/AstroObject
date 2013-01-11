# -*- coding: utf-8 -*-
# 
#  spectra.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.6.1
# 
"""
:mod:`spectra` — Raw Spectrum Management 
=============================================

An **stack** and **frame** class which can handle raw spectrum data. This module only handles raw spectra. These spectra are simply data held in image-like **frames**. This class allows a spectrum to be consistently read and written to a FITS file, using image rows as data arrays. The spectra functions contained in this module are bland. For more sophisitcated spectral analysis, see the :mod:`anaspec` module, which contians classes which can re-sample a raw spectrum and interpolate correctly across a spectrum to provide an analytic interface to otherwise discrete spectra.

.. warning:: The class implemented here does not yet use a sophisticated enough method for saving FITS header data etc. As such, it will not preserve state names etc. The development of this class should bring it inline with the STSCI spectra classes in the future.

.. inheritance-diagram::
    AstroObject.spectra.SpectraStack
    AstroObject.spectra.SpectraFrame
    :parts: 1

:class:`SpectraStack` – Raw Spectrum **stacks**
-----------------------------------------------

.. autoclass::
    AstroObject.spectra.SpectraStack
    :members:
    :inherited-members:

:class:`SpectraFrame` – Raw Spectrum **frames**
-----------------------------------------------

.. autoclass::
    AstroObject.spectra.SpectraFrame
    :members:
    :special-members:
    :inherited-members:
    

"""

import base, image

# Standard Scipy Toolkits
import numpy as np
import pyfits as pf
import scipy as sp

# Scipy Extras
from scipy import ndimage
from scipy.spatial.distance import cdist
from scipy.linalg import norm

# Standard Python Modules
import os

# Submodules from this system
from . import logging as logging
from .util import getVersion, npArrayInfo
from .util.mpl import expandLim

__all__ = ["SpectraMixin","SpectraFrame","SpectraStack"]

__version__ = getVersion()

LOG = logging.getLogger(__name__)

class SpectraMixin(base.Mixin):
    """Mixin to set the properties of Spectra **frames** and to provide a :meth:`~.base.BaseFrame.__show__` method. Used for any spectrum **frame** which contains raw data."""
    
    _resolution = None

    def __hdu__(self, primary=False):
        """Returns an HDU to represent this frame. If this frame is linear, (see :meth:`x_is_linear`), the output will be an HDU with just the flux, and keyword hearders which describe the wavelength."""
        if not self.x_is_linear():
            return super(SpectraMixin, self).__hdu__(primary)
        CRVAL = self.wavelengths[0]
        CDELT = np.mean(self.dx())
        if primary:
            HDU = pf.PrimaryHDU(self.flux)
        else:
            HDU = pf.ImageHDU(self.flux)
        HDU.update('CRVAL',CRVAL)
        HDU.update('CDELT',CDELT)
    
    @classmethod
    def __read__(cls,HDU,label):
        """Read into this frame type."""
        Object = super(SpectraMixin, cls).__read__(HDU, label)
        if "CRVAL" in HDU.header and "CDELT" in HDU.header:
            CRVAL = HDU.header['CRVAL']
            CDELT = HDU.header['CDELT']
            CRMAX = CRVAL + CDELT * HDU.data.shape[0]
            wavelengths = np.arange(CRVAL,CRMAX,CDELT)
            Object.data = np.vstack((wavelengths,Object.data))
        return Object
        
    
    @property
    def wavelengths(self):
        """Accessor to get the wavelengths from this spectrum"""
        return self.data[0]
        
    @property
    def flux(self):
        """Accessor to get the flux from this spectrum"""
        return self.data[1]
    
    @property
    def resolution(self):
        """Spectral resolution"""
        if hasattr(self,'_resolution') and self._resolution is not None:
            return self._resolution
        from .util.functions import get_resolution
        return get_resolution(self.wavelengths,matched=True)
        
    @resolution.setter
    def resolution(self,values):
        """Set the explicit resolution"""
        if values is None:
            self._resolution = None
            return
        assert values.shape == self.wavelengths.shape
        self._resolution = values

    
    def __info__(self):
        """Return information about this spectrum."""
        return [ self.label, npArrayInfo(self.wavelengths,u"̵λ"), npArrayInfo(self.flux,u"flux"), npArrayInfo(self.resolution,u"R") ]
    
    def __show__(self):
        """Plots the image in this frame using matplotlib's ``imshow`` function. The color map is set to an inverted binary, as is often useful when looking at astronomical images. The figure object is returned, and can be manipulated further.
        
        .. Note::
            This function serves as a quick view of the current state of the frame. It is not intended for robust plotting support, as that can be easily accomplished using ``matplotlib``. Rather, it attempts to do the minimum possible to create an acceptable image for immediate inspection."""
        LOG.log(2,"Plotting %s using matplotlib.pyplot.plot" % self)
        import matplotlib as mpl
        import matplotlib.pyplot as plt

        
        plt.plot(self.wavelengths,self.flux,".-",label=self.label)
        plt.axis(expandLim(plt.axis()))
        plt.gca().ticklabel_format(style="sci",scilimits=(3,3))
        return plt.gca()
     
    def dx(self):
        """x-axis spacing (usually wavelengths, but could be energy etc.)"""
        return np.diff(self.wavelengths)
        
    def dlogx(self, logbase=10):
        """x-axis logarithmix spacing."""
        return np.log(self.wavelengths)/np.log(logbase)
        
    def x_is_linear(self, tol=1e-10):
        """Whether the x-axis is approximately linear"""
        return np.std(self.dx()) < tol
        
    def x_is_log(self, logbase=10, tol=1e-10):
        """Whether the x-axis is approximately logarithmic"""
        return np.std(self.dlogx(logbase = logbase)) < tol
        
    def linearize(self, strict = False):
        """Linearize this spectrum"""
        new_wavelengths = np.linspace(np.min(self.wavelengths),np.max(self.wavelengths),self.wavelengths.size)
        from .util.functions import get_resolution, Resample, cap_resolution, conserve_resolution
        new_resolutions = get_resolution(new_wavelengths)
        if not strict:
            new_resolutions = cap_resolution(self.resolution,new_resolutions)
        elif strict and not conserve_resolution(self.resolution,new_resolutions):
            raise Exception("Resolution not conserved!")
        new_flux = Resample(self.wavelengths,self.flux,new_wavelengths,new_resolutions)
        self.data = np.vstack((new_wavelengths,new_flux))
        
    def logarize(self, strict = False):
        """Apply a logarithmic scale to this spectrum"""
        new_wavelengths = np.logspace(np.log10(np.min(self.wavelengths)),np.log10(np.max(self.wavelengths)),self.wavelengths.size)
        from .util.functions import get_resolution, Resample, cap_resolution, conserve_resolution
        new_resolutions = get_resolution(new_wavelengths)
        if not strict:
            new_resolutions = cap_resolution(self.resolution,new_resolutions)
        elif strict and not conserve_resolution(self.resolution,new_resolutions):
            raise Exception("Resolution not conserved!")
        new_flux = Resample(self.wavelengths,self.flux,new_wavelengths,new_resolutions)
        self.data = np.vstack((new_wavelengths,new_flux))
    

class SpectraFrame(SpectraMixin,base.HDUHeaderMixin,base.BaseFrame):
    """A single frame of a spectrum. This will save the spectrum as an image, with the first row having flux, and second row having the wavelength equivalent. Further rows can accomodate further spectral frames when stored to a FITS image. However, the frame only accepts a single spectrum."""
    def __init__(self, data=None, label=None, header=None, metadata=None, **kwargs):
        self.data = data # The image data
        self.size = data.size # The size of this image
        self.shape = data.shape # The shape of this image
        super(SpectraFrame, self).__init__(label=label, header=header, metadata=metadata, **kwargs)
    
    def __call__(self):
        """Returns the data for this frame, which should be a ``numpy.ndarray``. The first row will be the spectral data, the second row the equivalent wavelength for this spectrum."""
        return self.data
        
    def __valid__(self):
        """Validates this spectrum frame to conform to the required data shape. This function is used to determine if a passed numpy data array appears to be a spectrum. It is essentially a helper function."""
        dimensions = 2
        rows = 2
        assert self.size == self.data.size, "Members of %s appear to be inconsistent!" % self
        assert self.shape == self.data.shape, "Members of %s appear to be inconsistent!" % self
        assert self.data.ndim == dimensions , "Data of %s does not appear to be %d-dimensional! Shape: %s" % (self,dimensions,self.shape)
        assert self.shape[0] == rows, "Spectrum for %s appears to be multi-dimensional, expected %d Shape: %s" % (self,rows,self.shape)        
        return super(SpectraFrame, self).__valid__()
    
    def __hdu__(self,primary=False):
        """Retruns an HDU which represents this frame. HDUs are either ``pyfits.PrimaryHDU`` or ``pyfits.ImageHDU`` depending on the *primary* keyword."""
        if primary:
            LOG.log(5,"Generating a primary HDU for %s" % self)
            HDU = pf.PrimaryHDU(self.data)
        else:
            LOG.log(5,"Generating an image HDU for %s" % self)
            HDU = pf.ImageHDU(self.data)
        return HDU
    
    
    @classmethod
    def __save__(cls,data,label):
        """Attempts to create a :class:`ImageFrame` object from the provided data. This requres some type checking to ensure that the provided data meets the general sense of such an image. If the data does not appear to be correct, this method will raise an :exc:`NotImplementedError` with a message describing why the data did not validate. Generally, this error will be intercepted by the caller, and simply provides an indication that this is not the right class for a particular piece of data.
        
        If the data is saved successfully, this method will return an object of type :class:`ImageFrame`
        
        The validation requires that the data be a type ``numpy.ndarray`` and that the data have 2 and only 2 dimensions. As well, the data should pass the :meth:`validate` method."""
        LOG.log(2,"Attempting to save as %s" % cls)
        dimensions = 2
        if not isinstance(data,np.ndarray):
            msg = "%s cannot handle objects of type %s, must be type %s" % (cls.__name__,type(data),np.ndarray)
            raise NotImplementedError(msg)
        if data.ndim != dimensions:
            LOG.warning("The data appears to be %d dimensional. This object expects %d dimensional data." % (len(data.shape),dimensions))
        try:
            Object = cls(data,label)
        except AssertionError as AE:
            msg = "%s data did not validate: %s" % (cls.__name__,AE)
            raise NotImplementedError(msg)
        LOG.log(2,"Saved %s with size %d" % (Object,Object.size))
        return Object
    
    @classmethod
    def __read__(cls,HDU,label):
        """Attempts to convert a given HDU into an object of type :class:`ImageFrame`. This method is similar to the :meth:`__save__` method, but instead of taking data as input, it takes a full HDU. The use of a full HDU allows this method to check for the correct type of HDU, and to gather header information from the HDU. When reading data from a FITS file, this is the prefered method to initialize a new frame."""
        LOG.log(2,"Attempting to read as %s" % cls)
        if not isinstance(HDU,(pf.ImageHDU,pf.PrimaryHDU)):
            msg = "Must save a PrimaryHDU or ImageHDU to a %s, found %s" % (cls.__name__,type(HDU))
            raise NotImplementedError(msg)
        if not isinstance(HDU.data,np.ndarray):
            msg = "HDU Data must be %s for %s, found data of %s" % (np.ndarray,cls.__name__,type(HDU.data))
            raise NotImplementedError(msg)    
        try:
            Object = cls(HDU.data,label)
        except AssertionError as AE:
            msg = "%s data did not validate: %s" % (cls.__name__,AE)
            raise NotImplementedError(msg)
        LOG.log(2,"Read %s with size %s" % (Object,Object.size))
        return Object
    

    


class SpectraStack(base.BaseStack):
    """This object tracks a number of data frames. This class is a simple subclass of :class:`base.BaseStack` and usese all of the special methods implemented in that base class. This object sets up an image object class which has two special features. First, it uses only the :class:`SpectraFrame` class for data. As well, it accepts an array in the initializer that will be saved immediately."""
    def __init__(self,dataClasses=[SpectraFrame],**kwargs):
        super(SpectraStack, self).__init__(dataClasses=dataClasses,**kwargs)

    def load(self,filename=None,framename=None):
        """Loads spectral data from a data file which contains two columns, one for wavelenght, and one for flux."""
        if not filename:
            filename = self.filename
        if framename == None:
            framename = os.path.basename(filename)
            LOG.log(2,"Set framename for image from filename: %s" % framename)
        if filename.lower().endswith(".fits") or filename.lower().endswith(".fit"):
            self.read(filename,framename)
        else:
            self.save(np.genfromtxt(filename,unpack=True,comments="#"),framename)
            
    def unload(self,filename=None,framename=None,clobber=False):
        """docstring for unload"""
        if not filename:
            filename = self.filename
        if framename == None:
            framename = self.framename
        
        if filename.lower().endswith(".fits") or filename.lower().endswith(".fit"):
            self.write(filename,framename,clobber=clobber)
        else:
            np.savetxt(filename,self.frame(framename).data.T,header="State %s raw data" % framename,comments="#")
        
    
        
        
        


            
