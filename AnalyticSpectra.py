# 
#  AnalyticSpectra.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.2.2
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

# Standard Python Modules
import math, copy, sys, time, logging, os

# Submodules from this system
from Utilities import *

class AnalyticSpectrum(AstroObjectBase.FITSFrame):
    """A functional spectrum object for spectrum generation. The default implementation is a flat spectrum."""
    def __init__(self,data,label,wavelengths=None,units=None):
        super(AnalyticSpectrum, self).__init__(data, label)
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
    """Binary composition of two functional spectra"""
    def __init__(self, partA, partB, operation):
        label = partA.label + " " + operation + " " + partB.label
        super(CompositeSpectra, self).__init__(None,label)
        self.A = partA
        self.B = partB
        self.operation = operation
        
    def __call__(self,wavelengths=None):
        """Calls the composite function components"""
        if wavelengths == None:
            wavelengths = self.wavelengths
        if wavelengths == None:
            raise ValueError("No wavelengths specified in %s" % (self))
            
        
        Awavelengths,Avalue = self.A(wavelengths)
        Bwavelengths,Bvalue = self.B(wavelengths)
        
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
            
from AnalyticSpectraObjects import *
        
