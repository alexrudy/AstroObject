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

from Test_AstroObjectAPI import *

import AstroImage as AI
import AstroObjectBase as AOB
from Utilities import AbstractError

class test_ImageFrame(object):
    """Tests the functions of Image Frame"""
    
    def setUp(self):
        """Sets up the test with some basic image data"""
        self.testJPG = "Tests/Hong-Kong.jpg"
        if not os.access(self.testJPG,os.R_OK):
            self.image = np.zeros((1000,1000))
            self.image[450:550,450:550] = np.ones((100,100))
        else:
            self.image = np.int32(np.sum(mpimage.imread(self.testJPG),axis=2))
        
    
    @nt.raises(AttributeError)
    def test_init_empty(self):
        """Cannot initialize an ImageFrame without data"""
        AI.ImageFrame(None,"Label")
        
    def test_init_data(self):
        """Frame initializes with data"""
        IFrame = AI.ImageFrame(self.image,"Hong Kong")
        assert IFrame.label == "Hong Kong"
    
    @nt.raises(AbstractError)
    def test_save_to_image(self):
        """Save an invalid object should raise an error"""
        AI.ImageFrame.__save__(None,"None")
        
        
    def test_save_data(self):
        """Save an image-like np.array should work"""
        IFrame = AI.ImageFrame.__save__(self.image,"Hong Kong")
        assert IFrame.label == "Hong Kong"
        assert not (np.abs(IFrame.data - self.image) > 1e-6).any()
    
    def test_save_many_dimensions(self):
        """Save a multidimensional image should work"""
        image = np.zeros((100,100,100))
        IFrame = AI.ImageFrame.__save__(image,"3D")
        assert IFrame.label == "3D"
        assert not (np.abs(IFrame.data - image) > 1e-6).any() 
    
    
    def test_read_grayscale_HDU(self):
        """Read an image HDU to ImageFrame should succeed"""
        HDU = pf.PrimaryHDU(self.image)
        IFrame = AI.ImageFrame.__read__(HDU,"Hong Kong")
        assert isinstance(IFrame,AI.ImageFrame)
        assert IFrame.label == "Hong Kong"
        assert not (np.abs(IFrame.data - self.image) > 1e-6).any()


    @nt.raises(AbstractError)
    def test_read_empty_HDU(self):
        """Read an empty HDU to an ImageFrame class should fail"""
        HDU = pf.PrimaryHDU()
        FFrame = AI.ImageFrame.__read__(HDU,"Empty")
        
    
    def test_call_should_return_data(self):
        """Calling a base frame should raise an abstract error"""
        IFrame = AI.ImageFrame(self.image,"Hong Kong")
        assert IFrame.label == "Hong Kong"
        data = IFrame()
        assert not (np.abs(data - self.image) > 1e-6).any() 



    def test_hdu_generates_image_hdu(self):
        """HDU method should generate an image HDU for primary and non-primary"""
        IFrame = AI.ImageFrame(self.image,"Hong Kong")
        assert IFrame.label == "Hong Kong"
        HDU = IFrame.__hdu__()
        assert isinstance(HDU,pf.ImageHDU)
        assert not (np.abs(HDU.data - self.image) > 1e-6).any() 
        HDU = IFrame.__hdu__(primary=True)
        assert isinstance(HDU,pf.PrimaryHDU)
        assert not (np.abs(HDU.data - self.image) > 1e-6).any() 


    def test_show_should_return_figure(self):
        """Show an ImageFrame should return figure"""
        IFrame = AI.ImageFrame(self.image,"Hong Kong")
        assert IFrame.label == "Hong Kong"
        figure = IFrame.__show__()
        assert isinstance(figure,mpl.image.AxesImage)

    def test_string_representation(self):
        """String representation correct for ImageFrame"""
        IFrame = AI.ImageFrame(self.image,"Hong Kong")
        assert IFrame.label == "Hong Kong"
        assert str(IFrame) == "<'ImageFrame' labeled 'Hong Kong'>"

class test_ImageFrame_API(API_Base_Frame):
    """docstring for test_ImageFrame_API"""
    def setUp(self):
        """Sets up the test with some basic image data"""
        self.testJPG = "Tests/Hong-Kong.jpg"
        if not os.access(self.testJPG,os.R_OK):
            self.image = np.zeros((1000,1000))
            self.image[450:550,450:550] = np.ones((100,100))
        else:
            self.image = np.int32(np.sum(mpimage.imread(self.testJPG),axis=2))
            
        self.VALID = self.image
        self.FRAME = AI.ImageFrame
        self.INVALID = 20
        self.FRAMESTR = "<'ImageFrame' labeled 'Hong Kong'>"
        
        def SAME(self,first,second):
            """Return whether these two are the same"""
            return not (np.abs(first,second) > 1e-6).any() 

                
        
class test_FITSObject(object):
    """Test grouping for testing the fits object"""

    def setUp(self):
        """Fixture for setting up a basic image frame"""
        self.testJPG = "Tests/Hong-Kong.jpg"
        if not os.access(self.testJPG,os.R_OK):
            self.image = np.zeros((1000,1000))
            self.image[450:550,450:550] = np.ones((100,100))
        else:
            self.image = np.int32(np.sum(mpimage.imread(self.testJPG),axis=2))
        self.Frame = AI.ImageFrame(self.image,"Hong Kong")
        self.FrameLabel = "Hong Kong"
        self.HDU = pf.PrimaryHDU(self.image)
        self.imHDU = pf.ImageHDU(self.image)
        
    
    @nt.raises(TypeError)
    def test_save_with_bad_data(self):
        """Saving to ImageObject should fail with none data"""
        IObject = AI.ImageObject()
        IObject.save(None)
        
    def test_save_with_data(self):
        """Saving to ImageObject should work with image data"""
        IObject = AI.ImageObject()
        IObject.save(self.image)


    def test_save_with_object(self):
        """Saving to ImageObject should succeed with FITSFrame"""
        IObject = AI.ImageObject()
        IObject.save(self.Frame)
        assert IObject.statename == self.FrameLabel
        assert isinstance(IObject.object(),AI.ImageFrame)

    def test_save_object_with_label(self):
        """Saving an object with an explicit label should change that object's label"""
        NewLabel = "Other"
        IObject = AI.ImageObject()
        IObject.save(self.Frame,NewLabel)
        assert IObject.statename == NewLabel
        assert IObject.object().label == NewLabel


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

    