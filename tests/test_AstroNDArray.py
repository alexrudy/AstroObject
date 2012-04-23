# -*- coding: utf-8 -*-
# 
#  test_AstroNDArray.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-04-18.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.5-a2
# 


# Test API Imports
from tests.AstroTest import *

# Parent Object Imports
import AstroObject.AstroNDArray

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

class equality_ImageFrame(equality_Base):
    """Equality methods for FITSFrames"""
    
    def data_eq_data(self,data,other):
        """Return whether these two are the same data"""
        return np.allclose(data,other)
        
    def frame_eq_frame(self,frame,other):
        """Return whether these two FITS frames are the same"""
        return np.allclose(frame(),other())
                
    def data_eq_frame(self,data,frame):
        """Return whether this data is the same as the data in this frame."""
        return np.allclose(frame(),data)


class test_NDArrayFrame(equality_ImageFrame,API_General_Frame):
    """AstroNDArray.NDArrayFrame"""
    
    def setup(self):
        """Sets up the test with some basic image data"""
        self.testJPG = "Hong-Kong.jpg"
        self.data = [self.testJPG]
        if not os.access(self.testJPG,os.R_OK):
            self.image = np.zeros((100,100))
            self.image[45:55,45:55] = np.ones((10,10))
        else:
            self.image = np.int32(np.sum(mpimage.imread(self.testJPG),axis=2))
        
        self.VALID = self.image
        self.FRAME = AstroObject.AstroNDArray.NDArrayFrame
        self.INVALID = 20
        self.FRAMESTR = "<'NDArrayFrame' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.image.AxesImage
        self.RKWARGS = {}
        super(test_NDArrayFrame,self).setup()            
    
    def test_read_grayscale_HDU(self):
        """__read__() an image HDU succeeds"""
        HDU = self.HDUTYPE(self.image)
        IFrame = self.FRAME.__read__(HDU,"Hong Kong")
        assert isinstance(IFrame,self.FRAME)
        assert IFrame.label == "Hong Kong"
        assert self.frame_eq_frame(IFrame,self.frame())
        
        

class test_NDArrayStack(equality_ImageFrame,API_Base_Object):
    """AstroNDArray.NDArrayStack"""
    
    def setup(self):
        """Fixture for setting up a basic image frame"""
        self.testJPG = "Data/Hong-Kong.jpg"
        self.data = [self.testJPG]
        self.files = ["TestFile.fits"]
        if not os.access(self.testJPG,os.R_OK):
            self.image = np.zeros((100,100))
            self.image[45:55,45:55] = np.ones((10,10))
        else:
            self.image = np.int32(np.sum(mpimage.imread(self.testJPG),axis=2))


        self.FRAME = AstroObject.AstroNDArray.NDArrayFrame
        self.HDU = pf.PrimaryHDU
        self.imHDU = pf.ImageHDU
        self.VALID = self.image
        self.INVALID = 20
        self.OBJECTSTR = None
        self.FRAMESTR = "<'ImageFrame' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.image.AxesImage
        self.OBJECT = AstroObject.AstroNDArray.NDArrayStack
        super(test_NDArrayStack, self).setup()
        
    def test_double_saving_data_should_not_reference(self):
        """data() should prevent data from referencing each other."""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.save(AObject.data(),"Other")
        assert AObject.statename == "Other"
        assert AObject.frame().label == "Other"
        AObject.select("Valid")
        assert AObject.statename == "Valid"
        assert AObject.frame().label == "Valid"
        AObject.select("Other")
        assert AObject.statename == "Other"
        assert AObject.frame().label == "Other"
        data = AObject.data()
        data[1,1] = -1.0
        assert AObject.data()[1,1] != -1.0
        AObject.select("Valid")
        assert AObject.data()[1,1] != -1.0

class btest_AstroImage_Functional(API_Base_Functional):
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
        self.FRAME = AN.NDArrayFrame
        self.HDU = pf.PrimaryHDU
        self.imHDU = pf.ImageHDU
        self.VALID = self.image
        self.INVALID = 20
        self.OBJECTSTR = None
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.image.AxesImage
        self.OBJECT = AN.NDArrayStack
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
