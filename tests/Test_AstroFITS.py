# 
#  Test_AstroFITS.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-11-08.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 

# Test API Imports
from AstroObject.tests.Test_AstroObjectAPI import *

# Parent Object Imports
import AstroObject.AstroFITS as AF

# Utility Imports
from AstroObject.Utilities import AbstractError, npArrayInfo

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

class test_HDUFrame(API_Base_Frame):
    """AstroFITS.ImageFrame"""
    
    def setUp(self):
        """Sets up the test with some basic image data"""
        self.testFITS = "Hong-Kong.fits"
        if not os.access(self.testFITS,os.R_OK):
            self.image = np.zeros((1000,1000))
            self.image[450:550,450:550] = np.ones((100,100))
        else:
            self.image = pf.open(self.testFITS)[0].data
            
        self.VALID = self.image
        self.FRAME = AF.HDUFrame
        self.INVALID = "20"
        self.FRAMESTR = "<'HDUFrame' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.image.AxesImage
        self.FRAMEINST = AF.HDUFrame(self.image,"Hong Kong")
        self.imHDU = pf.ImageHDU
        self.pmHDU = pf.PrimaryHDU
            
        def SAMEDATA(first,second):
            """Return whether these two are the same data"""
            if isinstance(first,np.ndarray) and isinstance(second,np.ndarray):
                return not (np.abs(first-second) > 1e-6).any()
            elif isinstance(first,np.ndarray) or isinstance(second,np.ndarray):
                return False
            else:
                return first == second
        
        def SAME(first,second):
            """Return whether these two are the same"""
            return SAMEDATA(first(),second())
        
        self.SAME = SAME
        self.SAMEDATA = SAMEDATA
        
        self.check_constants()
        
    def test_init_empty(self):
        """__init__() succeeds with empty data"""
        self.FRAME(None,"Label")
        
    def test_save_none(self):
        """__save__() with none object succeeds"""
        self.FRAME.__save__(None,"None")
    
    def test_read_empty_HDU(self):
        """__read__() an empty primary HDU succeeds"""
        HDU = pf.PrimaryHDU()
        AFrame = self.FRAME.__read__(HDU,"Empty")
    
    