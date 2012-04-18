# -*- coding: utf-8 -*-
# 
#  Test_AstroSpectra.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-31.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.4.0
# 

import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimage
import matplotlib.axes

import os

import nose.tools as nt
from nose.plugins.skip import Skip,SkipTest

from tests.AstroTest import *

import AstroObject.AstroSpectra

class equality_SpectraFrame(equality_Base):
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

        
class test_SpectraFrame(equality_SpectraFrame,API_General_Frame):
    """AstroSpectra.SpectraFrame"""
    
    def setup(self):
        """Fixture for setting up a basic image frame"""
        self.files = ["TestFile.fits"]
        self.FRAME = AstroObject.AstroSpectra.SpectraFrame
        self.HDU = pf.PrimaryHDU
        self.imHDU = pf.ImageHDU
        self.VALID = np.array([(np.arange(50) + 1.0) * 1e-7,np.sin(np.arange(50))+2.0])
        self.INVALID = 20
        self.OBJECTSTR = None
        self.FRAMESTR = "<'SpectraFrame' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.axes.Subplot
        self.RKWARGS = {}
        super(test_SpectraFrame, self).setup()
    
        
        
class test_SpectraObject(equality_SpectraFrame,API_Base_Object):
    """AstroSpectra.SpectraObject"""
        
    def setup(self):
        """Fixture for setting up a basic image frame"""
        self.files = ["TestFile.fits"]
        self.FRAME = AstroObject.AstroSpectra.SpectraFrame
        self.VALID = np.array([(np.arange(50) + 1.0) * 1e-7,np.sin(np.arange(50))+2.0])
        self.INVALID = 20
        self.OBJECTSTR = None
        self.FRAMESTR = "<'ImageFrame' labeled 'Valid'>"
        self.HDUTYPE = pf.ImageHDU
        self.SHOWTYPE = mpl.axes.Subplot
        self.OBJECT = AstroObject.AstroSpectra.SpectraObject
        super(test_SpectraObject, self).setup()
    
        
