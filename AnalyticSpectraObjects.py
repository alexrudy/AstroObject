# 
#  AnalyticSpectraObjects.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 

import AstroImage,AstroSpectra,AnalyticSpectra
from Utilities import *

import matplotlib.pyplot as plt
import matplotlib.image as mpimage
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
from scipy import ndimage
from scipy.spatial.distance import cdist
from scipy.linalg import norm
import numpy as np
import pyfits
import math, copy, sys, time, logging, os

class BlackBodySpectrum(AnalyticSpectra.AnalyticSpectra):
    """An analytic representation of a Blackbody Spectrum at a Kelvin Tempertaure"""
    def __init__(self, temperature, label=None):
        if label == None:
            label = "Black Body Spectrum at %4.2eK" % temperature
        super(BlackBodySpectrum, self).__init__(label)
        self.temperature = temperature
        
    def __call__(self,wavelength):
        """Calls this blackbody spectrum over certain wavelengths"""
        return BlackBody(wavelength,self.temperature)
        
        
class GaussianSpectrum(AnalyticSpectra.AnalyticSpectra):
    """docstring for GaussianSpectrum"""
    def __init__(self, mean, stdev, label=None):
        if label == None:
            label = "Gaussian Spectrum with mean: %4.2e and standard deviation: %4.2e" % (mean,stdev)
        super(GaussianSpectrum, self).__init__()
        self.mean = mean
        self.stdev = stdev
        
    def __call__(self,wavelength):
        """Calls a wavelength function"""
        return Gaussian(wavelength,self.mean,self.stdev)
        
        