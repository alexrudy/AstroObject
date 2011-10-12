# 
#  AnalyticSpectra.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 

import AstroImage,AstroSpectra
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

class AnalyticSpectra(AstroSpectra.SpectraFrame):
    """A functional spectrum object for spectrum generation. The default implementation is a flat spectrum."""
    def __init__(self,label,wavelengths=None,units=None):
        super(AnalyticSpectra, self).__init__(None,label)
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
        
    
    def __call__(self,wavelengths=None):
        """Returns the Flux data for this spectrum"""
        if wavelengths == None:
            wavelengths = self.wavelengths
        return np.hstack(np.ones(wavelengths.shape),wavelengths)
    
class CompositeSpectra(AnalyticSpectra):
    """Binary composition of two functional spectra"""
    def __init__(self, partA, partB, operation):
        label = partA.label + " " + operation + " " + partB.label
        super(CompositeSpectra, self).__init__(label)
        self.A = partA
        self.B = partB
        self.operation = operation
        
    def __call__(self,wavelengths=None):
        """Calls the composite function components"""
        if wavelengths == None:
            wavelengths = self.wavelengths
        if self.operation == 'add':
            return self.A(wavelengths) + self.B(wavelengths)
        elif self.operation == 'mul':
            return self.A(wavelengths) * self.B(wavelengths)
        elif self.operation == 'sub':
            return self.A(wavelengths) - self.B(wavelengths)
            
from AnalyticSpectraObjects import *
        