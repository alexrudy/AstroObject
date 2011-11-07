# 
#  Test_AstroObjectBase.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-28.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 

from AstroObject.Tests.Test_AstroObjectAPI import *
import AstroObject.AstroObjectBase as AOB
from AstroObject.Utilities import AbstractError
import nose.tools as nt
from nose.plugins.skip import Skip,SkipTest
import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
import os

__all__ = ['API_Abstract_Frame','API_Abstract_Object']

class API_Abstract_Frame(API_Base_Frame):
    """Tests an Abstract Frame"""
    
    def test_init_invalid(self):
        """__init__() fails with invalid data"""
        raise SkipTest("This is a bug, related to argument ordering on the frame.__init__() call.")
        # The following arguments are treated as label and header respectivley. The lack of abstract type cheking and/or a data argument means that this call doesn't fail when it should.
        self.FRAME(self.INVALID,"Invalid")
    
    @nt.raises(AttributeError)
    def test_init_data(self):
        """__init__() fails with invalid data"""
        raise SkipTest("This is a bug, related to argument ordering on the frame.__init__() call.")
        # The following arguments are treated as label and header respectivley. The lack of abstract type cheking and/or a data argument means that this call doesn't fail when it should.
        self.FRAME(self.INVALID,"Invalid")
    
    def test_init_empty(self):
        """__init__() abstract frame works without data"""
        AFrame = self.FRAME("Valid")
        assert AFrame.label == "Valid"
    
    @nt.raises(AbstractError)
    def test_save_data(self):
        """save() to an abstract base class raises an AbstractError"""
        raise SkipTest("This is a bug, related to argument ordering on the frame.__init__() call.")
        # The following arguments are treated as label and header respectivley. The lack of abstract type cheking and/or a data argument means that this call doesn't fail when it should.
        self.FRAME.__save__(self.VALID,"None")
    
    @nt.raises(AbstractError)
    def test_read_SecondaryHDU(self):
        """read() secondary HDU type should get an abstract error"""
        HDU = self.HDUTYPE(self.INVALID)
        self.FRAME.__read__(HDU,"Empty")
        
    @nt.raises(AbstractError)
    def test_read_PrimaryHDU(self):
        """read() primary HDU type should get an abstract error"""
        HDU = pf.PrimaryHDU(self.INVALID)
        BFrame = self.FRAME.__read__(HDU,"Not Empty")
    
    @nt.raises(AbstractError)
    def test_call(self):
        """__call__() a base frame should raise an AbstractError"""
        BFrame = self.FRAME("Empty")
        assert BFrame.label == "Empty"
        BFrame()
    
    @nt.raises(AbstractError)
    def test_HDU(self):
        """__hdu__() raises an AbstractError"""
        BFrame = self.FRAME("Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.__hdu__()
    
    @nt.raises(AbstractError)
    def test_PrimaryHDU(self):
        """__hdu__() primary raises an AbstractError"""
        BFrame = self.FRAME("Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.__hdu__(primary=True)
    
    @nt.raises(AbstractError)
    def test_show(self):
        """show() a base frame should fail"""
        BFrame = self.FRAME("Empty")
        assert BFrame.label == "Empty"
        BFrame.__show__()
    
    def test_string_representation(self):
        """srt() String representation correct for Frame"""
        AFrame = self.FRAME("Valid")
        assert AFrame.label == "Valid"
        assert str(AFrame) == self.FRAMESTR
    



class API_Abstract_Object(API_Base_Object):
    """Tests an Abstract Object"""
    
    
    @nt.raises(AbstractError)
    def test_data(self):
        """data() raises an abstract error for an abstract frame"""
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST)
        BObject.data()
        
    
    @nt.raises(IndexError)
    def test_cannot_remove_nonexistant_state(self):
        """Cannot Remove Non-Existant State"""
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST,"A")
        BObject.remove("B")
        
    
    @nt.raises(AbstractError)
    def test_show(self):
        """Show should call underlying show method, raising an abstract error"""
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
        
        def SAMEDATA(first,second):
            """Return whether these two are the same data"""
            return first == second
            
        
        def SAME(first,second):
            """Return whether these two are the same"""
            return SAMEDATA(first.label,second.label)
        
        self.SAME = SAME
        self.SAMEDATA = SAMEDATA
        
        self.doSetUp()
    
    def test_HDU(self):
        """HDU method raises an AbstractError"""
        BFrame = self.FRAME("Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.__hdu__()
        assert isinstance(HDU,pf.ImageHDU)
        assert HDU.data == None

    def test_PrimaryHDU(self):
        """HDU primary raises an AbstractError"""
        BFrame = self.FRAME("Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.__hdu__(primary=True)
        assert isinstance(HDU,pf.PrimaryHDU)
        assert HDU.data == None
        
    def test_read_empty_HDU(self):
        """Reads an empty HDU"""
        HDU = pf.PrimaryHDU()
        BFrame = self.FRAME.__read__(HDU,"Empty")
        assert isinstance(BFrame,self.FRAME)
        assert BFrame.label == "Empty"
        



class test_FITSObject(API_Abstract_Object):
    """AstroObjectBase.FITSObject"""
    def setUp(self):
        self.FILENAME = "TestFile.fits"
        self.FRAME = AOB.FITSFrame
        self.OBJECT = AOB.FITSObject
        self.FRAMESTR = "<'FITSFrame' labeled 'Valid'>"
        self.VALID = None
        self.INVALID = np.array([1,2,3]).astype(np.int16)
        self.FRAMELABEL = "Empty"
        self.FRAMEINST = self.FRAME("Empty")
        self.HDUTYPE = pf.ImageHDU
        self.HDU = pf.PrimaryHDU()
        self.imHDU = pf.ImageHDU()
        self.SHOWTYPE = None
        self.OBJECTSTR = None
        
        def SAMEDATA(first,second):
            """Return whether these two are the same data"""
            raise AbstractError("This doesn't make sense for an abstract frame...")
            
        
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
        















