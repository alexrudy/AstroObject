# -*- coding: utf-8 -*-
# 
#  AnalyticSpectraObjects.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.4.0
# 

# Parent Modules
import AstroImage,AstroSpectra,AnalyticSpectra,AstroObjectBase

# Standard Scipy Toolkits
import numpy as np
import pyfits as pf
import scipy as sp

# Scipy Extras
from scipy import ndimage
from scipy.spatial.distance import cdist
from scipy.linalg import norm

# Standard Python Modules
import math, copy, sys, time, logging, os

# Submodules from this system
from Utilities import *

__all__ = ["BlackBodySpectrum","GaussianSpectrum","FlatSpectrum"]

__version__ = getVersion()

class BlackBodySpectrum(AstroObjectBase.AnalyticMixin,AnalyticSpectra.AnalyticSpectrum):
    """An analytic representation of a Blackbody Spectrum at a Kelvin Tempertaure.
    
    :param float temperature: The temperature, in Kelvin, of this black body curve.
    
    .. inheritance-diagram::
        AstroObject.AnalyticSpectra.BlackBodySpectrum
        :parts: 1
        
    
    """
    def __init__(self, temperature, label=None, **kwargs):
        if label == None:
            label = "Black Body Spectrum at %4.2eK" % temperature
        super(BlackBodySpectrum, self).__init__(None,label,**kwargs)
        self.temperature = temperature
        
    def __call__(self,wavelengths=None,**kwargs):
        """Calls this blackbody spectrum over certain wavelengths"""
        return np.vstack((wavelengths,BlackBody(wavelengths,self.temperature)))
        
        
class GaussianSpectrum(AstroObjectBase.AnalyticMixin,AnalyticSpectra.AnalyticSpectrum):
    """An analytic representation of a gaussian function in spectral form.
    
    :param float mean: The center of the Gaussian, in wavelength units.
    :param float stdev: The standard deviation of the gaussian, in wavelength units.
    :param float height: The maximum height of the gaussian in flux units.
    
    .. inheritance-diagram::
        AstroObject.AnalyticSpectra.GaussianSpectrum
        :parts: 1
        
    
    """
    def __init__(self, mean, stdev, height, label=None):
        if label == None:
            label = "Gaussian Spectrum with mean: %4.2e and standard deviation: %4.2e" % (mean,stdev)
        super(GaussianSpectrum, self).__init__(None,label)
        self.mean = mean
        self.stdev = stdev
        self.height = height
        
    
    def __call__(self,wavelengths=None,**kwargs):
        """Calls this gaussian spectrum over certain wavelengths"""
        return np.vstack((wavelengths,Gaussian(wavelengths,self.mean,self.stdev,self.height)))
        
    

class FlatSpectrum(AstroObjectBase.AnalyticMixin,AnalyticSpectra.AnalyticSpectrum):
    """An analytc form of a flat value at every wavelength.
    
    :param float value: The height of this flat spectrum, in flux units.
    
    .. inheritance-diagram::
        AstroObject.AnalyticSpectra.FlatSpectrum
        :parts: 1
        
    
    """
    def __init__(self, value, label=None):
        if label == None:
            label = "Flat spectrum with value %3f" % value
        super(FlatSpectrum, self).__init__(None,label)
        self.value = value
        
    def __call__(self,wavelengths,**kwargs):
        """Calls a flat spectrum over given wavelengths"""
        return np.vstack((wavelengths,np.ones(wavelengths.shape)*self.value))
