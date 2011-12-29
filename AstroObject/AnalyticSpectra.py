# 
#  AnalyticSpectra.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.2.8
# 

# Parent Modules
import AstroObjectBase,AstroImage,AstroSpectra

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
import scipy.interpolate

# Standard Python Modules
import math, copy, sys, time, logging, os
import itertools

# Submodules from this system
from Utilities import *

__all__ = ["AnalyticSpectrum","CompositeSpectra","InterpolatedSpectrum"]

LOG = logging.getLogger(__name__)

class AnalyticSpectrum(AstroObjectBase.FITSFrame):
    """A functional spectrum object for spectrum generation. The default implementation is a flat spectrum."""
    def __init__(self,data=None,label=None,wavelengths=None,units=None,**kwargs):
        super(AnalyticSpectrum, self).__init__(data=data,label=label, **kwargs)
        self.wavelengths = wavelengths
        self.units = units #Future will be used for enforcing unit behaviors
        
    
    def __add__(self,other):
        """Implements spectrum addition"""
        return CompositeSpectra(self,other,'add')
        
    
    def __mul__(self,other):
        """Implements spectrum multiplication"""
        return CompositeSpectra(self,other,'mul')
        
    
    def __sub__(self,other):
        """Implements spectrum subtraction"""
        return CompositeSpectra(self,other,'sub')
        
    
    def __rsub__(self,other):
        """Reverse subtraction"""
        return CompositeSpectra(other,self,'sub')
        
    
    def __rmul__(self):
        """Reverse Multiplication"""
        return CompositeSpectra(self,other,'mul')
        
    
    def __radd__(self):
        """Reverse Addition"""
        return CompositeSpectra(self,other,'add')
        
    
    def __call__(self,wavelengths=None,**kwargs):
        """Returns the Flux data for this spectrum"""
        msg = "%s: Cannot Call: Abstract Spectra not instantiated with any properies." % (self)
        raise AbstractError(msg)
    
    def __hdu__(self,primary=False):
        """Returns a pyfits HDU representing this object"""
        msg = "%s: Cannot make HDU: Abstract Spectra not instantiated with any properies." % (self)
        raise AbstractError(msg)
    
    
    @classmethod
    def __save__(cls,data,label):
        """A generic class method for saving to this object with data directly"""
        msg = "%s: Abstract Analytic Structure cannot be the target of a save operation!" % (cls)
        raise AbstractError(msg)
    
    
    @classmethod
    def __read__(cls,HDU,label):
        """An abstract method for reading empty data HDU Frames"""
        LOG.debug("%s: Attempting to read data" % cls)
        msg = "%s: Cannot save HDU as Analytic Spectra" % (cls)
        raise AbstractError(msg)
    


class CompositeSpectra(AnalyticSpectrum):
    """Binary composition of two functional spectra. This object should not be initialized by the user. Instead, this class is returned when you combine two spectra of different types, or combine a spectra with any other type. As such, do not initialze composite spectra idependently. See the :meth:`__call__` function for documentation of how to use this type of object."""
    def __init__(self, partA, partB, operation):
        label = ""
        label += partA.label if hasattr(partA,'label') else str(partA)
        label += " " + operation + " "
        label += partB.label if hasattr(partB,'label') else str(partB)
        super(CompositeSpectra, self).__init__(None,label)
        self.A = partA
        self.B = partB
        self.operation = operation
        
    
    def __call__(self,wavelengths=None,**kwargs):
        """Calls the composite function components. The keyword arguments are passed on to calls to spectra contained within this composite spectra. All spectra varieties should accept arbitrary keywords, so this argument is used to pass keywords to spectra which require specific alternatives."""
        if wavelengths == None:
            wavelengths = self.wavelengths
        if wavelengths == None:
            raise ValueError("No wavelengths specified in %s" % (self))
            
        if isinstance(self.A,AnalyticSpectrum):
            Awavelengths,Avalue = self.A(wavelengths=wavelengths,**kwargs)
        else:
            Avalue = self.A
        if isinstance(self.B,AnalyticSpectrum):
            Bwavelengths,Bvalue = self.B(wavelengths=wavelengths,**kwargs)
        else:
            Bvalue = self.B
        
        if self.operation == 'add':
            Result = Avalue + Bvalue
        elif self.operation == 'mul':
            Result = Avalue * Bvalue
        elif self.operation == 'sub':
            Result = Avalue - Bvalue
        
        if Result != None:
            return np.vstack((wavelengths,Result))
        else:
            raise ValueError("Composition did not produce a value result!")
        
    


