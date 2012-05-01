# -*- coding: utf-8 -*-
# 
#  Test_AstroObjectBase.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-28.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.5.1
# 

from tests.AstroTest import *
import AstroObject.AstroObjectBase
import AstroObject.AstroFITS

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
    """AstroObjectBase.FITSFrame"""
    
    def setup(self):
        self.FRAME = AstroObject.AstroFITS.FITSFrame
        self.FRAMESTR = "<'FITSFrame' labeled 'Valid'>"
        self.VALID = None
        self.INVALID = np.array([1,2,3]).astype(np.int16)
        self.SHOWTYPE = None
        self.HDUTYPE = pf.ImageHDU
        self.RKWARGS = {}
        super(test_FITSFrame, self).setup()
    
        
class test_FITSStack(equality_FITSFrame,API_BaseStack):
    """AstroFITS.FITSStack"""
    def setup(self):
        self.files = ["TestFile.fits"]
        self.FRAME = AstroObject.AstroFITS.FITSFrame
        self.OBJECT = AstroObject.AstroFITS.FITSStack
        self.FRAMESTR = "<'FITSFrame' labeled 'Valid'>"
        self.VALID = None
        self.INVALID = np.array([1,2,3]).astype(np.int16)
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = None
        self.OBJECTSTR = None
    
    @nt.raises(TypeError)
    def test_save_with_data(self):
        """save() fails with valid data (Abstract Object)"""
        AObject = self.OBJECT()
        AObject.save(self.VALID)
        
    @nt.raises(TypeError)
    def test_save_overwrite(self):
        """save() can clobber from parent or save()"""
        AObject = self.OBJECT()
        AObject.save(self.VALID,"Valid")
        AObject.save(self.VALID,"Valid",clobber=True)
        AObject = self.OBJECT()
        AObject.clobber = True
        AObject.save(self.VALID,"Valid")
        AObject.save(self.VALID,"Valid")
        
    @nt.raises(TypeError)
    def test_save_no_overwrite(self):
        """save failes when trying to inadvertently clobber"""
        AObject = self.OBJECT()
        AObject.save(self.VALID,"Valid")
        AObject.save(self.VALID,"Valid",clobber=False)
        AObject = self.OBJECT()
        AObject.clobber = False
        AObject.save(self.VALID,"Valid")
        AObject.save(self.VALID,"Valid")
    
        
    @nt.raises(TypeError)
    def test_set_with_data(self):
        """[] fails with valid data"""
        AObject = self.OBJECT()
        AObject["Valid"] = self.VALID
        
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
    















