# -*- coding: utf-8 -*-
#
#  Test_AnalyticSpectra.py
#  ObjectModel
#
#  Created by Alexander Rudy on 2011-10-31.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.5.3-p2
#

import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.axes

import os,copy

import nose.tools as nt
from nose.plugins.skip import Skip,SkipTest

from tests.AstroTest import *

import AstroObject.AnalyticSpectra

class equality_AnalyticFrame(equality_Base):
    """Equality methods for FITSFrames"""
    
    def data_eq_data(self,data,other):
        """Return whether these two are the same data"""
        return np.allclose(data,other)
        
    def frame_eq_frame(self,frame,other):
        """Return whether these two FITS frames are the same"""
        return frame.label == other.label
                
    def data_eq_frame(self,data,frame):
        """Return whether this data is the same as the data in this frame."""
        return False

class equality_InterpolatedSpectraFrame(equality_AnalyticFrame):
    """Equality methods for FITSFrames"""
        
    def frame_eq_frame(self,frame,other):
        """Return whether these two FITS frames are the same"""
        return np.allclose(frame.data,other.data)
                
    def data_eq_frame(self,data,frame):
        """Return whether this data is the same as the data in this frame."""
        return np.allclose(frame.data,data)


class API_AnalyticSpectra(equality_AnalyticFrame,API_Base_Frame):
    """Set up and basic tests for analytic spectra"""
    
    def test_init_with_wavelengths(self):
        """__init__() works with wavelengths"""
        SFrame = self.frame(wavelengths=self.WAVELENGTHS)
        assert not np.abs(self.WAVELENGTHS - SFrame.requested_wavelengths > 1e-6).any()
    
    def test_call_with_arbitrary_arguments(self):
        """__call__() accepts arbitrary keyword arguments"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame(wavelengths=self.WAVELENGTHS,other=1,arbitrary="str",arguments="blah")
    
    @nt.raises(ValueError)
    def test_call(self):
        """__call__() fails"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame()
        
    def test_call_with_kwargs(self):
        """__call__(**kwargs) yields data"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame(wavelengths=self.WAVELENGTHS)
    
    
    def test_init_empty(self):
        """__init__() abstract frame works without data"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
    
    
    def test_add_objects(self):
        """__add__() Objects respont to + operator"""
        SFrame1 = self.frame()
        SFrame2 = self.frame()
        SFrame3 = SFrame1 + SFrame2
        assert isinstance(SFrame3,AstroObject.AnalyticSpectra.CompositeSpectra)
    
    def test_sub_objects(self):
        """__sub__() Objects respont to - operator"""
        SFrame1 = self.frame()
        SFrame2 = self.frame()
        SFrame3 = SFrame1 - SFrame2
        assert isinstance(SFrame3,AstroObject.AnalyticSpectra.CompositeSpectra)
    
    
    def test_mul_objects(self):
        """__mul__() Objects respont to * operator"""
        SFrame1 = self.frame()
        SFrame2 = self.frame()
        SFrame3 = SFrame1 * SFrame2
        assert isinstance(SFrame3,AstroObject.AnalyticSpectra.CompositeSpectra)
    
    def test_add_other(self):
        """__add__() Handles adding of other simple classes"""
        SFrame1 = self.frame()
        SFrame2 = 10.0
        SFrame3 = SFrame1 + SFrame2
        assert isinstance(SFrame3,AstroObject.AnalyticSpectra.CompositeSpectra)


