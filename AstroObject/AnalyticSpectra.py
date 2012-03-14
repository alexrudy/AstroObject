# -*- coding: utf-8 -*-
# 
#  AnalyticSpectra.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.3.0
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

class AnalyticSpectrum(AstroObjectBase.BaseFrame):
    """A functional spectrum object for spe ctrum generation. The default implementation is a flat spectrum.
    
    The Analytic spectrum can be provided with a set of wavelengths upon intialization. The `wavelengths` keyword will be stored and used when this spectrum is later called by the system. The `units` keyword is currently unused."""
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
        
    def __div__(self,other):
        """Implements spectrum division"""
        return CompositeSpectra(self,other,'div')
    
    
    def __rsub__(self,other):
        """Reverse subtraction"""
        return CompositeSpectra(other,self,'sub')
        
    def __rdiv__(self,other):
        """Reverse division"""
        return CompositeSpectra(other,self,'div')
    
    def __rmul__(self,other):
        """Reverse Multiplication"""
        return CompositeSpectra(other,self,'mul')
        
    
    def __radd__(self,other):
        """Reverse Addition"""
        return CompositeSpectra(other,self,'add')


class CompositeSpectra(AnalyticSpectrum):
    """Binary composition of two functional spectra. This object should not be initialized by the user. Instead, this class is returned when you combine two spectra of different types, or combine a spectra with any other type. As such, do not initialze composite spectra idependently. See the :meth:`__call__` function for documentation of how to use this type of object."""
    ops = {'sub':"-",'add':"+",'mul':"*",'div':"/"}
    def __init__(self, partA, partB, operation):
        label = "("
        label += partA.label if hasattr(partA,'label') else str(partA)
        label += ") " + self.ops[operation] + " ("
        label += partB.label if hasattr(partB,'label') else str(partB)
        label += ")"
        super(CompositeSpectra, self).__init__(None,label)
        self.A = partA
        self.B = partB
        self.operation = operation
        
    
    def __call__(self,wavelengths=None,**kwargs):
        """Calls the composite function components. The keyword arguments are passed on to calls to spectra contained within this composite spectra. All spectra varieties should accept arbitrary keywords, so this argument is used to pass keywords to spectra which require specific alternatives. Pass in `wavelengths` to use the given wavelengths. If none are passed in, it will look for object-level saved wavelengths, which you can specify simply by setting the `self.wavelengths` parameter on the object."""
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
        elif self.operation == 'div':
            Result = Avalue / Bvalue
        if Result != None:
            return np.vstack((wavelengths,Result))
        else:
            raise ValueError("Composition did not produce a value result!")
        
    


