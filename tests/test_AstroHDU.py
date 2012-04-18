# -*- coding: utf-8 -*-
# 
#  Test_AstroHDU.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-11-08.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.4.0
# 

# Test API Imports
from tests.AstroTest import *

# Parent Object Imports
import AstroObject.AstroHDU

# Utility Imports
from AstroObject.Utilities import npArrayInfo

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

class equality_HDUFrame(equality_Base):
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

class test_HDUFrame(equality_HDUFrame,API_CanBeEmpty_Frame,API_General_Frame):
    """AstroHDU.HDUFrame"""
    
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
        self.FRAME = AstroObject.AstroHDU.HDUFrame
        self.INVALID = 20
        self.FRAMESTR = "<'HDUFrame' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.image.AxesImage
        self.RKWARGS = {}
        super(test_HDUFrame,self).setup()
    

class test_HDUObject(equality_HDUFrame,API_Base_Object):
    """AstroHDU.HDUObject"""
    
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

        self.FRAME = AstroObject.AstroHDU.HDUFrame
        self.HDU = pf.PrimaryHDU
        self.imHDU = pf.ImageHDU
        self.VALID = self.image
        self.INVALID = 20
        self.OBJECTSTR = None
        self.FRAMESTR = "<'HDUFrame' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.image.AxesImage
        self.OBJECT = AstroObject.AstroHDU.HDUObject
        super(test_HDUObject, self).setup()
    
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

    
