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

import os,copy

import nose.tools as nt
from nose.plugins.skip import Skip,SkipTest

from AstroObject.tests.Test_AstroObjectBase import *

import AstroObject.AnalyticSpectra as AS
from AstroObject.Utilities import AbstractError

class API_AnalyticSpectra(API_Abstract_Frame):
    """Set up and basic tests for analytic spectra"""

    def test_init_with_wavelengths(self):
        """__init__() works with wavelengths"""
        SFrame = self.FRAME(self.VALID,"Empty",self.WAVELENGTHS)
        assert not np.abs(self.WAVELENGTHS - SFrame.wavelengths > 1e-6).any()


    def test_init_empty(self):
        """__init__() abstract frame works without data"""
        AFrame = self.FRAME(self.VALID,"Valid")
        assert AFrame.label == "Valid"


    def test_add_objects(self):
        """__add__() Objects respont to + operator"""
        SFrame1 = self.FRAME(self.VALID,"Empty")
        SFrame2 = self.FRAME(self.VALID,"Empty")
        SFrame3 = SFrame1 + SFrame2
        assert isinstance(SFrame3,AS.CompositeSpectra)

    def test_sub_objects(self):
        """__sub__() Objects respont to - operator"""
        SFrame1 = self.FRAME(self.VALID,"Empty")
        SFrame2 = self.FRAME(self.VALID,"Empty")
        SFrame3 = SFrame1 - SFrame2
        assert isinstance(SFrame3,AS.CompositeSpectra)


    def test_mul_objects(self):
        """__mul__() Objects respont to * operator"""
        SFrame1 = self.FRAME(self.VALID,"Empty")
        SFrame2 = self.FRAME(self.VALID,"Empty")
        SFrame3 = SFrame1 * SFrame2
        assert isinstance(SFrame3,AS.CompositeSpectra)
        
    def test_add_other(self):
        """__add__() Handles adding of other simple classes"""
        SFrame1 = self.FRAME(self.VALID,"Empty")
        SFrame2 = 10.0
        SFrame3 = SFrame1 + SFrame2
        assert isinstance(SFrame3,AS.CompositeSpectra)

class test_AnalyticSpectraFrame(API_AnalyticSpectra):
    """AnalyticSpecra.AnalyticSpectrum"""
    
    def setUp(self):
        """Sets up the test with some basic image data."""
                
        self.VALID = None
        self.FRAME = AS.AnalyticSpectrum
        self.INVALID = np.array([1,2,3])
        self.FRAMESTR = "<'AnalyticSpectrum' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.artist.Artist
        self.WAVELENGTHS = np.arange(100)
        
        self.attributes = copy.deepcopy(self.attributes) + ['WAVELENGTHS']
        
        def SAMEDATA(first,second):
            """Return whether these two are the same data"""
            raise AbstractError("Data undefined...")
            
        
        def SAME(first,second):
            """Return whether these two are the same"""
            raise AbstractError("Data undefined...")
        
        self.SAME = SAME
        self.SAMEDATA = SAMEDATA
        
        
        self.check_constants()
        
    


class test_InterpolatedSpectra(API_AnalyticSpectra):
    """AnalyticSpecra.InterpolatedSpectra"""
    def setUp(self):
        """Sets up the test with some basic image data."""
                
        self.VALID = np.array([[-100.0,200.0,300.0],[1,3,5]])
        self.FRAME = AS.InterpolatedSpectrum
        self.INVALID = np.array([1,2,3])
        self.FRAMESTR = "<'InterpolatedSpectrum' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.artist.Artist
        self.WAVELENGTHS = np.arange(100)
        
        self.attributes = copy.deepcopy(self.attributes) + ['WAVELENGTHS']
        
        def SAMEDATA(first,second):
            """Return whether these two are the same data"""
            return not (np.abs(first-second) > 1e-6).any()
            
        
        def SAME(first,second):
            """Return whether these two are the same"""
            return SAMEDATA(first(),second())
        
        self.SAME = SAME
        self.SAMEDATA = SAMEDATA
        
        
        self.check_constants()
    
    def test_show(self):
        """__show__() returns a valid type"""
        AFrame = self.FRAME(self.VALID,"Valid")
        assert AFrame.label == "Valid"
        figure = AFrame.__show__()
        assert isinstance(figure,self.SHOWTYPE), "Found type %s" % type(figure)
        
    def test_call(self):
        """__call__() yields data"""
        AFrame = self.FRAME(self.VALID,"Valid")
        assert AFrame.label == "Valid"
        data = AFrame(self.WAVELENGTHS)