# -*- coding: utf-8 -*-
# 
#  functions.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-05-08.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 
u"""
:mod:`util.functions` — Common Astronomical functons
----------------------------------------------------

.. automethod::
    AstroObject.util.functions.BlackBody
    
.. automethod::
    AstroObject.util.functions.Gaussian
    
.. automethod::
    AstroObject.util.functions.get_resolution
    
.. automethod::
    AstroObject.util.functions.conserve_resolution
    
.. automethod::
    AstroObject.util.functions.cap_resolution
    
.. automethod::
    AstroObject.util.functions.get_resolution_spectrum
    
.. automethod::
    AstroObject.util.functions.Resample


"""
import numpy as np
import scipy as sp
import scipy.constants as spconst

def BlackBody(wl,T):
    """Return black-body flux as a function of wavelength. Usese constants from Scipy Constants, and expects SI units"""
    h = spconst.h
    c = spconst.c
    k = spconst.k
    exponent = (h * c)/(wl * k * T)
    exponential=np.exp(exponent)
    flux = np.nan_to_num((2.0 * h * c**2.0)/(wl**5.0) * (1.0)/(exponential-1.0))
    
    return flux

def Gaussian(x,mean,stdev,height):
    """Rertun a gaussian at postion x, whith mean, stdev, and height"""
    return height*np.exp(-(x-mean)**2.0/(2.0*stdev**2.0))

def get_resolution(wavelengths,matched=True):
    """Return the resolution from a set of wavelengths.
    
    :param wavelengths: an array of wavelengths
    :param bool matched: return resolution elements aligned with wavelengths (return n object. Otherwise, return n-1 objects, for the resolution at the center of each wavelength bin)
    :return: An array of resolutions
    
    """
    wavelengths = np.asarray(wavelengths)
    resolutions = wavelengths[:-1] / np.diff(wavelengths)
    if matched:
        resolutions = np.hstack((resolutions,resolutions[-1]))
    return resolutions
    
def conserve_resolution(given_resolution,target_resolution):
    """Test whether a target resolution is less than a given resolution.
    
    :param given_resolution: the resolution to test against
    :param target_resolution: the resolution for testing
    
    """
    given_interp_f = sp.interpolate.interp1d(np.arange(given_resolution.size),given_resolution,bounds_error=False,fill_value=np.min(given_resolution))
    given_resolution_d = given_interp_f(np.arange(target_resolution.size))
    return not (target_resolution > given_resolution_d).any()
    

def cap_resolution(given_resolution,target_resolution):
    """Cap the target resolution so that it does not exceed the given resolution.
    
    :param given_resolution: The resolution to cap at.
    :param target_resolution: The output resolution, which will be clipped at the interpolated ``given_resolution``.
    
    """
    given_interp_f = sp.interpolate.interp1d(np.arange(given_resolution.size),given_resolution,bounds_error=False,fill_value=np.min(given_resolution))
    given_resolution_d = given_interp_f(np.arange(target_resolution.size))
    delta_resolution = target_resolution > given_resolution_d
    target_resolution[delta_resolution] = given_resolution_d[delta_resolution]
    return target_resolution


def get_resolution_spectrum(minwl,maxwl,resolution):
    """Return a constant resolution spectrum.
    
    :param float minwl: The starting wavelength.
    :param float maxwl: The ending wavelength.
    :param float resolution: The constant resolution
    :returns: Tuple of (wavelegnths, resolutions)
    
    """
        
    dwl = [minwl]
    new_wl = minwl
    while new_wl <= maxwl:
        new_wl += (new_wl / resolution)
        dwl += [new_wl]
            
    dense_wavelengths = np.array(dwl)
    dense_resolution = dense_wavelengths[:-1] / np.diff(dense_wavelengths)
    dense_wavelengths = dense_wavelengths[:-1]
    return dense_wavelengths, dense_resolution 
    
def Resample(old_wavelengths,flux,new_wavelengths,resolution=None):
    """Gaussian resampling of a spectrum.
    
    :param array old_wavelengths: The original wavelength data for resampling.
    :param array flux: The flux of the spectrum at each wavelength.
    :param array new_wavelengths: The requested wavelengths.
    :param array resolution: The requesting resolution (only provided if the requesting resolution should not be determined by the requesting wavelengths.)
    
    """
    if resolution is None:
        resolution = get_resolution(new_wavelengths)
                
    # The main resampling function.
    # A two dimensional grid is used (instead of two for-loops). The grid stretches across wavelength (data), wavelength (requested). The 
    # standard deviation of the blurring gaussian corresponds point-for-point to the requested wavelengths. As such, we will have columns which
    # we can sum to make the new wavelengths, and rows which show the distribution of flux from each old wavelength into each new wavelength.
    sigma = new_wavelengths / resolution / 2.35
    curve = lambda wl,center,sig : (1.0/np.sqrt(np.pi * sig ** 2.0 )) * np.exp( - 0.5 * (wl - center) ** 2.0 / (sig ** 2.0) ).astype(np.float)
        
    # This is the two dimensional grid for the resampling function.
    MWL,MCENT = np.meshgrid(old_wavelengths,new_wavelengths)
    MWL,MSIGM = np.meshgrid(old_wavelengths,sigma)
        
    # DO THE MATH!
    curves = curve(MWL,MCENT,MSIGM)
        
    # We then must normalize the light spread across each aperture by the gaussian. This makes sure the blurring gaussian only distributes
    # the amont of flux under each wavelength.
    ones = np.ones(old_wavelengths.shape)
    base = np.sum(curves * ones, axis=1)
    top  = np.sum(curves * flux,axis=1)
        
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
    
    return flux
