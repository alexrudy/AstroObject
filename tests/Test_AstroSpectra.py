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

import AstroObject.AstroSpectra as AS
from AstroObject.Utilities import AbstractError

class test_SpectraFrame(API_Base_Frame):
    """AstroSpectra.SpectraFrame"""
    
    def setUp(self):
        """Sets up the test with some basic image data"""
            
        self.VALID = np.ones((2,100))
        self.FRAME = AS.SpectraFrame
        self.INVALID = 20
        self.FRAMESTR = "<'SpectraFrame' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.artist.Artist
        self.imHDU = pf.ImageHDU
        self.pmHDU = pf.PrimaryHDU
        def SAMEDATA(first,second):
            """Return whether these two are the same data"""
            return not (np.abs(first-second) > 1e-6).any()
            
        
        def SAME(first,second):
            """Return whether these two are the same"""
            return SAMEDATA(first(),second())
        
        self.SAME = SAME
        self.SAMEDATA = SAMEDATA
        
        self.check_constants()
        
        
        
        
class test_SpectraObject(API_Base_Object):
    """AstroSpectra.SpectraObject"""
        
    def setUp(self):
        """Fixture for setting up a basic image frame"""
        self.VALID = np.ones((2,100))
        self.FRAMEINST = AS.SpectraFrame(self.VALID,"Flat")
        self.FRAMELABEL = "Flat"
        self.FRAME = AS.SpectraFrame
        self.HDU = pf.PrimaryHDU(self.VALID)
        self.imHDU = pf.ImageHDU(self.VALID)
        self.INVALID = 20
        self.OBJECTSTR = None
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.artist.Artist
        self.OBJECT = AS.SpectraObject
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
        