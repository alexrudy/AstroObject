#!/usr/bin/env python
# 
#  Test_AnalyticSpectra.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-31.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 

import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimage

import os

import nose.tools as nt
from nose.plugins.skip import Skip,SkipTest

from AstroObject.Tests.Test_AstroObjectBase import *

import AstroObject.AnalyticSpectra as AS
from AstroObject.Utilities import AbstractError

class test_AnalyticSpectraFrame(API_Abstract_Frame):
    """AnalyticSpecra.AnalyticSpectrum"""
    
    def setUp(self):
        """Sets up the test with some basic image data."""
                
        self.DATA = None
        self.FRAME = AS.AnalyticSpectrum
        self.INVALID = np.array([1,2,3])
        self.FRAMESTR = "<'AnalyticSpectrum' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.artist.Artist
        def SAME(first,second):
            """Return whether these two are the same"""
            raise AbstractError("Data undefined...")
            
        self.SAME = SAME
        
        self.check_constants()
        
    def test_init_with_wavelengths(self):
        """Initialize with Wavelengths"""
        wl = np.arange(100)
        SFrame = self.FRAME("Empty",wl)
        assert not np.abs(wl - SFrame.wavelengths > 1e-6).any()
        
    def test_init_empty(self):
        """__init__ abstract frame works without data"""
        AFrame = self.FRAME("Valid")
        assert AFrame.label == "Valid"
        
    @nt.raises(AbstractError)
    def test_HDU(self):
        """HDU method raises an AbstractError"""
        BFrame = self.FRAME("Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.__hdu__()
    
    @nt.raises(AbstractError)
    def test_PrimaryHDU(self):
        """HDU primary raises an AbstractError"""
        BFrame = self.FRAME("Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.__hdu__(primary=True)
        
    def test_add_objects(self):
        """Objects respont to + operator"""
        SFrame1 = self.FRAME("Empty")
        SFrame2 = self.FRAME("Empty")
        SFrame3 = SFrame1 + SFrame2
        assert isinstance(SFrame3,AS.CompositeSpectra)
    
    def test_sub_objects(self):
        """Objects respont to - operator"""
        SFrame1 = self.FRAME("Empty")
        SFrame2 = self.FRAME("Empty")
        SFrame3 = SFrame1 - SFrame2
        assert isinstance(SFrame3,AS.CompositeSpectra)
        
        
    def test_mul_objects(self):
        """Objects respont to * operator"""
        SFrame1 = self.FRAME("Empty")
        SFrame2 = self.FRAME("Empty")
        SFrame3 = SFrame1 * SFrame2
        assert isinstance(SFrame3,AS.CompositeSpectra)
        
