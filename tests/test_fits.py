# -*- coding: utf-8 -*-
# 
#  Test_base.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-28.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.6.0
# 

from tests.apitests import *
import AstroObject.base
import AstroObject.fits

import nose.tools as nt
from nose.plugins.skip import Skip,SkipTest
import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
import copy
import os    

class equality_FITSFrame(equality_Base):
    """Equality methods for FITSFrames"""
    
    def data_eq_data(self,data,other):
        """Return whether these two are the same data"""
        assert data is None, "First data is not None"
        assert other is None, "Second Data is not None"
        return data == other
        
    def frame_eq_frame(self,frame,other):
        """Return whether these two FITS frames are the same"""
        if hasattr(frame,'data'):
            assert frame.data is None
        if hasattr(other,'data'):
            assert other.data is None
        return True
            
    def data_eq_frame(self,data,frame):
        """Return whether this data is the same as the data in this frame."""
        assert data is None
        if hasattr(frame,'data'):
            assert frame.data is None
        return True
    
        

class test_FITSFrame(equality_FITSFrame,API_NoData_Frame,API_General_Frame):
    """base.FITSFrame"""
    
    def setup(self):
        self.FRAME = AstroObject.fits.FITSFrame
        self.FRAMESTR = "<'FITSFrame' labeled 'Valid'>"
        self.VALID = None
        self.INVALID = np.array([1,2,3]).astype(np.int16)
        self.SHOWTYPE = None
        self.HDUTYPE = pf.ImageHDU
        self.RKWARGS = {}
        self.FLABEL = "Valid"
        super(test_FITSFrame, self).setup()
    
        
class test_FITSStack(equality_FITSFrame,API_BaseStack):
    """fits.FITSStack"""
    def setup(self):
        self.files = ["TestFile.fits","TestFile.dat","TestFile.npy"]
        self.FRAME = AstroObject.fits.FITSFrame
        self.OBJECT = AstroObject.fits.FITSStack
        self.FRAMESTR = "<'FITSFrame' labeled 'Valid'>"
        self.VALID = None
        self.INVALID = np.array([1,2,3]).astype(np.int16)
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = None
        self.OBJECTSTR = None
        self.FLABEL = "Valid"
    
    @nt.raises(TypeError)
    def test_save_with_data(self):
        """save() fails with valid data (Abstract Object)"""
        AObject = self.OBJECT()
        AObject.save(self.VALID)
        
    @nt.raises(TypeError)
    def test_save_overwrite(self):
        """save() can clobber from parent or save()"""
        AObject = self.OBJECT()
        AObject.save(self.VALID,self.FLABEL)
        AObject.save(self.VALID,self.FLABEL,clobber=True)
        AObject = self.OBJECT()
        AObject.clobber = True
        AObject.save(self.VALID,self.FLABEL)
        AObject.save(self.VALID,self.FLABEL)
        
    @nt.raises(TypeError)
    def test_save_no_overwrite(self):
        """save failes when trying to inadvertently clobber"""
        AObject = self.OBJECT()
        AObject.save(self.VALID,self.FLABEL)
        AObject.save(self.VALID,self.FLABEL,clobber=False)
        AObject = self.OBJECT()
        AObject.clobber = False
        AObject.save(self.VALID,self.FLABEL)
        AObject.save(self.VALID,self.FLABEL)
    
    @nt.raises(TypeError)
    def test_write_to_singleframe_textfile(self):
        """write(singleFrame=True) creates single framed text files."""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject["Other"] = self.frame()
        PF,Fs,FN = AObject.write("test.dat",singleFrame=True,clobber=True)
        assert Fs == []
        assert PF == "Other"
        
    @nt.raises(TypeError)
    def test_write_to_singleframe_numpyfile(self):
        """write(singleFrame=True) creates single framed numpy files."""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject["Other"] = self.frame()
        PF,Fs,FN = AObject.write(self.files[2],singleFrame=True,clobber=True)
        AObject.read(self.files[2],clobber=True)        
        assert Fs == []
        assert PF == "Other"    
    
    @nt.raises(TypeError)
    def test_set_with_data(self):
        """[] fails with valid data"""
        AObject = self.OBJECT()
        AObject[self.FLABEL] = self.VALID
        
    def test_double_saving_data_should_not_reference(self):
        """data() should prevent data from referencing each other."""
        raise SkipTest("data() does not make sense with abstract base class")
    
    @nt.raises(NotImplementedError)
    def test_data(self):
        """data() raises an abstract error for an abstract frame"""
        BObject = self.OBJECT()
        BObject.save(self.frame())
        BObject.data()
        
    
    @nt.raises(NotImplementedError)
    def test_d(self):
        """.d raises an abstract error for an abstract frame"""
        BObject = self.OBJECT()
        BObject.save(self.frame())
        BObject.d
    
    
    @nt.raises(NotImplementedError)
    def test_show(self):
        """show() calls underlying show method, raising an abstract error"""
        BObject = self.OBJECT()
        BObject.save(self.frame())
        BObject.show()
    















