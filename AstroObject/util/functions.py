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

def Resample(old_wavelengths,flux,new_wavelengths,resolution=None):
    """Gaussian resampling of a spectrum"""
    if resolution is None:
        resolution = new_wavelenghts[:-1] / np.diff(new_wavelengths)
        new_wavelengths = new_wavelengths[:-1]
        
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
