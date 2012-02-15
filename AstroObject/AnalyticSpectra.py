# 
#  AnalyticSpectra.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.3.0a2+dep
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
import scipy.integrate

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
        LOG.log(2,"%s: Attempting to read data" % cls)
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
        """Resample the given spectrum to a lower resolution. 
        
        This is a vector-based calculation, and so should be relatively fast. This function contains ZERO for loops, and uses entirely numpy-based vector mathematics. Sanity checks try to keep your input clean. It can also redshift a spectrum by a given z parameter, if that is necessary."""
        
        # Data sanity check
        if resolution.shape != wavelengths.shape:
            LOG.debug("%s: Wavelength Size: %d, Resolution Size %d" % (self,wavelengths.size,resolution.size))
            raise AttributeError("You must provide resolution appropriate for resampling. Size mismatch!")
        
        # Redshifting
        oldwl,oldfl = self.data
        oldwl = oldwl * (1.0 + z)
        
        # Unit sanity check
        if np.min(oldwl) < 1e-12 or np.max(oldwl) > 1e-3:
            msg = "%s: It looks like your defining wavelength units are wrong: "
            LOG.warning(msg % self + npArrayInfo(oldwl,"WL"))
        
        # Tolerance for interpolation is set here:
        tolfrac = 8 # Maximum interpolation is 1/8th of a resolution element.
        mintol = wavelengths[0] * resolution[0] / tolfrac
        maxtol = wavelengths[-1] * resolution[-1] / tolfrac
        
        # Interpolation tolerance check
        # If this fails, it suggests that the requested wavelengths fall outside the data provided. This will result in
        # resampled values, but they are non-physical as the resampled values assume all non-existent data points to be zero
        if np.min(oldwl) - mintol > np.min(wavelengths) or np.max(oldwl) + maxtol < np.max(wavelengths):
            msg = "Cannot extrapolate during reampling process. Please provide new wavelengths that are within the range of old ones."
            LOG.critical(msg)
            LOG.debug("%s: %s" % (self,npArrayInfo(wavelengths,"New Wavelengths")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldwl,"Old Wavelengths")))
            LOG.debug("%s: Tolerance Range for New Wavelengths: [%g,%g]" % (self,mintol,maxtol))
            raise ValueError(msg)
        
        # Resolution Sanity Check
        # The system cannot generate more information than was already there. As such, the new resolution should be worse than the original.
        oldres = oldwl[:-1] / np.diff(oldwl)
        if np.min(oldres) > np.min(resolution):
            LOG.warning("The new resolution seems to expect more detail than the old one. %g -> %g" % (np.min(oldres),np.min(resolution)))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldres,"given resolution")))
            LOG.debug("%s: %s" % (self,npArrayInfo(resolution,"requested resoluton")))
        
        # The main resampling function.
        # A two dimensional grid is used (instead of two for-loops). The grid stretches across wavelength (data), wavelength (requested). The 
        # standard deviation of the blurring gaussian corresponds point-for-point to the requested wavelengths. As such, we will have columns which
        # we can sum to make the new wavelengths, and rows which show the distribution of flux from each old wavelength into each new wavelength.
        sigma = wavelengths / resolution / 2.35
        curve = lambda wl,center,sig : (1.0/np.sqrt(np.pi * sig ** 2.0 )) * np.exp( - 0.5 * (wl - center) ** 2.0 / (sig ** 2.0) ).astype(np.float)
        
        # This is the two dimensional grid for the resampling function.
        MWL,MCENT = np.meshgrid(oldwl,wavelengths)
        MWL,MSIGM = np.meshgrid(oldwl,sigma)
        
        # DO THE MATH!
        curves = curve(MWL,MCENT,MSIGM)
        
        # We then must normalize the light spread across each aperture by the gaussian. This makes sure the blurring gaussian only distributes
        # the amont of flux under each wavelength.
        ones = np.ones(oldwl.shape)
        base = np.sum(curves * ones, axis=1)
        top  = np.sum(curves * oldfl,axis=1)
        
        # If we try to normalize by dividing by zero, we are doing something wrong.
        # Removing these data points should be okay, because they are data points which we calculated to
        # have zero total flux anyways, and so we can ignore them.
        zeros = base == np.zeros(base.shape)
        if np.sum(zeros) > 0:
            LOG.warning("%s: Removed %d zeros from re-weighting." % (self,np.sum(zeros)))
            LOG.debug("%s: %s" % (self,npArrayInfo(base,"Normalization Denominator")))
            LOG.debug("%s: %s" % (self,npArrayInfo(base,"Normalization Numerator")))
        # We don't actually clip those zero data points, we just make them into dumb numbers so that we don't get divide-by-zero errors
        base[zeros] = np.ones(np.sum(zeros))
        top[zeros] = np.zeros(np.sum(zeros))
        
        # Do the actual normalization
        flux = top  / base
        
        # This is our sanity check. Everything we calculated should be a number. If it comes out as nan, then we have done something wrong.
        # In that case, we raise an error after printing information about the whole calculation.
        if np.isnan(flux).any():
            msg = "Detected NaN in result of Resampling!"
            exps =  - 0.5 * (MWL - MCENT) ** 2.0 / (MSIGM ** 2.0)
            LOG.critical("%s: %s" % (self,msg))
            LOG.debug("%s: %s" % (self,npArrayInfo(wavelengths,"New Wavelengths")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldwl,"Old Wavelengths")))
            LOG.debug("%s: %s" % (self,npArrayInfo(sigma,"Resolution Sigmas")))
            LOG.debug("%s: %s" % (self,npArrayInfo(exps,"Exponent Value")))
            LOG.debug("%s: %s" % (self,npArrayInfo(np.exp(exps),"Exponent Evaluated")))
            LOG.debug("%s: %s" % (self,npArrayInfo(curves,"Curve Evaluated")))
            LOG.debug("%s: %s" % (self,npArrayInfo(base,"Normalization Denominator")))
            LOG.debug("%s: %s" % (self,npArrayInfo(flux,"Resulting Flux")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldfl,"Original Flux")))
            raise ValueError(msg)
        
        # We do print fun information about the final calculation regardless.
        LOG.debug("%s: %s" % (self,npArrayInfo(flux,"New Flux")))
        
        # Finally, return the data in a way that makes sense for the just-in-time spectrum calculation objects
        return np.vstack((wavelengths,flux))
        
