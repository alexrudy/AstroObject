# -*- coding: utf-8 -*-
# 
#  AnalyticSpectra.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.3.4
# 
"""
Analytic Spectra and Interpolation :mod:`AnalyticSpectra`
*********************************************************

Objects for manipulating and managing spectra which are inherently analytic (i.e. you want interpolation, or your spectrum to be defined by a single function). The classes provided in this module are *FRAMES* not *OBJECTS*, i.e. they are individual representations of spectra etc.

It is possible to create an AnalyticSpectraObject to hold many spectra. However, such an object might be of limited utility, as it could not be used to write or read data saved in FITS files, as the FITS format is not conducive to storing analytic items.

.. Note::
    This is a solvable problem. I could use FITS header information to store the required values for an analytic spectrum, and then simply store empty images. However, I don't need this capability now, so maybe in a future version.

This module contains a few pre-defined analytic spectra which you can use as examples. See the :mod:`AnalyticSpectraObjects` module.

This module provides basic analytic spectrum capabilites. There is a simple principle at work in this module: Do all calculations as late as possible. As such, most spectra will be defined as basic analytic spectra. However, the use of the :class:`CompositeSpectra` class allows spectra to be used in mathematics::
    
    A = AnalyticSpectrum()
    B = AnaltyicSpectrum()
    C = A + B * 20
    
.. Note::
    I believe that STSCI Python has some spectrum capabilities, and I am researching combining this module to provide adaptors for the STSCI implementation.

.. autoclass::
    AstroObject.AnalyticSpectra.AnalyticSpectrum
    :members:
    :special-members:

.. autoclass::
    AstroObject.AnalyticSpectra.CompositeSpectra
    :members:
    :inherited-members:
    
    .. automethod:: __call__

Expansion Objects
-----------------

These objects expand the concept of an analytic spectrum to be any spectrum which can respond to calls with arbitrary wavelength boundaries. The spectra in the :class:`InterpolatedSpectrum` class rely on a number of potential methods to calculate the desired wavelength values. The public methods for this class are generally the accepted potential resolution methods.

.. autoclass::
    AstroObject.AnalyticSpectra.InterpolatedSpectrum
    :members:
    :inherited-members:
    
    .. automethod:: __call__
    
    .. automethod:: _presanity
    
    .. automethod:: _postsanity

.. autoclass::
    AstroObject.AnalyticSpectra.Resolver
        
    .. automethod:: __call__

    
.. autoclass::
    AstroObject.AnalyticSpectra.UnitarySpectrum
        
    .. automethod:: __call__
    

Analytic Spectrum Objects
-------------------------

These objects actually have spectral functions included.

.. autoclass::
    AstroObject.AnalyticSpectra.BlackBodySpectrum
    :members:
    :inherited-members:
    
    .. automethod:: __call__
    

.. autoclass::
    AstroObject.AnalyticSpectra.GaussianSpectrum
    :members:
    :inherited-members:
    
    .. automethod:: __call__
    

.. autoclass::
    AstroObject.AnalyticSpectra.FlatSpectrum
    :members:
    :inherited-members:
    
    .. automethod:: __call__

"""
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

__all__ = ["AnalyticSpectrum","CompositeSpectra","InterpolatedSpectrum","InterpolatedSpectrumBase"]

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
        
    


