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

__all__ = [u"AnalyticSpectrum","CompositeSpectra","InterpolatedSpectrum"]

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
            raise ValueError(u"No wavelengths specified in %s" % (self))
            
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
            raise ValueError(u"Composition did not produce a value result!")
        
    


class InterpolatedSpectrum(AnalyticSpectrum,AstroSpectra.SpectraFrame):
    """An analytic representation of a generic, specified spectrum. The spectrum provided will be used to create an infintiely dense interpolation function. This function can then be used to call the spectrum at any wavelength. The interpolation used by default is a simple 1d interpolation.
    
    Passing the name of any member function in this class to the `method` parameter will change the interpolation/method used for this spectrum.
    
    """
    def __init__(self, data=None, label=None, wavelengths=None,resolution=None, intSteps=150, method=u"interpolate",integrator='integrate_hist', **kwargs):
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
        
    def _presanity(self,oldwl,oldfl,newwl,newrs=None,extrapolate=False,debug=False,warning=False,error=False,message=False,upsample=False,**kwargs):
        """Sanity checks performed before any specturm operation.
        
        Controls:
        ------------|--------------------------------
        debug       | show debugging info
        message     | pass a message in
        upsample    | allow the system to upsample
        extrapolate | allow the system to extrapolate
        error       | an error class to raise
        warning     | if true, show a warning
        """
        # Unit sanity check
        msg = []
        if message:
            msg += [message]
        elif error or warning:
            msg += [u"Unkown alert triggered."]
            debug = True
        dmsg = []
        arrays = kwargs
        newrb = True if newrs != None else False
        
        if np.min(oldwl) < 1e-12 or np.max(oldwl) > 1e-3:
            msg += [u"%s: Given λ units appear wrong!"]
            arrays[u"Given λ"] = oldwl
        
        if np.min(newwl) < 1e-12 or np.max(newwl) > 1e-3:
            msg += [u"%s: Requested λ units appear wrong!"]
            arrays[u"Requested λ"] = newwl
        
        if (np.diff(oldwl) < 0).any():
            msg += [u"Given λ must be monotonically increasing."]
            arrays[u"Given λ"] = oldwl
            error = ValueError
            
        if (np.diff(newwl) < 0).any():
            msg += [u"Requested λ must be monotonically increasing."]
            arrays[u"Requested λ"] = oldwl
            error = ValueError
        
        if (oldfl <= 0).any():
            msg += [u"Given flux <= 0 at some point."]
            arrays[u"Given Flux"] = oldfl
            warning = True
        
        # Data shape sanity check
        if newrb and newrs.shape != newwl.shape:
            dmsg += [u"%s: λ shape: %s, R shape: %s" % (self,newwl.shape,newrs.shape)]
            msg += [u"Shape Mismatch between R and λ"]
            error = AttributeError
            
        if oldwl.shape != oldfl.shape:
            dmsg += [u"%s: λ shape: %s, flux shape: %s" % (self,oldwl.shape,oldrs.shape)]
            msg += [u"Shape Mismatch between flux and λ"]
            error = AttributeError
        
        if newrb and (np.min(newrs) <= 0).any():
            msg += [u"Requested R is less than zero!"]
            arrays[u"Requested R"] = newrs
            error = AttributeError
            
        
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
                msg += [u"Should not extrapolate during reampling process. Please provide new λ that are within the range of old ones."]
                warning = True
            else:
                msg += [u"Can not extrapolate during reampling process. Please provide new λ that are within the range of old ones."]
                error = ValueError
            arrays[u"Requested λ"] = newwl
            arrays[u"Given λ"] = oldwl
            dmsg += [u"%s: Allowed range for Requested λ: [%g,%g]" % (self,mintol,maxtol)]
        
        oldrs =  oldwl[:-1] / np.diff(oldwl)
        
        # Resolution Sanity Check
        # The system cannot generate more information than was already there. As such, the new resolution should be worse than the original.
        if newrb:
            if np.max(newrs) > np.min(oldrs):
                oldrsf = sp.interpolate.interp1d(oldwl[:-1],oldrs,bounds_error=False,fill_value=np.min(oldrs))
                oldrsd = oldrsf(newwl)
                delrs = newrs - oldrsd
                if (delrs > 0).any():
                    rswi = np.argmax(delrs)
                    msg += [u"Requested R is more detailed than given R. %g -> %g" % (newrs[rswi],oldrsd[rswi])]
                    arrays[u"Requested R"] = newrs
                    arrays[u"Given R"] = oldrs
                    arrays[u"Given interpolated R"] = oldrsd
                    arrays[u"Given Δλ"] = np.diff(oldwl)
                    arrays[u"Given λ"] = oldwl
                    arrays[u"Difference in R"] = delrs
                    if upsample:
                        debug = True
                    else:
                        error = ValueError
                else:
                    msg += [u"Requested R may be close to same detail as given R. Fidelity might not be preserved."]
                    arrays[u"Requested R"] = newrs
                    arrays[u"Given R"] = oldrs
                    if not upsample:
                        warning = True
                    
        if debug:
            arrays[u"Requested λ"] = newwl
            arrays[u"Given λ"] = oldwl
            arrays[u"Given Flux"] = oldfl
            if newrb:
                arrays[u"Requested R"] = newrs
                      
        if error:
            for m in msg:
                LOG.critical(m)
        elif warning:
            for m in msg:
                LOG.warning(m)
        elif debug:
            LOG.debug(u"Pre Sanity-Check Debugging Information:")
            for m in msg:
                LOG.debug(m)
            
        if error or warning or debug:
            for dm in dmsg:
                LOG.debug(dm)
            for name,array in arrays.iteritems():
                LOG.debug(u"%s: %s" % (self,npArrayInfo(array,name)))
                
        if error:
            raise error(msg[0])
        
            
    def _postsanity(self,oldwl,oldfl,newwl,newfl,newrs=None,debug=False,warning=False,extrapolate=False,error=False,message=None,**kwargs):
        """Post operation sanity checks."""
        msg = []
        dmsg = []
        if message:
            msg += [message]
        elif error or warning:
            msg += [u"Unkown alert triggered."]
            debug = True
        arrays = kwargs
        arrays[u"Requested λ"] = newwl
        arrays[u"Given λ"] = oldwl
        arrays[u"New Flux"] = newfl
        arrays[u"Given Flux"] = oldfl
        newrb = True if newrs != None else False
        if newrb:
            arrays[u"Requested R"] = newrs
                
        if np.isnan(newfl).any():
            msg += [u"Detected NaN in Flux!"]
            error = ValueError
                
        if float(np.sum(newfl <= 0))/float(np.size(newfl)) > 0.01 and (oldfl > 0).all() and not extrapolate:
            msg += [u"New Flux <= 0 for more than 1% of points"]
            warning = True
            
        if newfl.shape != newwl.shape:
            msg += [u"λ lengths have changed: %s -> %s" % (newfl.shape,newwl.shape)]
            error = ValueError
        
        if (newfl <= 0).any() and (oldfl > 0).all():
            msg += [u"New Flux <= 0 some point!"]
            warning = True
        
        if error:
            for m in msg:
                LOG.critical(m)
        elif warning:
            for m in msg:
                LOG.warning(m)
        elif debug:
            LOG.debug(u"Pre Sanity-Check Debugging Information:")
        if error or warning or debug:
            for dm in dmsg:
                LOG.debug(dm)
            for name,array in arrays.iteritems():
                LOG.debug(u"%s: %s" % (self,npArrayInfo(array,name)))                
        if error:
            raise error(msg[0])

        
        
    def interpolate(self,wavelengths=None,extrapolate=False,fill_value=0,**kwargs):
        """Uses a 1d Interpolation to fill in missing spectrum values.
        
        This interpolator uses the scipy.interpolate.interp1d method to interpolate between data points in the original spectrum. Normally, this method will not allow extrapolation. The keywords `extrapolate` and `fill_value` can be used to trigger extrapolation away from the interpolated values."""
        if wavelengths == None:
            wavelengths = self.wavelengths
        
        LOG.debug(u"Interpolate Starting")
        
        
        oldwl,oldfl = self.data
        # Sanity Checks for Data
        self._presanity(oldwl,oldfl,wavelengths,extrapolate=extrapolate)
        
        self.func = sp.interpolate.interp1d(oldwl,oldfl,bounds_error=False,fill_value=fill_value)
        
        flux = self.func(wavelengths)
        
        self._postsanity(oldwl,oldfl,wavelengths,flux)
        # We do print fun information about the final calculation regardless.
        LOG.debug(u"%s: %s" % (self,npArrayInfo(flux,"New Flux")))
        
        # Finally, return the data in a way that makes sense for the just-in-time spectrum calculation objects
        return np.vstack((wavelengths,flux))
    
    def polyfit(self,wavelengths=None,order=2,**kwargs):
        """Uses a 1d fit to find missing spectrum values.
        
        This method will extrapolate away from the provided data. The function used is a np.poly1d() using an order 2 np.polyfit."""
        if wavelengths == None:
            wavelengths = self.wavelengths
        
        
        LOG.debug(u"Polyfit Starting")
        
        oldwl,oldfl = self.data
        # Sanity Checks for Data
        self._presanity(oldwl,oldfl,wavelengths,extrapolate=True)
        
        self.func = np.poly1d(np.polyfit(oldwl,oldfl,order))
        
        flux = self.func(wavelengths)
        
        self._postsanity(oldwl,oldfl,wavelengths,flux,extrapolate=True)
        # We do print fun information about the final calculation regardless.
        LOG.debug(u"%s: %s" % (self,npArrayInfo(flux,"New Flux")))
        
        # Finally, return the data in a way that makes sense for the just-in-time spectrum calculation objects
        return np.vstack((wavelengths,flux))
    
        
    def resample(self,wavelengths=None,resolution=None,z=0.0,upsample=False,**kwargs):
        """Resample the given spectrum to a lower resolution. 
        
        This is a vector-based calculation, and so should be relatively fast. This function contains ZERO for loops, and uses entirely numpy-based vector mathematics. Sanity checks try to keep your input clean. It can also redshift a spectrum by a given z parameter, if that is necessary."""        
        if wavelengths == None:
            wavelengths = self.wavelengths
        if resolution == None:
            resolution = self.resolution
        if wavelengths == None:
            raise ValueError(u"Requires Wavelenths")
        if resolution == None:
            raise ValueError(u"Requires Resolution")
        
        LOG.debug(u"Resample Starting")
        
        
        
        # Redshifting
        oldwl,oldfl = self.data
        oldwl = oldwl * (1.0 + z)
        # Sanity Checks for Data
        self._presanity(oldwl,oldfl,wavelengths,resolution,upsample=upsample)
        
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
        

        msgarray = {
            u"Normalization Denominator" : base,
            u"Normalization Numerator" : top,
            u"Resolution σ" : sigma,
            u"Exponent Value" : (- 0.5 * (MWL - MCENT) ** 2.0 / (MSIGM ** 2.0)),
            u"Exponent Evaluated" : np.exp(- 0.5 * (MWL - MCENT) ** 2.0 / (MSIGM ** 2.0)),
            u"Curve Evaluated" : curves,
        }
        if np.sum(zeros) > 0:
            self._postsanity(oldwl,oldfl,wavelengths,flux,resolution,warning=True,message=u"Removed %d zeros from re-weighting." % (np.sum(zeros)),**msgarray)
        else:
            self._postsanity(oldwl,oldfl,wavelengths,flux,resolution,**msgarray)
            
        
        
        # We do print fun information about the final calculation regardless.
        LOG.debug(u"%s: %s" % (self,npArrayInfo(flux,"New Flux")))
        LOG.debug(u"Resample Complete")
                
        # Finally, return the data in a way that makes sense for the just-in-time spectrum calculation objects
        return np.vstack((wavelengths,flux))
    
    
    
    def integrate_hist(self,wavelengths=None,**kwargs):
        """Performs wavelength-integration for f-lambda spectra using a trapezoidal integrator.
        
        This converts f-lambda spectra into F-lambda spectra, which can then be converted into photon counts. Integration is done with the trapezoid method."""
        if wavelengths == None:
            wavelengths = self.wavelengths
        if wavelengths == None:
            raise ValueError(u"Requires Wavelenths")
        
        upscale = 10
        startindexs = np.arange(0,wavelengths.size) * upscale
        func = sp.interpolate.interp1d(startindexs,wavelengths)
        findindexs = np.arange(0,np.max(startindexs))
        bins = func(findindexs)
        
        # Data sanity check
        oldwl,oldfl = self.interpolate(wavelengths=bins,extrapolate=True,**kwargs)
        LOG.debug(u"Integration Starting")
        
        error = None
        warning = False
        msg = None
        arrays = {}
                
        if (np.diff(bins) <= 0).any():
            msg = u"λ Bins must increase monotonically. [wl + %g]" % (wavelengths[-1]+np.diff(wavelengths)[-1])
            arrays = {u"λ Binsu" : bins, u"Requested λ" : wavelengths ,u"Requested Δλ": wavelengths, u"Bin Δλ" : np.diff(bins),u"λ Offset" : offset }
            error = ValueError
        else:
            bincount,wavelengths = np.histogram(oldwl[:-1],wavelengths)
            if (bincount == 0).any():
                msg = u"Requested λ is poorly represented in given λ"
                arrays = {u"Histogram of λ" : bincount, u"Requested λ" : wavelengths , u"Given λ" : oldwl }
                error = ValueError
            elif (bincount < 2).any():
                msg = u"Bins appear undersampled by given λ"
                arrays = {u"Histogram of λ" : bincount, u"Requested λ" : wavelengths , u"Given λ" : oldwl }
                warning = True
        self._presanity(oldwl,oldfl,wavelengths,error=error,message=msg,warning=warning,extrapolate=True,**arrays)
        
        wlStart = wavelengths[:-1]
        wlEnd = wavelengths[1:]         
        
        w = (oldwl[1:]-oldwl[:-1]) * (oldfl[1:]+oldfl[:-1]) / 2
        
        flux, bins = np.histogram(oldwl[:-1],wavelengths,weights=w)
        flux = np.hstack((flux,flux[-1]))
        
        # This is our sanity check. Everything we calculated should be a number. If it comes out as nan, then we have done something wrong.
        # In that case, we raise an error after printing information about the whole calculation.
        arrays = { u"Requested lower bound λ" : wlStart , u"Requested upper bound λ" : wlEnd }
        self._postsanity(oldwl,oldfl,wavelengths,flux,extrapolate=True,**arrays)
        # We do print fun information about the final calculation regardless.
        LOG.debug(u"%s: %s" % (self,npArrayInfo(flux,"New Flux")))
        LOG.debug(u"Integration Complete")
        
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
            raise ValueError(u"Requires Wavelenths")
        
        LOG.debug(u"Integration Starting")
        
        
        # Data sanity check
        oldwl,oldfl = self.data
        self._presanity(oldwl,oldfl,wavelengths,None)
        
        self.func = sp.interpolate.interp1d(oldwl,oldfl,bounds_error=False,fill_value=0)
        
        wlStart = wavelengths[:-1]
        wlEnd = wavelengths[1:]         
        
        flux = np.array([ sp.integrate.quad(self.func,wlS,wlE,limit=self.intSteps,full_output=1)[0] for wlS,wlE in zip(wlStart,wlEnd) ])
        flux = np.hstack((flux,flux[-1]))
        
        # This is our sanity check. Everything we calculated should be a number. If it comes out as nan, then we have done something wrong.
        # In that case, we raise an error after printing information about the whole calculation.
        arrays = { u"Requested lower bound λu" : wlStart , u"Requested upper bound λ" : wlEnd }
        self._postsanity(oldwl,oldfl,wavelengths,flux,**arrays)

        # We do print fun information about the final calculation regardless.
        LOG.debug(u"%s: %s" % (self,npArrayInfo(flux,"New Flux")))
        LOG.debug(u"Integration Complete")
        
        return np.vstack((wavelengths,flux))
    
    def resolve(self,wavelengths,resolution,resolve_method='resample',upscaling=False,**kwargs):
        """Oversample underlying spectra.
        
        Using the `resolve_method` method (by default :meth:`integrate`), this function gets a high resolution copy of the underlying data. The high resolution data can later be downsampled using the :meth:`resample` method. This is a faster way to access integrated spectra many times. The speed advantages come over the integrator. By default the system gets 100x the requested resolution. This can be tuned with the `upscaling` keyword to optimize between speed and resolution coverage."""
        self.resolver = getattr(self,resolve_method)
        
        newwl = np.copy(wavelengths)
        newrs = np.copy(resolution)
        oldwl,oldfl = self.data
        oldrs =  oldwl[:-1] / np.diff(oldwl)
        
        if not upscaling:        
            upsample = False
            oldrsf = sp.interpolate.interp1d(oldwl[:-1],oldrs,bounds_error=False,fill_value=np.min(oldrs))
            oldrsd = oldrsf(newwl)
            delrs = newrs > oldrsd
            newrs[delrs] = oldrsd[delrs]
        else:
            upsample = True
            
        
        # Save the original data
        self.original_data = self.data
        
        # Do the actual integration, and save it to the object.
        dwl,dfl = self.resolver(wavelengths=newwl,resolution=newrs,upsample=upsample,**kwargs)
        self.resolved_data = np.vstack((dwl,dfl))
        self.resolved = True
        return self.resolved_data
        
                
    def resolve_and_resample(self,wavelengths,resolution,resolve_method='resample',resample_method='integrate_hist',**kwargs):
        """Resolve a spectrum at very high resolution, then re-sample down the proper size.
        
        This method reduces the use of computationally intensive integrators in spectral calculation. The intensive integrator is used only on the first pass over the spectrum. The integrator is called at a higher resolution (normally 100x, controlled by the `upscaling` parameter). This higher resolution copy is saved in the object, and downsampled for each request for spectrum information."""
        
        LOG.debug(u"Resolve and Resample Starting")
        if hasattr(self,'resolved'):
            txt = u"Resolved" if self.resolved else "Resolving"
            oldwl,oldfl = self.data
            # Test resolution for current validity:
            bincount,bins = np.histogram(oldwl[:-1],wavelengths)
            if (bincount == 0).any():
                txt = "Re-resolving"
                self.resolved = False            
            LOG.debug(u"%s: %s" % (self,txt))
        else:
            LOG.debug(u"%s: %s" % (self,"Resolving first"))
        
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
    def __init__(self, spectrum, resolution=10, method='pre_resolve',**kwargs):
        label = u"R[" + spectrum.label + "]"
        data = spectrum(method=method,upscaling=resolution,**kwargs)
        super(UniarySpectrum, self).__init__(data=data, label=label,method='resolve_and_resample',**kwargs)
        self.resolved = True
        self.original_data = spectrum.original_data
        
                    

import AnalyticSpectraObjects
from AnalyticSpectraObjects import *

__all__ += AnalyticSpectraObjects.__all__