class FLambdaSpectrum(ResampledSpectrum):
    """A spectrum that must be integrated to get data values."""
    def __init__(self, data=None, label=None, intSteps=150, **kwargs):
        super(ResampledSpectrum, self).__init__(data=data,label=label, **kwargs)
        self.intSteps = intSteps
        
    def __call__(self,wavelengths=None,resolution=None,**kwargs):
        """Calls this FLambda spectrum over certain wavelengths"""
        if wavelengths == None:
            wavelengths = self.wavelengths
        if resolution == None:
            resolution = self.resolution
        if wavelengths == None:
            raise ValueError("Requires Wavelenths")
        if resolution == None:
            raise ValueError("Requires Resolution")
        return self.integrate(wavelengths,resolution)


    def integrate(self,wavelengths,resolution,z=0.0):
        """Performs wavelength-integration for flambda spectra"""
        # Data sanity check
        if resolution.shape != wavelengths.shape:
            LOG.debug("%s: Wavelength Size: %d, Resolution Size %d" % (self,wavelengths.size,resolution.size))
            raise AttributeError("You must provide resolution appropriate for resampling. Size mismatch!")
            
        wlStart = wavelengths
        wlEnd = (wlStart / resolution) + wlStart
        
        if np.allclose(wlStart[1:],wlEnd[:-1]):
            LOG.warning("Resolution doesn't seem to register to pixel positions")
            LOG.debug("%s : %s" % (self,npArrayInfo(wlStart[1:],"Lower Bounds")))
            LOG.debug("%s : %s" % (self,npArrayInfo(wlEnd[:-1],"Upper Bounds")))
        
        flux = np.array([ sp.integrate.quad(self.func,wlS,wlE,limit=self.intSteps)[0] for wlS,wlE in zip(wlStart,wlEnd) ])
        
        return np.vstack((wavelengths,flux))
                
        
        

        

import AnalyticSpectraObjects
from AnalyticSpectraObjects import *

__all__ += AnalyticSpectraObjects.__all__