class API_InterpolatedSpectrumBase(equality_InterpolatedSpectraFrame,API_AnalyticSpectra):
    """API_InterpolatedSpectrumBase"""
    
    def save_or_compare(self,data,filename,skip=True):
        """Save or compare data"""
        fname = filename % self.__class__.__name__
        try:
            old_data = np.load(fname)
        except IOError:
            np.save(fname,data)
            if skip:
                raise SkipTest
            else:
                return True
        else:
            passed = self.data_eq_data(data,old_data)
            
            if not passed:
                print npArrayInfo(data,"New Calc")
                print npArrayInfo(old_data,"Old Data")
            return passed
    
    def test_call(self):
        """__call__() yields valid data"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        WL = self.WAVELENGHTS_LOWR
        data = AFrame(wavelengths=WL[:-1],resolution=(WL[:-1]/np.diff(WL))/4,method='resample')        
        assert self.save_or_compare(data,"tests/data/%s-call.npy")
        
    def test_call_with_kwargs(self):
        """__call__() accepts arbitrary keyword arguments"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        WL = self.WAVELENGHTS_LOWR
        data = AFrame(wavelengths=WL[:-1],resolution=(WL[:-1]/np.diff(WL))/4,other=1,arbitrary="str",arguments="blah",method='resample')        
        assert self.save_or_compare(data,"tests/data/%s-call.npy",skip=False)    
    
    def test_call_resample(self):
        """__call__(method='resample') yields valid data"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        WL = self.WAVELENGHTS_LOWR
        data = AFrame(wavelengths=WL[:-1],resolution=(WL[:-1]/np.diff(WL))/4,method='resample')        
        assert self.save_or_compare(data,"tests/data/%s-resample.npy")
        
    def test_call_resample_with_arbitrary_arguments(self):
        """__call__(method='resample') accepts arbitrary keyword arguments"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        WL = self.WAVELENGHTS_LOWR
        data = AFrame(wavelengths=WL[:-1],resolution=(WL[:-1]/np.diff(WL))/4,other=1,arbitrary="str",arguments="blah",method='resample')
        assert self.save_or_compare(data,"tests/data/%s-resample2.npy",skip=False)

    def test_call_integrate_quad(self):
        """__call__(method='integrate_quad') yields valid data"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame(wavelengths=self.WAVELENGTHS[:-1],resolution=(self.WAVELENGTHS[:-1]/np.diff(self.WAVELENGTHS)),method="integrate_quad")
        assert self.save_or_compare(data,"tests/data/%s-integrateQ.npy")
        
        
    def test_call_integrate_quad_with_arbitrary_arguments(self):
        """__call__(method='integrate_quad') accepts arbitrary keyword arguments"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame(wavelengths=self.WAVELENGTHS[:-1],resolution=np.diff(self.WAVELENGTHS),other=1,arbitrary="str",arguments="blah",method="integrate_quad")
        assert self.save_or_compare(data,"tests/data/%s-integrateQ2.npy",skip=False)
        
    def test_call_integrate_hist_with_arbitrary_arguments(self):
        """__call__(method='integrate_hist')  accepts arbitrary keyword arguments"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame(wavelengths=self.WAVELENGTHS[:-1],resolution=np.diff(self.WAVELENGTHS),other=1,arbitrary="str",arguments="blah",method="integrate_hist")
        assert self.save_or_compare(data,"tests/data/%s-integrateH2.npy",skip=False)
    
    def test_call_integrate_hist(self):
        """__call__(method='integrate_hist') yields valid data"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame(wavelengths=self.WAVELENGTHS[:-1],resolution=np.diff(self.WAVELENGTHS),method="integrate_hist")
        assert self.save_or_compare(data,"tests/data/%s-integrateH.npy")

    def test_call_interpolate_with_arbitrary_arguments(self):
        """__call__(method='interpolate')  accepts arbitrary keyword arguments"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame(wavelengths=self.WAVELENGTHS[:-1],resolution=np.diff(self.WAVELENGTHS),other=1,arbitrary="str",arguments="blah",method="interpolate")
        assert self.save_or_compare(data,"tests/data/%s-interpolate2.npy",skip=False)
    
    def test_call_interpolate(self):
        """__call__(method='interpolate') yields valid data"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame(wavelengths=self.WAVELENGTHS[:-1],resolution=np.diff(self.WAVELENGTHS),method="interpolate")
        assert self.save_or_compare(data,"tests/data/%s-interpolate.npy")

    def test_call_polyfit_with_arbitrary_arguments(self):
        """__call__(method='polyfit')  accepts arbitrary keyword arguments"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame(wavelengths=self.WAVELENGTHS[:-1],resolution=np.diff(self.WAVELENGTHS),other=1,arbitrary="str",arguments="blah",method="polyfit")
        assert self.save_or_compare(data,"tests/data/%s-polyfit2.npy",skip=False)
    
    def test_call_polyfit(self):
        """__call__(method='polyfit') yields valid data"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame(wavelengths=self.WAVELENGTHS[:-1],resolution=np.diff(self.WAVELENGTHS),method="polyfit")
        assert self.save_or_compare(data,"tests/data/%s-polyfit.npy")
        
    def test_call_resolve_with_arbitrary_arguments(self):
        """__call__(method='resolve')  accepts arbitrary keyword arguments"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame(wavelengths=self.WAVELENGTHS[:-1],resolution=np.diff(self.WAVELENGTHS),other=1,arbitrary="str",arguments="blah",method="resolve")
        assert self.save_or_compare(data,"tests/data/%s-resolve2.npy",skip=False)
    
    def test_call_resolve(self):
        """__call__(method='resolve') yields valid data"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame(wavelengths=self.WAVELENGTHS[:-1],resolution=np.diff(self.WAVELENGTHS),method="resolve")
        assert self.save_or_compare(data,"tests/data/%s-resolve.npy")

    def test_call_resolve_and_integrate_arguments(self):
        """__call__(method='resolve_and_integrate')  accepts arbitrary keyword arguments"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame(wavelengths=self.WAVELENGTHS[:-1],resolution=np.diff(self.WAVELENGTHS),other=1,arbitrary="str",arguments="blah",method="resolve_and_integrate")
        assert self.save_or_compare(data,"tests/data/%s-resolve_and_integrate2.npy",skip=False)
    
    def test_call_resolve_and_integrate(self):
        """__call__(method='resolve_and_integrate') yields valid data"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame(wavelengths=self.WAVELENGTHS[:-1],resolution=np.diff(self.WAVELENGTHS),method="resolve_and_integrate")
        assert self.save_or_compare(data,"tests/data/%s-resolve_and_integrate.npy")
    

