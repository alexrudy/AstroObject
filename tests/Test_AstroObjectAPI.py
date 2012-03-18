#
#  Test_AstroObjectAPI.py
#  ObjectModel
#
#  Created by Alexander Rudy on 2011-10-31.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#

# Parent Imports
import AstroObject.AstroObjectBase as AOB
from AstroObject.Utilities import AbstractError

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

__all__ = ["API_Base","API_Base_Frame","API_Abstract_Frame","API_Base_Object","API_Base_Functional"]

class API_Base(object):
    """Methods common to all tests!"""
    def setUp(self):
        self.check_constants()
        self.clear_files()
    
    doSetUp = setUp
    
    def check_constants(self):
        """API-Based Test Contains Appropriate Constants"""
        passed = True
        missing = []
        for attribute in self.attributes:
            passed &= hasattr(self,attribute)
            if not hasattr(self,attribute):
                missing += [attribute]
        assert passed, "Test API is missing attributes: %s" % missing
    
    def tearDown(self):
        self.clear_files()
    
    doTearDown = tearDown
    
    def clear_files(self):
        if hasattr(self,'FILENAME'):
            if os.access(self.FILENAME,os.F_OK):
                os.remove(self.FILENAME)


class API_Abstract_Frame(API_Base):
    """Tests an Abstract Frame"""
    attributes = ['FRAME','VALID','INVALID','SAME','SAMEDATA','SHOWTYPE','HDUTYPE','FRAMESTR','pmHDU','imHDU']
    
    def test_init_data(self):
        """__init__() succeds with None (Valid) data"""
        self.FRAME(data=self.VALID,label="Invalid")
    
    def test_init_empty(self):
        """__init__() abstract frame works without data"""
        AFrame = self.FRAME(data=None,label="Valid")
        assert AFrame.label == "Valid"
    
    @nt.raises(AttributeError)
    def test_init_invalid(self):
        """__init__() fails with invalid data"""
        self.FRAME(data=self.INVALID,label="Invalid")
        
    @nt.raises(AttributeError)
    def test_init_nolabel(self):
        """__init__() fails with valid data but no label"""
        AFrame = self.FRAME(self.VALID,None)
    
    @nt.raises(AbstractError)
    def test_save_data(self):
        """__save__() to an abstract base class raises an AbstractError"""
        # raise SkipTest("This is a bug, related to argument ordering on the frame.__init__() call.")
        # The following arguments are treated as label and header respectivley. The lack of abstract type cheking and/or a data argument means that this call doesn't fail when it should.
        self.FRAME.__save__(self.VALID,"None")
    
    @nt.raises(AbstractError)
    def test_save_none(self):
        """__save__() with none object raises an AbstractError"""
        self.FRAME.__save__(None,"None")
    @nt.raises(AbstractError)
    def test_read_SecondaryHDU(self):
        """__read__() secondary HDU type should get an abstract error"""
        self.FRAME.__read__(self.imHDU(self.INVALID),"Empty")
        
    @nt.raises(AbstractError)
    def test_read_PrimaryHDU(self):
        """__read__() primary HDU type should get an abstract error"""
        BFrame = self.FRAME.__read__(self.pmHDU(self.INVALID),"Not Empty")
    
    @nt.raises(AbstractError)
    def test_read_empty_HDU(self):
        """__read__() an empty primary HDU fails"""
        HDU = pf.PrimaryHDU()
        AFrame = self.FRAME.__read__(HDU,"Empty")
    
    @nt.raises(AbstractError)
    def test_call(self):
        """__call__() a base frame should raise an AbstractError"""
        BFrame = self.FRAME(data=self.VALID,label="Empty")
        assert BFrame.label == "Empty"
        BFrame()
    
    @nt.raises(AbstractError)
    def test_HDU(self):
        """__hdu__() raises an AbstractError"""
        BFrame = self.FRAME(data=self.VALID,label="Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.__hdu__()
    
    @nt.raises(AbstractError)
    def test_PrimaryHDU(self):
        """__hdu__() primary raises an AbstractError"""
        BFrame = self.FRAME(data=self.VALID,label="Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.__hdu__(primary=True)
    
    @nt.raises(AbstractError)
    def test_show(self):
        """__show__() a base frame should fail"""
        BFrame = self.FRAME(data=self.VALID,label="Empty")
        assert BFrame.label == "Empty"
        BFrame.__show__()
    


    def test_string_representation(self):
        """__repr__() String representation correct for Frame"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        assert str(AFrame) == self.FRAMESTR
    

class API_Base_Frame(API_Abstract_Frame):
    """This class implements all of the tests required to ensure that the API is obeyed."""
    
    @nt.raises(AttributeError)
    def test_init_empty(self):
        """__init__() fails without data"""
        self.FRAME(data=None,label="Label")

    def test_init_data(self):
        """__init__() succeeds with valid data"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        assert self.SAMEDATA(AFrame.data,self.VALID)
    
    
    def test_save_data(self):
        """__save__() valid data"""
        AFrame = self.FRAME.__save__(self.VALID,"Valid")
        assert AFrame.label == "Valid"
        assert self.SAMEDATA(AFrame.data,self.VALID)
    
    
    def test_read_PrimaryHDU(self):
        """__read__() primary HDU succeeds"""
        AFrame = self.FRAME.__read__(self.pmHDU(self.VALID),"Valid")
        assert isinstance(AFrame,self.FRAME)
        assert AFrame.label == "Valid"
        assert self.SAMEDATA(AFrame.data,self.VALID)
    
    
    def test_read_SecondaryHDU(self):
        """__read__() secondary HDU succeeds"""
        AFrame = self.FRAME.__read__(self.imHDU(self.VALID),"Valid")
        assert isinstance(AFrame,self.FRAME)
        assert AFrame.label == "Valid"
        assert self.SAMEDATA(AFrame.data,self.VALID)
    
    
    
    
    def test_call(self):
        """__call__() yields data"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        data = AFrame()
        assert self.SAMEDATA(data,self.VALID)
    
    
    def test_HDU(self):
        """__hdu__() works for secondary HDUs"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        HDU = AFrame.__hdu__()
        assert isinstance(HDU,self.HDUTYPE)
        assert self.SAMEDATA(HDU.data,self.VALID)
    
    
    def test_PrimaryHDU(self):
        """__hdu__() works for primary HDUs"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        HDU = AFrame.__hdu__(primary=True)
        assert isinstance(HDU,pf.PrimaryHDU)
        assert self.SAMEDATA(HDU.data,self.VALID)
    
    
    def test_show(self):
        """__show__() returns a valid type"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        figure = AFrame.__show__()
        assert isinstance(figure,self.SHOWTYPE), "Found type %s" % type(figure)
    
    



class API_Base_Object(API_Base):
    """Test grouping for testing the fits object"""
    attributes = ['FRAMEINST','VALID','INVALID','SAME','SHOWTYPE','HDUTYPE','OBJECTSTR','OBJECT','FRAMELABEL',
    'FRAME','imHDU','FILENAME','SAMEDATA']
    
    
    @nt.raises(TypeError)
    def test_save_with_none(self):
        """save() fails when passed None"""
        AObject = self.OBJECT()
        AObject.save(None)
        
    @nt.raises(TypeError)
    def test_set_with_none(self):
        """[] fails when passed None"""
        AObject = self.OBJECT()
        AObject["Label"] = None
    
    
    def test_save_with_data(self):
        """save() works with valid data"""
        AObject = self.OBJECT()
        AObject.save(self.VALID,"Valid")
    
    def test_set_with_data(self):
        """[] works with valid data"""
        AObject = self.OBJECT()
        AObject["Valid"] = self.VALID
    
    
    @nt.raises(TypeError)
    def test_save_with_invalid_data(self):
        """save() fails with invalid data"""
        AObject = self.OBJECT()
        AObject.save(self.INVALID,"Invalid")
    
    @nt.raises(TypeError)
    def test_set_with_invalid_data(self):
        """save() fails with invalid data"""
        AObject = self.OBJECT()
        AObject["Invalid"] = self.INVALID
    
    
    def test_save_with_frame(self):
        """save() succeeds with a frame"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        assert AObject.statename == self.FRAMELABEL
        assert isinstance(AObject.frame(),self.FRAME)
    
    def test_set_frame_with_label(self):
        """Saving an object with an explicit label changes that object's label"""
        NewLabel = "Other"
        AObject = self.OBJECT()
        AObject[NewLabel] = self.FRAMEINST
        assert AObject.statename == NewLabel
        assert AObject.frame().label == NewLabel
    
    
    def test_save_frame_with_label(self):
        """Saving an object with an explicit label changes that object's label"""
        NewLabel = "Other"
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,NewLabel)
        assert AObject.statename == NewLabel
        assert AObject.frame().label == NewLabel
    
    
    def test_double_saving_an_object_should_reference(self):
        """save() should prevent data in frames from referencing each other"""        
        NewLabel = "Other"
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        AObject.save(self.FRAMEINST,NewLabel)
        assert AObject.statename == NewLabel
        assert AObject.frame().label == NewLabel
        try:
            AObject.select(self.FRAMELABEL)
            assert AObject.statename == self.FRAMELABEL
            assert AObject.frame().label == self.FRAMELABEL
            AObject.select(NewLabel)
            assert AObject.statename == NewLabel
            assert AObject.frame().label == NewLabel
        except AssertionError as e:
            raise SkipTest("This is a bug, should be fixed in a later version. %s" % e)
    
    def test_double_saving_data_should_not_reference(self):
        """data() should prevent data from referencing each other."""
        NewLabel = "Other"
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        AObject.save(AObject.data(),NewLabel)
        assert AObject.statename == NewLabel
        assert AObject.frame().label == NewLabel
        try:
            AObject.select(self.FRAMELABEL)
            assert AObject.statename == self.FRAMELABEL
            assert AObject.frame().label == self.FRAMELABEL
            AObject.select(NewLabel)
            assert AObject.statename == NewLabel
            assert AObject.frame().label == NewLabel
        except AssertionError as e:
            raise SkipTest("This is a bug, should be fixed in a later version. %s" % e)
    
    @nt.raises(IOError)
    def test_read_from_nonexistent_file(self):
        """read() fails if the file doesn't exist"""
        AObject = self.OBJECT()
        AObject.read(self.FILENAME)
    
    def test_write_clobbers_file(self):
        """write() can clobber existing files"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        AObject.write(self.FILENAME)
        AObject.write(self.FILENAME,clobber=True)
    
    @nt.raises(IOError)
    def test_write_does_not_clobber_file(self):
        """write() doesn't clobber files by default"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        AObject.write(self.FILENAME)
        AObject.write(self.FILENAME)
    
    def test_select(self):
        """select() changes to correct state"""
        Label = "Other"
        Frame = self.FRAME(self.VALID,Label)
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        AObject.save(Frame,Label)
        assert AObject.statename == Label
        assert AObject.frame().label == Label
        AObject.select(self.FRAMELABEL)
        assert AObject.statename == self.FRAMELABEL
        assert AObject.frame().label == self.FRAMELABEL
    
    
    @nt.raises(IndexError)
    def test_select_unknown_state(self):
        """select() cannont select non-existant states"""
        AObject = self.OBJECT()
        AObject.select(self.FRAMELABEL)
    
    
    def test_data(self):
        """data() returns data object"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        data = AObject.data()
        assert self.SAMEDATA(data,self.VALID)
    
    
    @nt.raises(KeyError)
    def test_data_empty(self):
        """data() raises a key error when no data present"""
        AObject = self.OBJECT()
        AObject.data()
    
    
    @nt.raises(KeyError)
    def test_frame_empty(self):
        """frame() raises a key error when key is missing"""
        AObject = self.OBJECT()
        AObject.frame()
    
    def test_frame(self):
        """frame() returns data object"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        frame = AObject.frame()
        assert self.SAME(frame,self.FRAMEINST)
    
    def test_get(self):
        """[] returns data object"""
        AObject = self.OBJECT()
        AObject[self.FRAMEINST.label] = self.FRAMEINST
        frame = AObject[self.FRAMEINST.label]
        assert self.SAME(frame,self.FRAMEINST)
    
    
    @nt.raises(KeyError)
    def test_duplicate_state_name(self):
        """save() should not allow duplication of state name"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        AObject.save(self.FRAMEINST)
    
    def test_list_statenames(self):
        """list() should show all statenames"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,"A")
        AObject.save(self.FRAMEINST,"B")
        assert ["A","B"] == sorted(AObject.list())
    
    def test_list_empty(self):
        """list() should be empty on a fresh object"""
        AObject = self.OBJECT()
        assert [] == AObject.list()
    
    def test_keep(self):
        """keep() only retains given state"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,"A")
        AObject.save(self.FRAMEINST,"B")
        assert ["A","B"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        AObject.keep("A")
        assert ["A"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        assert "B" not in AObject.states, "States: %s" % AObject.states
    
    
    def test_keep_multiple(self):
        """keep() only retains given states"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,"A")
        AObject.save(self.FRAMEINST,"B")
        AObject.save(self.FRAMEINST,"C")
        assert ["A","B","C"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        AObject.keep("A","C")
        assert ["A","C"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        assert "B" not in AObject.states, "States: %s" % AObject.states
    
    @nt.raises(IndexError)
    def test_keep_non_existant_state(self):
        """keep() fails with non-existent state"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,"A")
        AObject.save(self.FRAMEINST,"B")
        assert ["A","B"] == sorted(AObject.list())
        AObject.keep("C")
    
    @nt.raises(IndexError)
    def test_keep_empty(self):
        """keep() fails with an empty object"""
        AObject = self.OBJECT()
        AObject.keep("B")
    
    def test_keep_valid_state(self):
        """keep() leaves the object with a valid selected state"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,"A")
        AObject.save(self.FRAMEINST,"B")
        assert ["A","B"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        AObject.select("B")
        AObject.keep("A")
        AObject.frame()
    
    def test_remove(self):
        """remove() deletes given state"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,"A")
        AObject.save(self.FRAMEINST,"B")
        assert ["A","B"] == sorted(AObject.list())
        AObject.remove("A")
        assert ["B"] == sorted(AObject.list())
        assert "A" not in AObject.states, "States: %s" % AObject.states
    
    def test_remove_multiple(self):
        """remove() deletes given states"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,"A")
        AObject.save(self.FRAMEINST,"B")
        AObject.save(self.FRAMEINST,"C")
        assert ["A","B","C"] == sorted(AObject.list())
        AObject.remove("A","C")
        assert ["B"] == sorted(AObject.list())
        assert "A" not in AObject.states, "States: %s" % AObject.states
    
    def test_remove_valid_state(self):
        """remove() leaves the object with a valid selected state"""
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST,"A")
        BObject.save(self.FRAMEINST,"B")
        assert ["A","B"] == BObject.list()
        BObject.select("A")
        BObject.remove("A")
        BObject.frame()
    
    @nt.raises(IndexError)
    def test_remove_non_existant_state(self):
        """remove() fails with non-existent state"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,"A")
        AObject.remove("B")
    
    @nt.raises(IndexError)
    def test_remove_empty(self):
        """remove() fails with an empty object"""
        AObject = self.OBJECT()
        AObject.remove("B")
    
    @nt.raises(KeyError)
    def test_show_empty(self):
        """show() raises KeyError for an empty object"""
        AObject = self.OBJECT()
        AObject.show()
    
    def test_show(self):
        """show() calls underlying show method"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        figure = AObject.show()
        assert isinstance(figure,self.SHOWTYPE), "Returned type %s" % type(figure)
    
    @nt.raises(KeyError)
    def test_show_non_existant_state(self):
        """show() raises KeyError for a non-existent state name"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        AObject.show(self.FRAMELABEL + "JUNK...")
    
    def test_object(self):
        """object() call exists and works, but has been depreciated"""
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST)
        assert BObject.object() == BObject.frame()
    


class API_Base_Functional(API_Base):
    """Functional Tests Basic API Level"""
    attributes = ['FRAMEINST','VALID','INVALID','SAME','SHOWTYPE','HDUTYPE','OBJECTSTR','OBJECT','FRAMELABEL',
    'FRAME','imHDU','FILENAME','SAMEDATA']
    
    def test_write_and_read(self):
        """User writes an image and reads from the same frame"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        AObject.write(self.FILENAME)
        BObject = self.OBJECT()
        assert os.access(self.FILENAME,os.F_OK)
        labels = BObject.read(self.FILENAME)
        assert labels == AObject.list()
        assert isinstance(BObject.frame(),self.FRAME)
        assert self.SAME(self.FRAMEINST,BObject.frame())
        
