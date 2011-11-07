#!/usr/bin/env python
# 
#  Test_AstroImage.py
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

import os

import nose.tools as nt
from nose.plugins.skip import Skip,SkipTest

from AstroObject.tests.Test_AstroObjectAPI import *

import AstroObject.AstroImage as AI
import AstroObject.AstroObjectBase as AOB
from AstroObject.Utilities import AbstractError

class test_ImageFrame(API_Base_Frame):
    """AstroImage.ImageFrame"""
    
    def setUp(self):
        """Sets up the test with some basic image data"""
        self.testJPG = "Hong-Kong.jpg"
        if not os.access(self.testJPG,os.R_OK):
            self.image = np.zeros((1000,1000))
            self.image[450:550,450:550] = np.ones((100,100))
        else:
            self.image = np.int32(np.sum(mpimage.imread(self.testJPG),axis=2))
            
        self.VALID = self.image
        self.FRAME = AI.ImageFrame
        self.INVALID = 20
        self.FRAMESTR = "<'ImageFrame' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.image.AxesImage
        self.FRAMEINST = AI.ImageFrame(self.image,"Hong Kong")
            
        def SAMEDATA(first,second):
            """Return whether these two are the same data"""
            return not (np.abs(first-second) > 1e-6).any()
            
        
        def SAME(first,second):
            """Return whether these two are the same"""
            return SAMEDATA(first(),second())
        
        self.SAME = SAME
        self.SAMEDATA = SAMEDATA
        
        self.check_constants()
        
        
    
            
    def test_read_grayscale_HDU(self):
        """__read__ an image HDU succeeds"""
        HDU = pf.PrimaryHDU(self.image)
        IFrame = AI.ImageFrame.__read__(HDU,"Hong Kong")
        assert isinstance(IFrame,AI.ImageFrame)
        assert IFrame.label == "Hong Kong"
        assert self.SAME(IFrame,self.FRAMEINST)
        
        
        
class test_ImageObject(API_Base_Object):
    """AstroImage.ImageObject"""
        
    def setUp(self):
        """Fixture for setting up a basic image frame"""
        self.testJPG = "Tests/Hong-Kong.jpg"
        if not os.access(self.testJPG,os.R_OK):
            self.image = np.zeros((1000,1000))
            self.image[450:550,450:550] = np.ones((100,100))
        else:
            self.image = np.int32(np.sum(mpimage.imread(self.testJPG),axis=2))
        self.FRAMEINST = AI.ImageFrame(self.image,"Hong Kong")
        self.FRAMELABEL = "Hong Kong"
        self.FRAME = AI.ImageFrame
        self.HDU = pf.PrimaryHDU(self.image)
        self.imHDU = pf.ImageHDU(self.image)
        self.VALID = self.image
        self.INVALID = 20
        self.OBJECTSTR = None
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.image.AxesImage
        self.OBJECT = AI.ImageObject
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
        
        
    def test_read_from_image_file(self):
        """loadFromFile() directly from an image file"""
        if not os.access(self.testJPG,os.R_OK):
            raise SkipTest
        IObject = self.OBJECT()
        IObject.loadFromFile(self.testJPG,"TestJPG")
        assert IObject.statename == "TestJPG"
        
    
    @nt.raises(IOError)
    def test_read_from_nonexistant_file(self):
        """loadFromFile() fails for a non-existant image file"""
        IObject = self.OBJECT()
        IObject.loadFromFile("Bogus")
        
        