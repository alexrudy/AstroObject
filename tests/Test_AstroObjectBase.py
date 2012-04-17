# -*- coding: utf-8 -*-
# 
#  Test_AstroObjectBase.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-28.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.4.0
# 

from tests.Test_AstroObjectAPI import *
import AstroObject.AstroObjectBase as AOB
import nose.tools as nt
from nose.plugins.skip import Skip,SkipTest
import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
import copy
import os

__all__ = ['API_Abstract_Object']    



class API_Abstract_Object(API_Base_Object):
    """Tests an Abstract Object"""
    
    def test_double_saving_data_should_not_reference(self):
        """data() should prevent data from referencing each other."""
        raise SkipTest("data() does not make sense with abstract base class")
    
    @nt.raises(NotImplementedError)
    def test_data(self):
        """data() raises an abstract error for an abstract frame"""
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST)
        BObject.data()
        
    
    @nt.raises(NotImplementedError)
    def test_show(self):
        """show() calls underlying show method, raising an abstract error"""
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST)
        BObject.show()
        

class test_FITSFrame(API_Abstract_Frame):
    """AstroObjectBase.FITSFrame"""
    
    def setUp(self):
        self.FRAME = AOB.FITSFrame
        self.FRAMESTR = "<'FITSFrame' labeled 'Valid'>"
        self.VALID = None
        self.INVALID = np.array([1,2,3]).astype(np.int16)
        self.SHOWTYPE = None
        self.HDUTYPE = pf.ImageHDU
        self.HEADER = pf.PrimaryHDU().header
        self.HEADER.update('FEATURE','Value')
        self.imHDU = pf.ImageHDU
        self.pmHDU = pf.PrimaryHDU
        
        
        
        def SAMEDATA(first,second):
            """Return whether these two are the same data"""
            return first == second
            
        
        def SAME(first,second):
            """Return whether these two are the same"""
            return SAMEDATA(first.label,second.label)
        
        self.SAME = SAME
        self.SAMEDATA = SAMEDATA
        
        self.attributes = copy.deepcopy(self.attributes) + ['HEADER']
        
        self.doSetUp()
    
    def test_HDU_special(self):
        """__hdu__() generates an empty Image HDU"""
        BFrame = self.FRAME(data=self.VALID,label="Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.__hdu__()
        assert isinstance(HDU,pf.ImageHDU)
        assert HDU.data == None
    
    def test_HDU(self):
        """hdu() generates an empty Image HDU"""
        BFrame = self.FRAME(data=self.VALID,label="Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.hdu()
        assert isinstance(HDU,pf.ImageHDU)
        assert HDU.data == None
    
    
    def test_HDU_with_header(self):
        """hdu() generates an empty Image HDU with Header"""
        BFrame = self.FRAME(data=self.VALID,label="Empty",header=self.HEADER)
        assert BFrame.label == "Empty"
        HDU = BFrame.hdu()
        assert isinstance(HDU,pf.ImageHDU)
        assert HDU.data == None
        assert HDU.header["FEATURE"] == 'Value'

    def test_PrimaryHDU_special(self):
        """__hdu__() primary generates an empty Primary HDU"""
        BFrame = self.FRAME(data=self.VALID,label="Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.__hdu__(primary=True)
        assert isinstance(HDU,pf.PrimaryHDU)
        assert HDU.data == None    
    
    def test_PrimaryHDU(self):
        """hdu() primary generates an empty Primary HDU"""
        BFrame = self.FRAME(data=self.VALID,label="Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.hdu(primary=True)
        assert isinstance(HDU,pf.PrimaryHDU)
        assert HDU.data == None
        
    def test_read_empty_HDU(self):
        """__read__() works on an empty primary HDU"""
        HDU = pf.PrimaryHDU()
        BFrame = self.FRAME.__read__(HDU,"Empty")
        assert isinstance(BFrame,self.FRAME)
        assert BFrame.label == "Empty"
        



class test_FITSObject(API_Abstract_Object):
    """AstroObjectBase.BaseObject"""
    def setUp(self):
        self.FILENAME = "TestFile.fits"
        self.FRAME = AOB.FITSFrame
        self.OBJECT = AOB.FITSObject
        self.FRAMESTR = "<'FITSFrame' labeled 'Valid'>"
        self.VALID = None
        self.INVALID = np.array([1,2,3]).astype(np.int16)
        self.FRAMELABEL = "Empty"
        self.FRAMEINST = self.FRAME(data=None,label="Empty")
        self.HDUTYPE = pf.ImageHDU
        self.HDU = pf.PrimaryHDU
        self.imHDU = pf.ImageHDU
        self.SHOWTYPE = None
        self.OBJECTSTR = None
        
        def SAMEDATA(first,second):
            """Return whether these two are the same data"""
            raise NotImplementedError("This doesn't make sense for an abstract frame...")
            
        
        def SAME(first,second):
            """Return whether these two are the same"""
            return isinstance(first,AOB.FITSFrame) and isinstance(second,AOB.FITSFrame)
        
        self.SAME = SAME
        self.SAMEDATA = SAMEDATA
        
        self.doSetUp()
    
    @nt.raises(TypeError)
    def test_save_with_data(self):
        """save() fails with valid data (Abstract Object)"""
        AObject = self.OBJECT()
        AObject.save(self.VALID)
        
    @nt.raises(TypeError)
    def test_set_with_data(self):
        """[] fails with valid data"""
        AObject = self.OBJECT()
        AObject["Valid"] = self.VALID
        
        