class InterpolatedSpectrum(AnalyticSpectrum,AstroSpectra.SpectraFrame):
    """An analytic representation of a generic, specified spectrum"""
    def __init__(self, data=None, label=None, wavelengths=None, **kwargs):
        self.data = data
        self.size = data.size # The size of this image
        self.shape = data.shape # The shape of this image
        super(InterpolatedSpectrum, self).__init__(data=data,label=label,**kwargs)
        x,y = self.data
        self.func = sp.interpolate.interp1d(x,y)
        self.wavelengths = wavelengths
    
    def __call__(self,wavelengths=None,**kwargs):
        """Calls this interpolated spectrum over certain wavelengths"""
        if wavelengths == None:
            wavelengths = self.wavelengths
        return np.vstack((wavelengths,self.func(wavelengths)))
        
class ResampledSpectrum(InterpolatedSpectrum):
    """A spectrum that must be called with resampling information"""
    def __init__(self, data=None, label=None, wavelengths=None, resolution=None, **kwargs):
        super(ResampledSpectrum, self).__init__(data=data,label=label, **kwargs)
        self.wavelengths = wavelengths
        self.resolution = resolution
        
    def __call__(self,wavelengths=None,resolution=None,**kwargs):
        """Calls this resampled spectrum over certain wavelengths"""
        if wavelengths == None:
            wavelengths = self.wavelengths
        if resolution == None:
            resolution = self.resolution
        if wavelengths == None:
            raise ValueError("Requires Wavelenths")
        if resolution == None:
            raise ValueError("Requires Resolution")
        return self.resample(wavelengths,resolution)
        
    def resample(self,wavelengths,resolution,z=0.0):
        """Resample the given spectrum to a lower resolution"""
        
        if resolution.size != wavelengths.size:
            LOG.debug("%s: Wavelength Size: %d, Resolution Size %d" % (self,wavelengths.size,resolution.size))
            raise AttributeError("You must provide resolution appropriate for resampling. Size mismatch!")
        
        oldwl,oldfl = self.data
        oldwl = oldwl * (1.0 + z)
        mintol = wavelengths[0] * resolution[0] / 4
        maxtol = wavelengths[-1] * resolution[-1] / 4
        
        if np.min(oldwl) - mintol > np.min(wavelengths) or np.max(oldwl) + maxtol < np.max(wavelengths):
            msg = "Cannot extrapolate during reampling process. Please provide new wavelengths that are within the range of old ones."
            LOG.critical(msg)
            LOG.debug("%s: %s" % (self,npArrayInfo(wavelengths,"centers")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldwl,"wls")))
            raise ValueError(msg)
        
        oldres = oldwl[:-1] / np.diff(oldwl)
        if np.min(oldres) > np.min(resolution):
            LOG.warning("The new resolution seems to expect more detail than the old one. %g -> %g" % (np.min(oldres),np.min(resolution)))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldres,"given resolution")))
            LOG.debug("%s: %s" % (self,npArrayInfo(resolution,"requested resoluton")))
        
        ones = np.ones(oldwl.shape)
        sigma = wavelengths / resolution / 2.35
        curve = lambda wl,center,sig : (1.0/np.sqrt(np.pi * sig ** 2.0 )) * np.exp( - 0.5 * (wl - center) ** 2.0 / (sig ** 2.0) ).astype(np.float)
        MWL,MCENT = np.meshgrid(oldwl,wavelengths)
        MWL,MSIGM = np.meshgrid(oldwl,sigma)
        curves = curve(MWL,MCENT,MSIGM)
        exps =  - 0.5 * (MWL - MCENT) ** 2.0 / (MSIGM ** 2.0)
        base = np.sum(curves * ones, axis=1)
        top = np.sum(curves * oldfl,axis=1)
        zeros = base == np.zeros(base.shape)
        base[zeros] = np.ones(np.sum(zeros))
        top[zeros] = np.zeros(np.sum(zeros))
        
        flux = top  / base
        
        if np.isnan(flux).any():
            msg = "Detected NaN in result of Resampling!"
            LOG.critical("%s: %s" % (self,msg))
            LOG.debug("%s: %s" % (self,npArrayInfo(wavelengths,"centers")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldwl,"wls")))
            LOG.debug("%s: %s" % (self,npArrayInfo(sigma,"sigmas")))
            LOG.debug("%s: %s" % (self,npArrayInfo(exps,"exps")))
            LOG.debug("%s: %s" % (self,npArrayInfo(np.exp(exps),"exps-calc")))
            LOG.debug("%s: %s" % (self,npArrayInfo(curves,"curves")))
            LOG.debug("%s: %s" % (self,npArrayInfo(base,"base")))
            LOG.debug("%s: %s" % (self,npArrayInfo(flux,"flux")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldfl,"oldfl")))
            raise ValueError(msg)
        LOG.debug("%s: %s" % (self,npArrayInfo(flux,"flux")))
        return np.vstack((wavelengths,flux))

import AnalyticSpectraObjects
from AnalyticSpectraObjects import *

__all__ += AnalyticSpectraObjects.__all__