class InterpolatedSpectrumBase(AnalyticSpectrum):

    def __init__(self, data=None, label=None, wavelengths=None,resolution=None, method=u"interpolate",integrator='integrate_hist', **kwargs):
        super(InterpolatedSpectrumBase, self).__init__(data=data,label=label,**kwargs)
        self.wavelengths = wavelengths
        self.resolution = resolution
        self.method = getattr(self,method)
        self.default_integrator = integrator
        
        
    
    def __call__(self,method=None,**kwargs):
        """Calls this interpolated spectrum over certain wavelengths. The `method` parameter will default to the one set for the object, and controls the method used to interpret this spectrum. Available methods include all members of :class:`InterpolatedSpectrum` which provide return values (all those documented below)."""
        if method == None:
            method = self.method
        if isinstance(method,str):
            method = getattr(self,method)
        return method(**kwargs)
        
    def _presanity(self,oldwl,oldfl,newwl,newrs=None,extrapolate=False,upsample=False,debug=False,warning=False,error=False,message=False,**kwargs):
        """Sanity checks performed before any specturm operation. `oldwl` and `oldfl` are the given wavelengths and flux for the spectrum. `newwl` and `newrs` are the requested wavelengths and resolution (respectively) for the spectrum. `extrapolate` allows the new wavelengths to extraopolate from the old ones. If not, only operations that appear to interpolate will be allowed. `upsample` allows the operation to get more resolution information than is already present in the spectrum. `warning` and `debug` flip those flags prematurely, to force warning or debug output. `error` should be an error class to be raised by the sanity checks. These keywords allow custom sanity checks to be performed before calling this function. The benefit of this system, is that sanity checks are all run on every operation, allowing the user to examine all of the potenital problems simultaneously, rather than one at a time, as each successive check is run. The arbitrary keywords at the end allow the user to feed a dictionary of array names and arrays to be included in the sanity check output in the case of failure.
        
        Checks include:
        
        - Wavelength Units (between 1e-12 and 1e-3)
        
        - Wavelengths must be montonically increasing
        
        - Given flux should be greater than 0 (Warning)
        
        - Requested Wavelength and Resolution should shape match.
        
        - Given flux and wavelength should shape match.
        
        - Requested resolution should be positive
        
        - If `extrapolate` then the reuqested wavelengths should be within some tolerance of the given wavelengths. If `extrapolate` is false, then the given wavelengths should fit within the bounds of the given wavelengths.
        
        - If `newrs` (Requested resolution) is given, it must not reuqest more information than is already present in the data. The `upsample` keyword disables this effect.
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
        
        # Check that the units of this spectrum look like SI units, inbound and outbound.
        if np.min(oldwl) < 1e-12 or np.max(oldwl) > 1e-3:
            msg += [u"%s: Given λ units appear wrong!"]
            arrays[u"Given λ"] = oldwl
        
        if np.min(newwl) < 1e-12 or np.max(newwl) > 1e-3:
            msg += [u"%s: Requested λ units appear wrong!"]
            arrays[u"Requested λ"] = newwl
        
        # Check that the units of the spectrum are monotonically increasing (inbound and outbound)
        if (np.diff(oldwl) < 0).any():
            msg += [u"Given λ must be monotonically increasing."]
            arrays[u"Given λ"] = oldwl
            error = ValueError
            
        if (np.diff(newwl) < 0).any():
            msg += [u"Requested λ must be monotonically increasing."]
            arrays[u"Requested λ"] = oldwl
            error = ValueError
        
        # Check that we have non-zero, positive flux provided.
        if (oldfl <= 0).any():
            msg += [u"Given flux <= 0 at some point."]
            arrays[u"Given Flux"] = oldfl
        
        # Data shape sanity check
        if newrb and newrs.shape != newwl.shape:
            dmsg += [u"%s: λ shape: %s, R shape: %s" % (self,newwl.shape,newrs.shape)]
            msg += [u"Shape Mismatch between R and λ"]
            error = AttributeError
            
        if oldwl.shape != oldfl.shape:
            dmsg += [u"%s: λ shape: %s, flux shape: %s" % (self,oldwl.shape,oldrs.shape)]
            msg += [u"Shape Mismatch between flux and λ"]
            error = AttributeError
        
        # Check that resolution is nonzero positive.
        if newrb and (np.min(newrs) <= 0).any():
            msg += [u"Requested R is less than zero!"]
            arrays[u"Requested R"] = newrs
            error = AttributeError
            
        
        # Interpolation tolerance check
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
                                        
        if debug:
            arrays[u"Requested λ"] = newwl
            arrays[u"Given λ"] = oldwl
            arrays[u"Given Flux"] = oldfl
            if newrb:
                arrays[u"Requested R"] = newrs
        
        if len(msg) > 0 and not (error or warning):
            debug = True
                      
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
        
            
    def _postsanity(self,oldwl,oldfl,newwl,newfl,newrs=None,extrapolate=False,debug=False,warning=False,error=False,message=None,**kwargs):
        """Sanity checks performed before any specturm operation. `oldwl` and `oldfl` are the given wavelengths and flux for the spectrum. `newwl` and `newfl` are the found wavelengths and flux (respectively) for the spectrum. `newrs` is the requested resolution. `extrapolate` allows the new wavelengths to extraopolate from the old ones. If not, only operations that appear to interpolate will be allowed. `upsample` allows the operation to get more resolution information than is already present in the spectrum. `warning` and `debug` flip those flags prematurely, to force warning or debug output. `error` should be an error class to be raised by the sanity checks. These keywords allow custom sanity checks to be performed before calling this function. The benefit of this system, is that sanity checks are all run on every operation, allowing the user to examine all of the potenital problems simultaneously, rather than one at a time, as each successive check is run. The arbitrary keywords at the end allow the user to feed a dictionary of array names and arrays to be included in the sanity check output in the case of failure.
        
        Checks performed are:
        
        - ``NaN`` not allowed in found flux.
        
        - ``0`` not allowed in more than ``1%%`` of fluxes. (**Warning**)
        
        - If there were no ``0`` s in the old flux, then the new flux should have no ``0`` s (**Warning**)
        
        - Flux and wavelength should have the same shape.
        
        """
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
        
        This interpolator uses the scipy.interpolate.interp1d method to interpolate between data points in the original spectrum. Normally, this method will not allow extrapolation. The keywords `extrapolate` and `fill_value` can be used to trigger extrapolation away from the interpolated values.
        
        Input should be a set of wavelengths requested for the system (in the `wavelengths` keyword). These wavelengths should not exceed the bounds of the given wavelengths for this spectrum (doing so doesn't really make sense for interpolation. See :meth:`polyfit` for a case where this might make sense.). The output will be a data array of wavelengths and fluxes (should be the provided `wavelengths`, and an equivalently shaped array with fluxes.)
        
        .. Warning :: This method does not prevent you from interpolating your spectrum into a higher resolution state. As such, it is possible, when calling interpolate, to increase the resolution of the spectrum, and end up 'creating' information."""
        if wavelengths == None:
            wavelengths = self.wavelengths
        
        LOG.debug(u"Interpolate Starting")
        
        oldwl,oldfl = self.data
        # Sanity Checks for Data
        self._presanity(oldwl,oldfl,wavelengths,extrapolate=extrapolate)
        
        # Interpolation function (invented on the spot!)
        func = sp.interpolate.interp1d(oldwl,oldfl,bounds_error=False,fill_value=fill_value)
        
        # Actually calling the interpolation
        flux = func(wavelengths)
        
        self._postsanity(oldwl,oldfl,wavelengths,flux)
        # We do print fun information about the final calculation regardless.
        LOG.debug(u"%s: %s" % (self,npArrayInfo(flux,"New Flux")))
        LOG.debug(u"Interpolate Finished")
        
        # Finally, return the data in a way that makes sense for the just-in-time spectrum calculation objects
        return np.vstack((wavelengths,flux))
    
    def polyfit(self,wavelengths=None,order=2,**kwargs):
        """Uses a 1d fit to find missing spectrum values.
        
        This method will extrapolate away from the provided data. The function used is a np.poly1d() using an order 2 np.polyfit. By default, this method will allow extrapolation away from the provided wavelengths. The `order` keyword can be used to adjust the polynomial order for this funciton.
        
        Input should be a set of wavelengths requested for the system (in the `wavelengths` keyword). The output will be a data array of wavelengths and fluxes (should be the provided `wavelengths`, and an equivalently shaped array with fluxes.)"""
        if wavelengths == None:
            wavelengths = self.wavelengths
        
        LOG.debug(u"Polyfit Starting")
        
        oldwl,oldfl = self.data
        # Sanity Checks for Data
        self._presanity(oldwl,oldfl,wavelengths,extrapolate=True)
        
        func = np.poly1d(np.polyfit(oldwl,oldfl,order))
        
        flux = func(wavelengths)
        
        self._postsanity(oldwl,oldfl,wavelengths,flux,extrapolate=True)
        # We do print fun information about the final calculation regardless.
        LOG.debug(u"%s: %s" % (self,npArrayInfo(flux,"New Flux")))
        
        # Finally, return the data in a way that makes sense for the just-in-time spectrum calculation objects
        return np.vstack((wavelengths,flux))
    
        
    def resample(self,wavelengths=None,resolution=None,upsample=False,**kwargs):
        """Resample the given spectrum to a different resolution.
        
        Normally, spectra are resolution limited in their sampling. If you want to sample a spectrum at a lower resolution, simply interpolating, or drawing nearest points to your desired wavelength may cause information loss. The resample method convolves the spectrum with a gaussian which has a width appropriate to your desired resolution. This re-distributes the information in the spectrum into neighboring points, preventing the loss of features due to interpolation and sampling errors.
        
        The resample spectrum normally does not allow you to up-sample a spectrum to a higher resolution, as this could lead to errors caused by 'information creation', i.e. your spectrum will appear to show more detail than is possible. Hoever, the system will allow upsampling (useful if you are confident that you will later downsample your spectrum) using the `upsample` keyword.
        
        Input should be a set of wavelengths requested for the system (in the `wavelengths` keyword) and an array of resolutions requested in the `resolutions` keyword. The output will be a data array of wavelengths and fluxes (should be the provided `wavelengths`, and an equivalently shaped array with fluxes.)
        
        .. Note :: If you request more detail than is given in the spectrum, or if you extrapolate on the spectrum, you may encounter parts of the new spectrum that have no data. As the fluxes are normalized, such data segments are set to zero. This will also produce a warning.
        
        This is a vector-based calculation, and so should be relatively fast. This function contains ZERO for loops, and uses entirely numpy-based vector mathematics."""        
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
        topzo = top == np.zeros(base.shape)    
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
        if (topzo.astype(int) < zeros.astype(int)).any():
            self._postsanity(oldwl,oldfl,wavelengths,flux,resolution,error=ValueError,message=u"Normalizing Zero error." % (np.sum(zeros)),**msgarray)
        elif np.sum(zeros) > 0:
            self._postsanity(oldwl,oldfl,wavelengths,flux,resolution,warning=True,message=u"Removed %d zeros from re-weighting." % (np.sum(zeros)),**msgarray)
        else:
            self._postsanity(oldwl,oldfl,wavelengths,flux,resolution,**msgarray)
            
        
        
        # We do print fun information about the final calculation regardless.
        LOG.debug(u"%s: %s" % (self,npArrayInfo(flux,"New Flux")))
        LOG.debug(u"Resample Complete")
                
        # Finally, return the data in a way that makes sense for the just-in-time spectrum calculation objects
        return np.vstack((wavelengths,flux))
    
    
    
    def integrate_hist(self,wavelengths=None,upscale=150,**kwargs):
        """Performs an integration along wavelengths using the trapezoidal approximation.
        
        The integrator uses a trapezoidal approximation, upscaled to include more data points in each trapezoidal section than the requested wavelengths. The integrator then uses the trapezoid approximation from http://en.wikipedia.org/wiki/Trapezoidal_rule to integrate the spectrum. This results in some integration error, but the integration error is presumably small when compared to the speedup gained over :meth:`integrate_quad`.
        
        Input should be a set of wavelengths requested for the system (in the `wavelengths` keyword). The output will be a data array of wavelengths and fluxes (should be the provided `wavelengths`, and an equivalently shaped array with fluxes.) The `upscale` keyword controls the degree of oversampling for this method.
        
        This calculation is based on the :meth:`interpolate` function and the :func:`np.histogram` function, both of which are not quite vector-fast, but are sufficiently fast for most purposes. This method has been tested to be much faster than :meth:`integrate_quad`
        """
        if wavelengths == None:
            wavelengths = self.wavelengths
        if wavelengths == None:
            raise ValueError(u"Requires Wavelenths")
        
        # Upsample the provided wavelengths
        # This increases the accuracy of the trapezoidal algorithm, as this algorithm is very sensitive to sampling errors.
        if upscale != 1.0:
            startindexs = np.arange(0,wavelengths.size) * upscale
            func = sp.interpolate.interp1d(startindexs,wavelengths)
            findindexs = np.arange(0,np.max(startindexs))
            bins = func(findindexs)
        else:
            bins = wavelengths
        
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
                msg = u"Given λ is undersampled in Requested λ (there is not at least 1 given λ per requested bin)"
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
    
    def integrate_quad(self,wavelengths=None,intSteps=150,**kwargs):
        """Performs an integration along wavelengths using the scipy QUADpack implementation in :func:`scipy.integrate.quad`. 
        
        Input should be a set of wavelengths requested for the system (in the `wavelengths` keyword). The output will be a data array of wavelengths and fluxes (should be the provided `wavelengths`, and an equivalently shaped array with fluxes.)
        
        This integrator uses a generator based for-loop wraped around a call to :func:`scipy.integrate.quad`. On an operation with ~100 elements, this operation can consume close to 20s of computation time. Also, this method must stay strictly within the provided wavelength data. The `intSteps` keyword controls the maximum number of steps in each integration. Turning this value down speeds up the integrator.
        """
        if wavelengths == None:
            wavelengths = self.wavelengths
        if wavelengths == None:
            raise ValueError(u"Requires Wavelenths")
        
        LOG.debug(u"Integration Starting")
        
        
        # Data sanity check
        oldwl,oldfl = self.data
        self._presanity(oldwl,oldfl,wavelengths)
        
        self.func = sp.interpolate.interp1d(oldwl,oldfl,bounds_error=False,fill_value=0)
        
        wlStart = wavelengths[:-1]
        wlEnd = wavelengths[1:]         
        
        flux = np.array([ sp.integrate.quad(self.func,wlS,wlE,limit=intSteps,full_output=1)[0] for wlS,wlE in zip(wlStart,wlEnd) ])
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
        """This method calls a spectrum method, saving and returning the result. The saved data is prepared for the :meth:`resolve_and_integrate` function before being returned. The method also prevents over-resolution sampling.
        
        The resolution provided (`resolution` keyword) are used to request a resampled resolution. However, to prevent information loss, by default (see the `upscaling` keyword) the method automatically prevents the new resolution from exceeding the inherent resolution of the provided data. This allows the system to request a high resolution spectrum, and instead receive the maximum amount of information available at every point.
        """
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
        
                
    def resolve_and_integrate(self,wavelengths,resolution,resolve_method='resample',integration_method='integrate_hist',**kwargs):
        """Resolve a spectrum at a given resolution once, and use that resolved resolution for integration in the future.
        
        The spectrum is first resolved by the :meth:`resolve` function. This provides an appropriately resampled spectrum for use with the integrator. The integrator is then called, and used to get a result. The data from the :meth:`resolve` function is saved for future use.
        
        Input should be a set of wavelengths requested for the system (in the `wavelengths` keyword) and an array of resolutions requested in the `resolutions` keyword. The output will be a data array of wavelengths and fluxes (should be the provided `wavelengths`, and an equivalently shaped array with fluxes.)
        
        .. Note :: The speedup advantage of this method is only beneficial for large data arrays, where the :meth:`resample` function is slow. However, it also allows the use of resample and integrate simultaneously. As such, there is essentially no downside to using this method over a UnitarySpectrum call to insert another interpolation method.
        """
        
        LOG.debug(u"Resolve and Resample Starting")
        if hasattr(self,'resolved'):
            txt = u"Resolved" if self.resolved else "Resolving"
            oldwl,oldfl = self.data
            # Test resolution for current validity:
            bincount,bins = np.histogram(oldwl[:-1],wavelengths)
            if (bincount == 0).any():
                txt = u"Re-resolving"
                self.resolved = False            
            LOG.debug(u"%s: %s" % (self,txt))
        else:
            self.resolved = False
            LOG.debug(u"%s: %s" % (self,"Resolving first"))
        
        # First pass resolving the spectrum to a denser data set.
        # This pass uses the upscaling parameter to find a much denser resolution.
        if not self.resolved:
            self.resolve(wavelengths=wavelengths,resolution=resolution,resolve_method=resolve_method,**kwargs)
        
        self.integrator = getattr(self,integration_method)
        self.data = self.resolved_data
        integrated = self.integrator(wavelengths=wavelengths,resolution=resolution,**kwargs)
        self.data = self.original_data
        return integrated
        

