# -*- coding: utf-8 -*-
# 
#  test_AstroNDArray.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-04-18.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 


# Test API Imports
from tests.Test_AstroObjectAPI import *

# Parent Object Imports
import AstroObject.AstroNDArray as AN

# Testing Imports
import nose.tools as nt
from nose.plugins.skip import Skip,SkipTest

# Scipy Imports
import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimage


# Python Imports
import math, copy, sys, time, logging, os

class test_NDArrayFrame(API_Base_Frame):
    """AstroImage.ImageFrame"""
    
    def setUp(self):
        """Sets up the test with some basic image data"""
        self.image = np.zeros((1000,1000))
        self.image[450:550,450:550] = np.ones((100,100))
        self.VALID = self.image
        self.FRAME = AN.NDArrayFrame
        self.INVALID = 20
        self.FRAMESTR = "<'NDArrayFrame' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.image.AxesImage
        self.FRAMEINST = AN.NDArrayFrame(self.image,"Hong Kong")
        self.imHDU = pf.ImageHDU
        self.pmHDU = pf.PrimaryHDU
            
        def SAMEDATA(first,second):
            """Return whether these two are the same data"""
            return not (np.abs(first-second) > 1e-6).any()
        
        
        def SAME(first,second):
            """Return whether these two are the same"""
            return SAMEDATA(first,second)
        
        self.SAME = SAME
        self.SAMEDATA = SAMEDATA
        
        self.check_constants()
        
    
            
    
    def test_read_grayscale_HDU(self):
        """__read__() an image HDU succeeds"""
        HDU = pf.PrimaryHDU(self.image)
        NFrame = AN.NDArrayFrame.__read__(HDU,"Hong Kong")
        assert isinstance(NFrame,AN.NDArrayFrame)
        assert NFrame.label == "Hong Kong"
        assert self.SAME(NFrame,self.FRAMEINST)
        
        

class test_ImageObject(API_Base_Object):
    """AstroImage.ImageObject"""
    
    def setUp(self):
        """Fixture for setting up a basic image frame"""
        self.image = np.zeros((1000,1000))
        self.image[450:550,450:550] = np.ones((100,100))
        self.FRAMEINST = AN.NDArrayFrame(self.image,"Hong Kong")
        self.FRAMELABEL = "Hong Kong"
        self.FRAME = AN.NDArrayFrame
        self.HDU = pf.PrimaryHDU
        self.imHDU = pf.ImageHDU
        self.VALID = self.image
        self.INVALID = 20
        self.OBJECTSTR = None
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.image.AxesImage
        self.OBJECT = AN.NDArrayObject
        self.FILENAME = "TestFile.fits"
        
        def SAMEDATA(first,second):
            """Return whether these two are the same data"""
            return not (np.abs(first-second) > 1e-6).any()
        
        
        def SAME(first,second):
            """Return whether these two are the same"""
            return SAMEDATA(first,second)
        
        self.SAME = SAME
        self.SAMEDATA = SAMEDATA
        
        self.check_constants()
    
    def test_double_saving_data_should_not_reference(self):
        """data() should prevent data from referencing each other."""
        NewLabel = "Other"
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        AObject.save(AObject.data(),NewLabel)
        assert AObject.statename == NewLabel
        assert AObject.frame().label == NewLabel
        AObject.select(self.FRAMELABEL)
        assert AObject.statename == self.FRAMELABEL
        assert AObject.frame().label == self.FRAMELABEL
        AObject.select(NewLabel)
        assert AObject.statename == NewLabel
        assert AObject.frame().label == NewLabel
        data = AObject.data()
        data[1,1] = -1.0
        assert AObject.data()[1,1] != -1.0
        AObject.select(self.FRAMELABEL)
        assert AObject.data()[1,1] != -1.0

class test_AstroImage_Functional(API_Base_Functional):
    """Functional Tests for AstroImage"""
    def setUp(self):
        """Fixture for setting up a basic image frame"""
        self.testJPG = "Data/Hong-Kong.jpg"
        if not os.access(self.testJPG,os.R_OK):
            self.image = np.zeros((1000,1000))
            self.image[450:550,450:550] = np.ones((100,100))
        else:
            self.image = np.int32(np.sum(mpimage.imread(self.testJPG),axis=2))
        self.FRAMEINST = AN.NDArrayFrame(self.image,"Hong Kong")
        self.FRAMELABEL = "Hong Kong"
        self.FRAME = AN.NDArrayFrame
        self.HDU = pf.PrimaryHDU
        self.imHDU = pf.ImageHDU
        self.VALID = self.image
        self.INVALID = 20
        self.OBJECTSTR = None
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.image.AxesImage
        self.OBJECT = AN.NDArrayObject
        self.FILENAME = "TestFile.fits"
        
        def SAMEDATA(first,second):
            """Return whether these two are the same data"""
            return not (np.abs(first-second) > 1e-6).any()
        
        
        def SAME(first,second):
            """Return whether these two are the same"""
            return SAMEDATA(first,second)
        
        self.SAME = SAME
        self.SAMEDATA = SAMEDATA
        
        self.check_constants()