class test_InterpolatedSpectrum(API_InterpolatedSpectrumBase,API_General_Frame):
    """AnalyticSpecra.InterpolatedSpectrum"""

    def setup(self):
        """Sets up the test with some basic image data"""
        self.WAVELENGTHS = ((np.arange(98)+1)/2.0 + 1.0) * 1e-7
        self.WAVELENGHTS_LOWR = ((np.arange(23)+1)*2.0 + 1.0) * 1e-7
        self.VALID = np.array([(np.arange(50) + 1.0) * 1e-7,np.sin(np.arange(50))+2.0])
        self.FRAME = AstroObject.AnalyticSpectra.InterpolatedSpectrum
        self.INVALID = 20
        self.FRAMESTR = "<'InterpolatedSpectrum' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.axes.Subplot
        self.FLABEL = "Valid"
        self.RKWARGS = {'wavelengths':self.WAVELENGTHS}
        super(test_InterpolatedSpectrum,self).setup()
    
    
    
    
class test_UnitarySpectrum(API_AnalyticMixin,API_InterpolatedSpectrumBase):
    """AnalyticSpectra.UnitarySpectrum"""
    def setup(self):
        """Sets up the test with some basic image data"""
        self.WAVELENGTHS = ((np.arange(98)+1)/2.0 + 1.0) * 1e-7
        self.WAVELENGHTS_LOWR = ((np.arange(23)+1)*2.0 + 1.0) * 1e-7
        self.VALID = AstroObject.AnalyticSpectra.InterpolatedSpectrum(np.array([(np.arange(50) + 1.0) * 1e-7,np.sin(np.arange(50))+2.0]),"Valid")
        self.FRAME = AstroObject.AnalyticSpectra.UnitarySpectrum
        self.INVALID = 20
        self.FRAMESTR = "<'UnitarySpectrum' labeled '[Valid]'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.axes.Subplot
        self.RKWARGS = { 'wavelengths' : self.WAVELENGTHS }
        self.FLABEL = "[Valid]"
        super(test_UnitarySpectrum,self).setup()
        
    def frame(self,**kwargs):
        """Return a valid frame"""
        return self.FRAME(self.VALID,**kwargs)
        
    def test_init_nolabel(self):
        """__init__() succeeds with valid data but no label"""
        AFrame = self.FRAME(self.VALID,label=None)
        assert AFrame.label == self.FLABEL
        
    @nt.raises(AttributeError)
    def test_init_empty(self):
        """__init__() works without data"""
        self.FRAME(data=None,label="Label")
        
    def test_call(self):
        """__call__() yields valid data"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        WL = self.WAVELENGHTS_LOWR
        data = AFrame(wavelengths=WL[:-1],resolution=(WL[:-1]/np.diff(WL))/4)        
        assert self.save_or_compare(data,"tests/data/%s-call.npy")
        
    def test_call_with_kwargs(self):
        """__call__() accepts arbitrary keyword arguments"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        WL = self.WAVELENGHTS_LOWR
        data = AFrame(wavelengths=WL[:-1],resolution=(WL[:-1]/np.diff(WL))/4,other=1,arbitrary="str",arguments="blah")        
        assert self.save_or_compare(data,"tests/data/%s-call.npy",skip=False)
        
    def test_call_resample(self):
        """__call__(method='resample') yields valid data"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        WL = self.WAVELENGHTS_LOWR
        data = AFrame(wavelengths=WL[:-1],resolution=(WL[:-1]/np.diff(WL))/4,method='resample',upsample=True)        
        assert self.save_or_compare(data,"tests/data/%s-resample.npy")
        
    def test_call_resample_with_arbitrary_arguments(self):
        """__call__(method='resample') accepts arbitrary keyword arguments"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        WL = self.WAVELENGHTS_LOWR
        data = AFrame(wavelengths=WL[:-1],resolution=(WL[:-1]/np.diff(WL))/4,other=1,arbitrary="str",arguments="blah",method='resample',upsample=True)
        assert self.save_or_compare(data,"tests/data/%s-resample2.npy",skip=False)
    
