# -*- coding: utf-8 -*-
#
#  Test_AstroImage.py
#  ObjectModel
#
#  Created by Alexander Rudy on 2011-10-31.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.5.1
#

# Test API Imports
from tests.AstroTest import *

# Parent Object Imports
import AstroObject.AstroImage

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
        
class test_ImageFrame(equality_ImageFrame,API_General_Frame):
    """AstroImage.ImageFrame"""
    
    def setup(self):
        """Sets up the test with some basic image data"""
        self.testJPG = "Hong-Kong.jpg"
        self.data = [self.testJPG]
        if not os.access(self.testJPG,os.R_OK):
            self.image = np.zeros((1000,1000))
            self.image[450:550,450:550] = np.ones((100,100))
        else:
            self.image = np.int32(np.sum(mpimage.imread(self.testJPG),axis=2))
        
        self.VALID = self.image
        self.FRAME = AstroObject.AstroImage.ImageFrame
        self.INVALID = 20
        self.FRAMESTR = "<'ImageFrame' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.image.AxesImage
        self.RKWARGS = {}
        super(test_ImageFrame,self).setup()
    
    def test_init_manydim(self):
        """__init__() works with many dimensional data."""
        self.FRAME(data=np.ones((100,100,100)),label="3D!")
    
    def test_read_grayscale_HDU(self):
        """__read__() an image HDU succeeds"""
        HDU = self.HDUTYPE(self.image)
        IFrame = self.FRAME.__read__(HDU,"Hong Kong")
        assert isinstance(IFrame,self.FRAME)
        assert IFrame.label == "Hong Kong"
        assert self.frame_eq_frame(IFrame,self.frame())
        
        

class test_ImageStack(equality_ImageFrame,API_BaseStack):
    """AstroImage.ImageStack"""
    
    def setup(self):
        """Fixture for setting up a basic image frame"""
        self.testJPG = "Data/Hong-Kong.jpg"
        self.data = [self.testJPG]
        self.files = ["TestFile.fits"]
        if not os.access(self.testJPG,os.R_OK):
            self.image = np.zeros((1000,1000))
            self.image[450:550,450:550] = np.ones((100,100))
        else:
            self.image = np.int32(np.sum(mpimage.imread(self.testJPG),axis=2))

        self.FRAME = AstroObject.AstroImage.ImageFrame
        self.HDU = pf.PrimaryHDU
        self.imHDU = pf.ImageHDU
        self.VALID = self.image
        self.INVALID = 20
        self.OBJECTSTR = None
        self.FRAMESTR = "<'ImageFrame' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.image.AxesImage
        self.OBJECT = AstroObject.AstroImage.ImageStack
        super(test_ImageStack, self).setup()
        
    
    def test_read_from_image_file(self):
        """loadFromFile() directly from an image file"""
        if not os.access(self.data[0],os.R_OK):
            raise SkipTest
        IObject = self.OBJECT()
        IObject.loadFromFile(self.data[0],"TestJPG")
        assert IObject.framename == "TestJPG"
        
    def test_mask(self):
        """mask() works to clip info off of side of image."""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.mask(10,10)
        
    def test_crop(self):
        """crop() works to centered crop"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.crop(500,500,40)
    
    @nt.raises(IOError)
    def test_read_from_nonexistant_file(self):
        """loadFromFile() fails for a non-existant image file"""
        IObject = self.OBJECT()
        IObject.loadFromFile("Bogus")
    
    def test_double_saving_data_should_not_reference(self):
        """data() should prevent data from referencing each other."""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.save(AObject.data(),"Other")
        assert AObject.framename == "Other"
        assert AObject.frame().label == "Other"
        AObject.select("Valid")
        assert AObject.framename == "Valid"
        assert AObject.frame().label == "Valid"
        AObject.select("Other")
        assert AObject.framename == "Other"
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
        self.FRAMEINST = AI.ImageFrame(self.image,"Hong Kong")
        self.FRAME = AI.ImageFrame
        self.HDU = pf.PrimaryHDU
        self.imHDU = pf.ImageHDU
        self.VALID = self.image
        self.INVALID = 20
        self.OBJECTSTR = None
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.image.AxesImage
        self.OBJECT = AI.ImageStack
        self.FILENAME = "TestFile.fits"
        
        def SAMEDATA(first,second):
            """Return whether these two are the same data"""
            return not (np.abs(first-second) > 1e-6).any()
        
        
        def SAME(first,second):
            """Return whether these two are the same"""
            return SAMEDATA(first(),second())
        
        self.SAME = SAME
        self.SAMEDATA = SAMEDATA
        
        self.check_constants()

        