class InterpolatedSpectrum(InterpolatedSpectrumBase,AstroSpectra.SpectraFrame):
    """An analytic representation of a generic, specified spectrum. The spectrum provided will be used to create an infintiely dense interpolation function. This function can then be used to call the spectrum at any wavelength. The interpolation used by default is a simple 1d interpolation.
    
    Passing the name of any member function in this class to the `method` parameter will change the interpolation/method used for this spectrum.
    
    """
    def __init__(self, data=None, label=None,**kwargs):    
        self.data = data
        self.size = data.size # The size of this image
        self.shape = data.shape # The shape of this image
        super(InterpolatedSpectrum, self).__init__(data=data,label=label,**kwargs)

        

class Resolver(InterpolatedSpectrum):
    """This spectrum performs a unitary operation on any InterpolatedSpectrum-type-object. The operation (specified by the `method` keyword) is performed after the contained spectrum is called. The included spectrum is called immediately and then discarded. As such, wavelength and resolution keywords should be provided when appropriate to resolve the spectrum immediately. This operation does not save the old data state. All methods in :class:`InterpolatedSpectrum` are available."""
    def __init__(self, spectrum, label=None, new_method='interpolate',**kwargs):
        data = spectrum(**kwargs)
        if not label:
            label =  u"R[" + spectrum.label + "]"
        super(Resolver, self).__init__(data=data,label=label,method=new_method,**kwargs)
        
        
class UnitarySpectrum(InterpolatedSpectrumBase):
    """This spectrum performs a unitary operation on any InterpolatedSpectrum-type-object. The operation (specified by the `method` keyword) is performed after the contained spectrum is called. All methods in :class:`InterpolatedSpectrum` are available."""
    def __init__(self, spectrum, method='interpolate', label=None,**kwargs):
        if not label:
            label =  u"[" + spectrum.label + "]"
        super(UnitarySpectrum, self).__init__(data=None, label=label,**kwargs)
        self.spectrum = spectrum
        self.method = getattr(self,method)
        
    def __call__(self,old_method=None,method=None,**kwargs):
        """Calls this interpolated spectrum over certain wavelengths. The `method` parameter will default to the one set for the object, and controls the method used to interpret this spectrum. The `old_method` parameter will be used on the contained spectrum. Available methods include all members of :class:`InterpolatedSpectrum` which provide return values (all those documented below)."""
        self.data = self.spectrum(method=old_method,**kwargs)
        return super(UnitarySpectrum, self).__call__(method=method,**kwargs)

                    

import AnalyticSpectraObjects
from AnalyticSpectraObjects import *

__all__ += AnalyticSpectraObjects.__all__