class test_Resolver(API_InterpolatedSpectrumBase,API_General_Frame):
    """AnalyticSpectra.Resolver"""
    def setup(self):
        """Sets up the test with some basic image data"""
        self.WAVELENGTHS = ((np.arange(98)+1)/2.0 + 1.0) * 1e-7
        self.WAVELENGHTS_LOWR = ((np.arange(23)+1)*2.0 + 1.0) * 1e-7
        self.VALIDF = AstroObject.AnalyticSpectra.InterpolatedSpectrum(np.array([(np.arange(50) + 1.0) * 1e-7,np.sin(np.arange(50))+2.0]),"Valid")
        self.VALID = self.VALIDF.data
        self.FRAME = AstroObject.AnalyticSpectra.Resolver
        self.INVALID = 20
        self.FRAMESTR = "<'Resolver' labeled 'R[Valid]'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.axes.Subplot
        self.RKWARGS = { 'wavelengths' : self.VALID[0] }
        self.FLABEL = "R[Valid]"
        super(test_Resolver,self).setup()
        
    def frame(self,**kwargs):
        """Return a valid frame"""
        nkwargs = {}
        nkwargs.update(self.RKWARGS)
        nkwargs.update(kwargs)
        return self.FRAME(self.VALIDF,**nkwargs)
        
    def test_init_nolabel(self):
        """__init__() succeeds with valid data but no label"""
        AFrame = self.FRAME(self.VALIDF,label=None,**self.RKWARGS)
        assert AFrame.label == self.FLABEL
        
    @nt.raises(AttributeError)
    def test_init_empty(self):
        """__init__() works without data"""
        self.FRAME(data=None,label="Label",**self.RKWARGS)
        
    def test_call(self):
        """__call__() yields valid data"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        WL = self.WAVELENGHTS_LOWR
        data = AFrame(wavelengths=WL[:-1],resolution=(WL[:-1]/np.diff(WL))/4)        
        assert self.save_or_compare(data,"tests/data/%s-call.npy")
        
    def test_call_with_kwargs(self):
        """__call__() accepts arbitrary keyword arguments"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        WL = self.WAVELENGHTS_LOWR
        data = AFrame(wavelengths=WL[:-1],resolution=(WL[:-1]/np.diff(WL))/4,other=1,arbitrary="str",arguments="blah")        
        assert self.save_or_compare(data,"tests/data/%s-call.npy",skip=False)
        
    def test_call_resample(self):
        """__call__(method='resample') yields valid data"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        WL = self.WAVELENGHTS_LOWR
        data = AFrame(wavelengths=WL[:-1],resolution=(WL[:-1]/np.diff(WL))/4,method='resample',upsample=True)        
        assert self.save_or_compare(data,"tests/data/%s-resample.npy")
        
    def test_call_resample_with_arbitrary_arguments(self):
        """__call__(method='resample') accepts arbitrary keyword arguments"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        WL = self.WAVELENGHTS_LOWR
        data = AFrame(wavelengths=WL[:-1],resolution=(WL[:-1]/np.diff(WL))/4,other=1,arbitrary="str",arguments="blah",method='resample',upsample=True)
        assert self.save_or_compare(data,"tests/data/%s-resample2.npy",skip=False)
        
