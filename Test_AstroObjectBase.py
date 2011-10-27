# 
#  Test_AstroObjectBase.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-28.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 

import AstroObjectBase as AOB
from Utilities import AbstractError
import nose.tools as nt
import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt

class test_FITSFrame(object):
    """Test grouping for those tests which apply to the basic FITS Frame"""
        
    @nt.raises(AbstractError)
    def test_save(self):
        """Attempting to save to an abstract base class should raise an error"""
        AOB.FITSFrame.__save__(None,"None")


    def test_read_empty_HDU(self):
        """Attempting to read an empty HDU to an abstract base class should succeed"""
        HDU = pf.PrimaryHDU()
        FFrame = AOB.FITSFrame.__read__(HDU,"Empty")
        assert isinstance(FFrame,AOB.FITSFrame)
        assert FFrame.label == "Empty"
    

    @nt.raises(AbstractError)
    def test_read_non_empty_HDU(self):
        """Attempting to read an not empty HDU to an abstract base class should fail"""
        HDU = pf.PrimaryHDU(np.array([1,2,3]).astype(np.int16))
        FFrame = AOB.FITSFrame.__read__(HDU,"Not Empty")
    

    @nt.raises(AbstractError)
    def test_call_should_fail(self):
        """Calling a base frame should raise an abstract error"""
        FFrame = AOB.FITSFrame("Empty")
        assert FFrame.label == "Empty"
        FFrame()
    


    def test_hdu_generates_empty_hdu(self):
        """Calling the HDU method should generate an empty HDU for primary and non-primary"""
        FFrame = AOB.FITSFrame("Empty")
        assert FFrame.label == "Empty"
        HDU = FFrame.__hdu__()
        assert isinstance(HDU,pf.ImageHDU)
        assert HDU.data == None
        HDU = FFrame.__hdu__(primary=True)
        assert isinstance(HDU,pf.PrimaryHDU)
        assert HDU.data == None
    

    @nt.raises(AbstractError)
    def test_show_should_fail(self):
        """Attempting to show a base frame should fail"""
        FFrame = AOB.FITSFrame("Empty")
        assert FFrame.label == "Empty"
        FFrame.__show__()

    def test_string_representation(self):
        """Confirm the desired string representation"""
        FFrame = AOB.FITSFrame("Empty")
        assert FFrame.label == "Empty"
        assert str(FFrame) == "<'FITSFrame' labeled 'Empty'>"



