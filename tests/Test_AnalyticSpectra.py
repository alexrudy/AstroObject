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

from tests.Test_AstroObjectBase import *
from tests.Test_AstroObjectAPI import *
from tests.Test_AstroSpectra import *

import AstroObject.AnalyticSpectra as AS

class API_AnalyticSpectra(API_Abstract_Frame):
    """Set up and basic tests for analytic spectra"""
    
    def test_init_with_wavelengths(self):
        """__init__() works with wavelengths"""
        SFrame = self.FRAME(data=self.VALID,label="Empty",wavelengths=self.WAVELENGTHS)
        assert not np.abs(self.WAVELENGTHS - SFrame.wavelengths > 1e-6).any()
    
    
    def test_call_with_arbitrary_arguments(self):
        """__call__() accepts arbitrary keyword arguments"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        data = AFrame(wavelengths=self.WAVELENGTHS,other=1,arbitrary="str",arguments="blah")
    
    def test_call(self):
        """__call__() yields data"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        data = AFrame(wavelengths=self.WAVELENGTHS)
    
    def test_init_empty(self):
        """__init__() abstract frame works without data"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
    
    
    def test_add_objects(self):
        """__add__() Objects respont to + operator"""
        SFrame1 = self.FRAME(data=self.VALID,label="Empty")
        SFrame2 = self.FRAME(data=self.VALID,label="Empty")
        SFrame3 = SFrame1 + SFrame2
        assert isinstance(SFrame3,AS.CompositeSpectra)
    
    def test_sub_objects(self):
        """__sub__() Objects respont to - operator"""
        SFrame1 = self.FRAME(data=self.VALID,label="Empty")
        SFrame2 = self.FRAME(data=self.VALID,label="Empty")
        SFrame3 = SFrame1 - SFrame2
        assert isinstance(SFrame3,AS.CompositeSpectra)
    
    
    def test_mul_objects(self):
        """__mul__() Objects respont to * operator"""
        SFrame1 = self.FRAME(data=self.VALID,label="Empty")
        SFrame2 = self.FRAME(data=self.VALID,label="Empty")
        SFrame3 = SFrame1 * SFrame2
        assert isinstance(SFrame3,AS.CompositeSpectra)
    
    def test_add_other(self):
        """__add__() Handles adding of other simple classes"""
        SFrame1 = self.FRAME(data=self.VALID,label="Empty")
        SFrame2 = 10.0
        SFrame3 = SFrame1 + SFrame2
        assert isinstance(SFrame3,AS.CompositeSpectra)
            

class test_AnalyticSpectraFrame(API_AnalyticSpectra,API_Abstract_Frame):
    """AnalyticSpecra.AnalyticSpectrum"""
    
    def setUp(self):
        """Sets up the test with some basic image data."""
        
        self.VALID = None
        self.FRAME = AS.AnalyticSpectrum
        self.INVALID = np.array([1,2,3])
        self.FRAMESTR = "<'AnalyticSpectrum' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.artist.Artist
        self.WAVELENGTHS = (np.arange(100) + 1.0) * 1e-7
        self.imHDU = pf.ImageHDU
        self.pmHDU = pf.PrimaryHDU
        
        self.attributes = copy.deepcopy(self.attributes) + ['WAVELENGTHS']
        
        def SAMEDATA(first,second):
            """Return whether these two are the same data"""
            raise NotImplementedError("Data undefined...")
        
        
        def SAME(first,second):
            """Return whether these two are the same"""
            raise NotImplementedError("Data undefined...")
        
        self.SAME = SAME
        self.SAMEDATA = SAMEDATA
        
        
        self.check_constants()
    
    @nt.raises(NotImplementedError)
    def test_call(self):
        """__call__() raises abstract error"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        data = AFrame(wavelengths=self.WAVELENGTHS)
        
    @nt.raises(NotImplementedError)
    def test_call_with_arbitrary_arguments(self):
        """__call__() accepts arbitrary keyword arguments"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        data = AFrame(wavelengths=self.WAVELENGTHS,other=1,arbitrary="str",arguments="blah")
        




class test_InterpolatedSpectra(API_AnalyticSpectra,test_SpectraFrame):
    """AnalyticSpecra.InterpolatedSpectra"""
    def setUp(self):
        """Sets up the test with some basic image data."""
        
        self.FRAME = AS.InterpolatedSpectrum
        self.INVALID = np.array([1,2,3])
        self.FRAMESTR = "<'InterpolatedSpectrum' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.artist.Artist
        self.WAVELENGTHS = ((np.arange(98)+1)/2.0 + 1.0) * 1e-7
        self.WAVELENGHTS_LOWR = ((np.arange(23)+1)*2.0 + 1.0) * 1e-7
        self.VALID = np.array([(np.arange(50) + 1.0) * 1e-7,np.sin(np.arange(50))+2.0])
        
        self.imHDU = pf.ImageHDU
        self.pmHDU = pf.PrimaryHDU
        
        
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
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        figure = AFrame.__show__()
        assert isinstance(figure,self.SHOWTYPE), "Found type %s" % type(figure)
    
    
    def test_call_resample(self):
        """__call__(method='resample') yields data"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        WL = self.WAVELENGHTS_LOWR
        data = AFrame(wavelengths=WL[:-1],resolution=(WL[:-1]/np.diff(WL))/4,method='resample')
        
    def test_call_resample_with_arbitrary_arguments(self):
        """__call__(method='resample') accepts arbitrary keyword arguments"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        WL = self.WAVELENGHTS_LOWR
        data = AFrame(wavelengths=WL[:-1],resolution=(WL[:-1]/np.diff(WL))/4,other=1,arbitrary="str",arguments="blah",method='resample')
    

    def test_call_integrate_quad(self):
        """__call__(method='integrate_quad') yields data"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        data = AFrame(wavelengths=self.WAVELENGTHS[:-1],resolution=(self.WAVELENGTHS[:-1]/np.diff(self.WAVELENGTHS)),method="integrate_quad")
        
    def test_call_integrate_quad_with_arbitrary_arguments(self):
        """__call__(method='integrate_quad') accepts arbitrary keyword arguments"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        data = AFrame(wavelengths=self.WAVELENGTHS[:-1],resolution=np.diff(self.WAVELENGTHS),other=1,arbitrary="str",arguments="blah",method="integrate_quad")
    
