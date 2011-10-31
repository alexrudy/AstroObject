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
from nose.plugins.skip import Skip,SkipTest
import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
import os

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


class test_FITSObject(object):
    """Test grouping for testing the fits object"""
    
    def setUp(self):
        """Fixture for setting up a basic image frame"""
        Image = np.ones((100,100))
        Image[45:55,45:55] = np.zeros((10,10))
        self.Frame = AOB.FITSFrame("Empty")
        self.FrameLabel = "Empty"
        self.HDU = pf.PrimaryHDU()
        
    
    @nt.raises(TypeError)
    def test_save_with_data(self):
        """Saving to FITSObject should fail with data"""
        FObject = AOB.FITSObject()
        FObject.save(None)
        
    
    def test_save_with_object(self):
        """Saving to FITSObject should succeed with FITSFrame"""
        FObject = AOB.FITSObject()
        FObject.save(self.Frame)
        assert FObject.statename == self.FrameLabel
        assert isinstance(FObject.object(),AOB.FITSFrame)
    
    def test_save_object_with_label(self):
        """Saving an object with an explicit label should change that object's label"""
        NewLabel = "Other"
        FObject = AOB.FITSObject()
        FObject.save(self.Frame,NewLabel)
        assert FObject.statename == NewLabel
        assert FObject.object().label == NewLabel
        
    
    def test_double_saving_an_object_should_reference(self):
        """Saving the same frame twice should cause referencing"""
        raise SkipTest("This is a bug, should be fixed in a later version.")
        NewLabel = "Other"
        FObject = AOB.FITSObject()
        FObject.save(self.Frame)
        FObject.save(self.Frame,NewLabel)
        assert FObject.statename == NewLabel
        assert FObject.object().label == NewLabel
        FObject.select(self.FrameLabel)
        assert FObject.statename == self.FrameLabel
        assert FObject.object().label == self.FrameLabel
        FObject.select(NewLabel)
        assert FObject.statename == NewLabel
        assert FObject.object().label == NewLabel
        
    
    def test_write_and_read_with_empty_HDU(self):
        """Writing and reading empty HDU"""
        Filename = "TestFile.fits"
        if os.access(Filename,os.F_OK):
            os.remove(Filename)
        FObject = AOB.FITSObject()
        FObject.save(self.Frame)
        FObject.write(Filename)
        assert os.access(Filename,os.F_OK)
        label = FObject.read(Filename)
        assert label == [Filename]
        assert Filename == FObject.statename
        assert isinstance(FObject.object(),AOB.FITSFrame)
        os.remove(Filename)
        
    
    def test_select_aquires_correct_state(self):
        """Select changes to correct state"""
        Label = "Other"
        Frame = AOB.FITSFrame(Label)
        FObject = AOB.FITSObject()
        FObject.save(self.Frame)
        FObject.save(Frame,Label)
        assert FObject.statename == Label
        assert FObject.object().label == Label
        FObject.select(self.FrameLabel)
        assert FObject.statename == self.FrameLabel
        assert FObject.object().label == self.FrameLabel
        
    
    @nt.raises(IndexError)
    def test_select_fails_on_unknown_state(self):
        """Select cannont select non-existant states"""
        FObject = AOB.FITSObject()
        FObject.select(self.FrameLabel)
        
    
    @nt.raises(AbstractError)
    def test_data_raises_abstract_error(self):
        """Data should raise underlying abstract error with frame saved"""
        FObject = AOB.FITSObject()
        FObject.save(self.Frame)
        FObject.data()
        
    
    @nt.raises(KeyError)
    def test_data_raises_key_error(self):
        """Data should raise key error when no data is present"""
        FObject = AOB.FITSObject()
        FObject.data()
        
    
    @nt.raises(KeyError)
    def test_object_raises_key_error(self):
        """Object should raise key error when no data is present"""
        FObject = AOB.FITSObject()
        FObject.object()
        
    
    @nt.raises(KeyError)
    def test_cannot_duplicate_state_name(self):
        """Save should not allow duplication of state name"""
        FObject = AOB.FITSObject()
        FObject.save(self.Frame)
        FObject.save(self.Frame)
    
    def test_list_statenames(self):
        """List should show all statenames"""
        FObject = AOB.FITSObject()
        FObject.save(self.Frame,"A")
        FObject.save(self.Frame,"B")
        assert ["A","B"] == FObject.list()
        
    
    def test_list_should_show_no_statenames(self):
        """Empty object should return no statenames"""
        FObject = AOB.FITSObject()
        assert [] == FObject.list()
        
    def test_remove_should_delete_state(self):
        """Remove Deletes States"""
        FObject = AOB.FITSObject()
        FObject.save(self.Frame,"A")
        FObject.save(self.Frame,"B")
        assert ["A","B"] == FObject.list()
        FObject.remove("A")
        assert ["B"] == FObject.list()
        assert "A" not in FObject.states, "States: %s" % FObject.states
        
    @nt.raises(IndexError)
    def test_cannot_remove_nonexistant_state(self):
        """Cannot Remove Non-Existant State"""
        FObject = AOB.FITSObject()
        FObject.save(self.Frame,"A")
        FObject.remove("B")
        
    
    @nt.raises(KeyError)
    def test_show_should_raise_key_error(self):
        """Show should raise KeyError for an empty object"""
        FObject = AOB.FITSObject()
        FObject.show()
        
    @nt.raises(AbstractError)
    def test_show_should_raise_abstract_error_with_frame(self):
        """Show should call underlying show method, raising an abstract error"""
        FObject = AOB.FITSObject()
        FObject.save(self.Frame)
        FObject.show()

    @nt.raises(KeyError)
    def test_show_should_raise_key_error_with_wrong_statename(self):
        """Show should raise KeyError for a non-existent state name"""
        FObject = AOB.FITSObject()
        FObject.save(self.Frame)
        FObject.show(self.FrameLabel + "JUNK...")