class InterpolatedSpectrum(AnalyticSpectrum,AstroSpectra.SpectraFrame):
    """An analytic representation of a generic, specified spectrum. The spectrum provided will be used to create an infintiely dense interpolation function. This function can then be used to call the spectrum at any wavelength. The interpolation used by default is a simple 1d interpolation.
    
    Passing the name of any member function in this class to the `method` parameter will change the interpolation/method used for this spectrum.
    
    """
    def __init__(self, data=None, label=None, wavelengths=None,resolution=None, intSteps=150, method="interpolate",integrator='integrate_trap', **kwargs):
        self.data = data
        self.size = data.size # The size of this image
        self.shape = data.shape # The shape of this image
        super(InterpolatedSpectrum, self).__init__(data=data,label=label,**kwargs)
        self.wavelengths = wavelengths
        self.resolution = resolution
        self.intSteps = intSteps
        self.method = getattr(self,method)
        self.default_integrator = integrator
        
        
    
    def __call__(self,method=None,**kwargs):
        """Calls this interpolated spectrum over certain wavelengths. The method parameter will default to the one set for the object, and controls the method used to interpret this spectrum."""
        if method == None:
            method = self.method
        if isinstance(method,str):
            method = getattr(self,method)
        return method(**kwargs)
        
    def _presanity(self,oldwl,oldfl,newwl,newrs=None,extrapolate=True,debug=False):
        """Sanity checks performed before any operation"""
        # Unit sanity check
        if np.min(oldwl) < 1e-12 or np.max(oldwl) > 1e-3:
            msg = u"%s: Given λ units appear wrong! "
            LOG.warning(msg % self + npArrayInfo(oldwl,"WL"))
    
        if np.min(newwl) < 1e-12 or np.max(newwl) > 1e-3:
            msg = u"%s: Requested λ units appear wrong! "
            LOG.warning(msg % self + npArrayInfo(oldwl,"WL"))
        
        
        if (np.diff(oldwl) < 0).any():
            msg = u"Given λ must be monotonically increasing."
            LOG.critical(msg)
            LOG.debug("%s: %s" % self,npArrayInfo(oldwl,u"Given λ"))
            raise ValueError(msg)
        
        if (np.diff(newwl) < 0).any():
            msg = u"Requested λ must be monotonically increasing."
            LOG.critical(msg)
            LOG.debug("%s: %s" % self,npArrayInfo(oldwl,u"Requested λ"))
            raise ValueError(msg)
        
        
        # Data shape sanity check
        if newrs!=None and newrs.shape != newwl.shape:
            LOG.debug(u"%s: λ shape: %s, R shape: %s" % (self,newwl.shape,newrs.shape))
            raise AttributeError(u"Shape Mismatch between R and λ")
        if oldwl.shape != oldfl.shape:
            LOG.debug(u"%s: λ shape: %s, flux shape: %s" % (self,oldwl.shape,oldrs.shape))
            raise AttributeError(u"Shape Mismatch between flux and λ")
        
        if newrs!=None and (np.min(newrs) <= 0).any():
            LOG.critical(u"New R is less than zero!")
            LOG.debug("%s: %s" % self,npArrayInfo(newrs,"New R"))
            raise AttributeError(u"New R does not make sense! Less than zero!")
            
        
        # Interpolation tolerance check
        # If this fails, it suggests that the requested wavelengths fall outside the data provided. This will result in
        # resampled values, but they are non-physical as the resampled values assume all non-existent data points to be zero
        if not extrapolate:
            mintol = np.min(oldwl)
            maxtol = np.max(oldwl)
        elif newrs != None:
            # Tolerance for interpolation is set here:
            tolfrac = 2 # Maximum interpolation is 1/8th of a resolution element.
            mintol = np.min(oldwl) - (oldwl[0] / oldwl[0]) / tolfrac
            maxtol = np.max(oldwl) + (oldwl[-1] / oldwl[-1]) / tolfrac
        else:
            tolfrac = 1.001
            mintol = np.min(oldwl) / tolfrac
            maxtol = np.max(oldwl) * tolfrac
        

        if np.min(newwl) < mintol or np.max(newwl) > maxtol:
            if extrapolate:
                msg = u"Should not extrapolate during reampling process. Please provide new λ that are within the range of old ones."
                LOG.warning(msg)
            else:
                msg = u"Can not extrapolate during reampling process. Please provide new λ that are within the range of old ones."
                LOG.critical(msg)
            LOG.debug("%s: %s" % (self,npArrayInfo(newwl,u"Requested λ")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldwl,u"Given λ")))
            LOG.debug(u"%s: Allowed range for Requested λ: [%g,%g]" % (self,mintol,maxtol))
            if not extrapolate:
                raise ValueError(msg)
        
        oldrs =  oldwl[:-1] / np.diff(oldwl)
        
        # Resolution Sanity Check
        # The system cannot generate more information than was already there. As such, the new resolution should be worse than the original.
        if newrs != None:
            
            if np.max(newrs) > np.min(oldrs):
                oldrsf = sp.interpolate.interp1d(oldwl[:-1],oldrs,bounds_error=False,fill_value=np.min(oldrs))
                oldrsd = oldrsf(newwl)
                delrs = newrs - oldrsd
                if (delrs > 0).any():
                    rswi = np.argmax(delrs)
                    LOG.warning("New R is more detailed than old R. %g -> %g" % (newrs[rswi],oldrsd[rswi]))
                    LOG.debug("%s: %s" % (self,npArrayInfo(newrs,"Requested R")))
                    LOG.debug("%s: %s" % (self,npArrayInfo(oldrs,"Given R")))
                    LOG.debug("%s: %s" % (self,npArrayInfo(oldrsd,"Given Dense R")))
                    LOG.debug("%s: %s" % (self,npArrayInfo(np.diff(oldwl),u"Given Δλ")))
                    LOG.debug("%s: %s" % (self,npArrayInfo(oldwl,u"Given λ")))
                    
        if debug:
            LOG.debug("Presanity Debug")
            LOG.debug("%s: %s" % (self,npArrayInfo(oldwl,u"Given λ")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldrs,"Given R")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldfl,"Given Flux")))
            LOG.debug("%s: %s" % (self,npArrayInfo(newwl,u"Requested λ")))
            if newrs != None:
                LOG.debug("%s: %s" % (self,npArrayInfo(newrs,"Requested R")))
            
                
        
    def interpolate(self,wavelengths=None,**kwargs):
        """Uses a 1d Interpolation to fill in missing spectrum values.
        
        This interpolator uses the scipy.interpolate.interp1d method to interpolate between data points in the original spectrum. This method will not handle changes in resolution appropriately."""
        if wavelengths == None:
            wavelengths = self.wavelengths
        
        oldwl,oldfl = self.data
        # Sanity Checks for Data
        self._presanity(oldwl,oldfl,wavelengths,None)
        
        self.func = sp.interpolate.interp1d(oldwl,oldfl,bounds_error=False,fill_value=0)
        
        flux = self.func(wavelengths)
        
        # This is our sanity check. Everything we calculated should be a number. If it comes out as nan, then we have done something wrong.
        # In that case, we raise an error after printing information about the whole calculation.
        if np.isnan(flux).any():
            msg = "Detected NaN in result of Resampling!"
            LOG.critical("%s: %s" % (self,msg))
            LOG.debug("%s: %s" % (self,npArrayInfo(wavelengths,u"Requested λ")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldwl,u"Given λ")))
            LOG.debug("%s: %s" % (self,npArrayInfo(flux,"Resulting Flux")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldfl,"Original Flux")))
            raise ValueError(msg)
            
        # We do print fun information about the final calculation regardless.
        LOG.debug("%s: %s" % (self,npArrayInfo(flux,"New Flux")))
        
        if flux.shape != wavelengths.shape:
            msg = u"λ lengths have changed: %s -> %s" % (oldwl.shape,wavelengths.shape)
            LOG.critical("%s: %s" % (self,msg))
            raise ValueError(msg)
            
        # Finally, return the data in a way that makes sense for the just-in-time spectrum calculation objects
        return np.vstack((wavelengths,flux))
        
    def resample(self,wavelengths=None,resolution=None,z=0.0,**kwargs):
        """Resample the given spectrum to a lower resolution. 
        
        This is a vector-based calculation, and so should be relatively fast. This function contains ZERO for loops, and uses entirely numpy-based vector mathematics. Sanity checks try to keep your input clean. It can also redshift a spectrum by a given z parameter, if that is necessary."""        
        if wavelengths == None:
            wavelengths = self.wavelengths
        if resolution == None:
            resolution = self.resolution
        if wavelengths == None:
            raise ValueError("Requires Wavelenths")
        if resolution == None:
            raise ValueError("Requires Resolution")

        
        # Redshifting
        oldwl,oldfl = self.data
        oldwl = oldwl * (1.0 + z)
        # Sanity Checks for Data
        self._presanity(oldwl,oldfl,wavelengths,resolution)
        
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
            
        # We don't actually clip those zero data points, we just make them into dumb numbers so that we don't get divide-by-zero errors
        base[zeros] = np.ones(np.sum(zeros))
        top[zeros] = np.zeros(np.sum(zeros))
        
        # Do the actual normalization
        flux = top  / base
        if np.sum(zeros) > 0:
            LOG.warning("%s: Removed %d zeros from re-weighting." % (self,np.sum(zeros)))
            exps =  - 0.5 * (MWL - MCENT) ** 2.0 / (MSIGM ** 2.0)
            LOG.debug("%s: %s" % (self,npArrayInfo(base,"Normalization Denominator")))
            LOG.debug("%s: %s" % (self,npArrayInfo(top,"Normalization Numerator")))
            LOG.debug("%s: %s" % (self,npArrayInfo(wavelengths,u"New λ")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldwl,u"Old λ")))
            LOG.debug("%s: %s" % (self,npArrayInfo(sigma,"Resolution σ")))
            LOG.debug("%s: %s" % (self,npArrayInfo(resolution,u"New R")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldwl[:-1]/np.diff(oldwl),u"Old R")))
            LOG.debug("%s: %s" % (self,npArrayInfo(exps,"Exponent value")))
            LOG.debug("%s: %s" % (self,npArrayInfo(np.exp(exps),"Exponent evaluated")))
            LOG.debug("%s: %s" % (self,npArrayInfo(curves,"Curve evaluated")))
            LOG.debug("%s: %s" % (self,npArrayInfo(flux,"Resulting Flux")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldfl,"Original Flux")))
        
        
        # This is our sanity check. Everything we calculated should be a number. If it comes out as nan, then we have done something wrong.
        # In that case, we raise an error after printing information about the whole calculation.
        if np.isnan(flux).any():
            msg = "Detected NaN in result of Resampling!"
            exps =  - 0.5 * (MWL - MCENT) ** 2.0 / (MSIGM ** 2.0)
            LOG.critical("%s: %s" % (self,msg))
            LOG.debug("%s: %s" % (self,npArrayInfo(wavelengths,u"New λ")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldwl,u"Old λ")))
            LOG.debug("%s: %s" % (self,npArrayInfo(sigma,"Resolution σ")))
            LOG.debug("%s: %s" % (self,npArrayInfo(exps,"Exponent value")))
            LOG.debug("%s: %s" % (self,npArrayInfo(np.exp(exps),"Exponent evaluated")))
            LOG.debug("%s: %s" % (self,npArrayInfo(curves,"Curve evaluated")))
            LOG.debug("%s: %s" % (self,npArrayInfo(base,"Normalization Denominator")))
            LOG.debug("%s: %s" % (self,npArrayInfo(flux,"Resulting Flux")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldfl,"Original Flux")))
            raise ValueError(msg)
        
        # We do print fun information about the final calculation regardless.
        LOG.debug("%s: %s" % (self,npArrayInfo(flux,"New Flux")))
        LOG.debug("Resample Complete")
        
        if flux.shape != wavelengths.shape:
            msg = u"λ lengths have changed: %s -> %s" % (oldwl.shape,wavelengths.shape)
            LOG.critical("%s: %s" % (self,msg))
            raise ValueError(msg)
        
        # Finally, return the data in a way that makes sense for the just-in-time spectrum calculation objects
        return np.vstack((wavelengths,flux))
    
    def integrate_trap(self,wavelengths=None,**kwargs):
        """Performs wavelength-integration for f-lambda spectra using a trapezoidal integrator.
        
        This converts f-lambda spectra into F-lambda spectra, which can then be converted into photon counts. Integration is done with the trapezoid method."""
        if wavelengths == None:
            wavelengths = self.wavelengths
        if wavelengths == None:
            raise ValueError("Requires Wavelenths")
        
        LOG.debug("Integration Starting")
        
        
        # Data sanity check
        oldwl,oldfl = self.data
        self._presanity(oldwl,oldfl,wavelengths,None)
        
        bins = np.hstack((wavelengths,wavelengths[-1]+np.diff(wavelengths)[-1]))
        wlStart = wavelengths[:-1]
        wlEnd = wavelengths[1:]         
        
        flux = (oldwl[1:]-oldwl[:-1]) * (oldfl[1:]+oldfl[:-1]) / 2
        
        flux, bins = np.histogram(oldwl[:-1],bins,weights=flux)
        
        # This is our sanity check. Everything we calculated should be a number. If it comes out as nan, then we have done something wrong.
        # In that case, we raise an error after printing information about the whole calculation.
        if np.isnan(flux).any():
            msg = "Detected NaN in result of Resampling!"
            LOG.critical("%s: %s" % (self,msg))
            LOG.debug("%s: %s" % (self,npArrayInfo(wavelengths,u"Requested λ")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldwl,u"Given λ")))
            LOG.debug("%s: %s" % (self,npArrayInfo(wlStart,"Start Wavelengths")))
            LOG.debug("%s: %s" % (self,npArrayInfo(wlEnd,"End Wavelengths")))
            LOG.debug("%s: %s" % (self,npArrayInfo(flux,"Resulting Flux")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldfl,"Original Flux")))
            raise ValueError(msg)
        if (flux == 0).any() and not (oldfl == 0).any():
            msg = "Detected 0 in result of Resampling!"
            LOG.warning("%s: %s" % (self,msg))
            LOG.debug("%s: %s" % (self,npArrayInfo(wavelengths,u"Requested λ")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldwl,u"Given λ")))
            LOG.debug("%s: %s" % (self,npArrayInfo(wlStart,"Start Wavelengths")))
            LOG.debug("%s: %s" % (self,npArrayInfo(wlEnd,"End Wavelengths")))
            LOG.debug("%s: %s" % (self,npArrayInfo(flux,"Resulting Flux")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldfl,"Original Flux")))
            
            
        # We do print fun information about the final calculation regardless.
        LOG.debug("%s: %s" % (self,npArrayInfo(flux,"New Flux")))
        LOG.debug("Integration Complete")
        
        if flux.shape != wavelengths.shape:
            msg = u"λ lengths have changed: %s -> %s" % (oldwl.shape,wavelengths.shape)
            LOG.critical("%s: %s" % (self,msg))
            raise ValueError(msg)
        
        return np.vstack((wavelengths,flux))
    
    def integrate(self,**kwargs):
        """Calls the default integrator."""
        method = getattr(self,self.default_integrator)
        return method(**kwargs)
    
    def integrate_quad(self,wavelengths=None,**kwargs):
        """Performs wavelength-integration for flambda spectra. 
        
        This converts f-lambda spectra into F-lambda spectra, which can then be converted into photon counts. Integration is done with the quad-pack method."""
        if wavelengths == None:
            wavelengths = self.wavelengths
        if wavelengths == None:
            raise ValueError("Requires Wavelenths")
        
        LOG.debug("Integration Starting")
        
        
        # Data sanity check
        oldwl,oldfl = self.data
        self._presanity(oldwl,oldfl,wavelengths,None)
        
        self.func = sp.interpolate.interp1d(oldwl,oldfl,bounds_error=False,fill_value=0)
        
        wlStart = wavelengths[:-1]
        wlEnd = wavelengths[1:]         
        
        flux = np.array([ sp.integrate.quad(self.func,wlS,wlE,limit=self.intSteps,full_output=1)[0] for wlS,wlE in zip(wlStart,wlEnd) ])
        
        
        # This is our sanity check. Everything we calculated should be a number. If it comes out as nan, then we have done something wrong.
        # In that case, we raise an error after printing information about the whole calculation.
        if np.isnan(flux).any():
            msg = "Detected NaN in result of Resampling!"
            LOG.critical("%s: %s" % (self,msg))
            LOG.debug("%s: %s" % (self,npArrayInfo(wavelengths,u"Requested λ")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldwl,u"Given λ")))
            LOG.debug("%s: %s" % (self,npArrayInfo(resolution,"Resolutions")))
            LOG.debug("%s: %s" % (self,npArrayInfo(wlStart,"Start Wavelengths")))
            LOG.debug("%s: %s" % (self,npArrayInfo(wlEnd,"End Wavelengths")))
            LOG.debug("%s: %s" % (self,npArrayInfo(flux,"Resulting Flux")))
            LOG.debug("%s: %s" % (self,npArrayInfo(oldfl,"Original Flux")))
            raise ValueError(msg)
        
        # We do print fun information about the final calculation regardless.
        LOG.debug("%s: %s" % (self,npArrayInfo(flux,"New Flux")))
        LOG.debug("Integration Complete")
        
        return np.vstack((wavelengths[:-1],flux))
    
    def resolve(self,wavelengths,resolution,upscaling=5,resolve_method='resample',**kwargs):
        """Oversample underlying spectra.
        
        Using the `resolve_method` method (by default :meth:`integrate`), this function gets a high resolution copy of the underlying data. The high resolution data can later be downsampled using the :meth:`resample` method. This is a faster way to access integrated spectra many times. The speed advantages come over the integrator. By default the system gets 100x the requested resolution. This can be tuned with the `upscaling` keyword to optimize between speed and resolution coverage."""
        self.resolver = getattr(self,resolve_method)
                
        # Save the original data
        self.original_data = self.data
        
        LOG.debug(npArrayInfo(wavelengths,u"λ"))
        
        oldwl,oldfl = self.data
        oldrs = oldwl[:-1] / np.diff(oldwl)
        densrs = np.ones(oldwl.shape) * np.max(resolution*upscaling)
        denswl = oldwl
        if np.max(resolution) > np.min(oldrs):
            oldrsf = sp.interpolate.interp1d(oldwl[:-1],oldrs,bounds_error=False,fill_value=np.min(oldrs))
            oldrsd = oldrsf(wavelengths)
            delrs = resolution - oldrsd
            if (delrs > 0).any():
                densrs = resolution*upscaling
                denswl = wavelengths
            else:
                LOG.debug("Not actually asking for more resolution! Moving on.")
                LOG.debug("%s: %s" % (self,npArrayInfo(oldrs,"Given R")))
                LOG.debug("%s: %s" % (self,npArrayInfo(resolution,"Requested R")))
                LOG.debug("%s: %s" % (self,npArrayInfo(densrs,"Dense R")))
                LOG.debug("%s: %s" % (self,npArrayInfo(oldwl,u"Given λ")))
                LOG.debug("%s: %s" % (self,npArrayInfo(wavelengths,u"Requested λ")))
        
        
        self._presanity(oldwl,oldfl,wavelengths,resolution*upscaling)        
        
        
        LOG.debug("%s: %s" % (self,npArrayInfo(densrs,"New Dense R")))
        
        # Do the actual integration, and save it to the object.
        dwl,dfl = self.resolver(wavelengths=denswl,resolution=densrs,**kwargs)
        self.resolved_data = np.vstack((dwl,dfl))
        self.resolved = True
        return self.resolved_data
        
                
    def resolve_and_resample(self,wavelengths,resolution,resolve_method='resample',resample_method='integrate_trap',**kwargs):
        """Resolve a spectrum at very high resolution, then re-sample down the proper size.
        
        This method reduces the use of computationally intensive integrators in spectral calculation. The intensive integrator is used only on the first pass over the spectrum. The integrator is called at a higher resolution (normally 100x, controlled by the `upscaling` parameter). This higher resolution copy is saved in the object, and downsampled for each request for spectrum information."""
        
        if hasattr(self,'resolved'):
            txt = "Resolved" if self.resolved else "Resolving"
            LOG.debug("%s: %s" % (self,txt))
        else:
            LOG.debug("%s: %s" % (self,"Resolving first"))
        
        # Set up flag variables.
        self.resolved = False if not hasattr(self,'resolved') else self.resolved
        
        # First pass resolving the spectrum to a denser data set.
        # This pass uses the upscaling parameter to find a much denser resolution.
        if not self.resolved:
            self.resolve(wavelengths=wavelengths,resolution=resolution,resolve_method=resolve_method,**kwargs)
        
        self.resampler = getattr(self,resample_method)
        self.data = self.resolved_data
        resampled = self.resampler(wavelengths=wavelengths,resolution=resolution,**kwargs)
        self.data = self.original_data
        return resampled
        
    def pre_resolve(self,**kwargs):
        """Instead of resolving a spectrum at call time, the spectrum can be called to resolve at creation time. In this case, the resolving method uses the raw data values for wavelengths. This pre-computation serves a similar purpose to :meth:`resolve_and_resample` but can also be used to collapse large collections of spectra. In the case of collapsing large collections (usually the collections are all constructed, but unresolved :class:`CompositeSpectra`), the collapse occurs at construction time, removing computation time from other areas of the program."""        
        oldwl,oldfl = self.data
        
        res = oldwl[:-1] / np.diff(oldwl)
        
        return self.resolve(wavelengths = oldwl[:-1], resolution = res, **kwargs)
        
        
        
        
class UnitarySpectrum(InterpolatedSpectrum):
    """This spectrum calls all contained spectra and resolves them. The resolved spectra are high resolution (using :meth:`pre_resolve` and :meth:`resolve`) and stored for later use. When this spectrum is later called, it will (by default) use :meth:`resolve_and_resample`."""
    def __init__(self, spectrum, resolution=1e2, method='pre_resolve',**kwargs):
        label = "R[" + spectrum.label + "]"
        data = spectrum(method=method,upscaling=resolution,**kwargs)
        super(UniarySpectrum, self).__init__(data=data, label=label,method='resolve_and_resample',**kwargs)
        self.resolved = True
        self.original_data = spectrum.original_data
        
                    

import AnalyticSpectraObjects
from AnalyticSpectraObjects import *

__all__ += AnalyticSpectraObjects.__all__
