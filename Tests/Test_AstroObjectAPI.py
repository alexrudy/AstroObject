# 
#  Test_AstroObjectAPI.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-31.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 

import AstroObject.AstroObjectBase as AOB
from AstroObject.Utilities import AbstractError
import nose.tools as nt
from nose.plugins.skip import Skip,SkipTest
import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
import os

__all__ = ["API_Base_Frame","API_Base_Object"]

class API_Base_Frame(object):
    """This class implements all of the tests required to ensure that the API is obeyed."""
    def setUp(self):
        self.check_constants()
    
    
    def check_constants(self):
        """API-Based Test Contains Appropriate Constants"""
        passed = True
        attributes = ['FRAME','VALID','INVALID','SAME','SHOWTYPE','HDUTYPE','FRAMESTR']
        for attribute in attributes:
            passed &= hasattr(self,attribute)
            
        assert passed
    
    @nt.raises(AttributeError)
    def test_init_empty(self):
        """__init__ fails without data"""
        self.FRAME(None,"Label")
        
    @nt.raises(Exception)
    def test_init_invalid(self):
        """__init__ fails with invalid data"""
        self.FRAME(self.INVALID,"Invalid")
        
    def test_init_data(self):
        """__init__ succeeds with valid data"""
        AFrame = self.FRAME(self.VALID,"Valid")
        assert AFrame.label == "Valid"
        assert self.SAME(AFrame.data,self.VALID)
    
    @nt.raises(AbstractError)
    def test_save(self):
        """Save an invalid object raises an AbstractError"""
        self.FRAME.__save__(None,"None")
        
    
    def test_save_data(self):
        """Save valid data"""
        AFrame = self.FRAME.__save__(self.VALID,"Valid")
        assert AFrame.label == "Valid"
        assert self.SAME(AFrame.data,self.VALID)
        
    
    def test_read_PrimaryHDU(self):
        """Read an HDU to Frame"""
        HDU = pf.PrimaryHDU(self.VALID)
        AFrame = self.FRAME.__read__(HDU,"Valid")
        assert isinstance(AFrame,self.FRAME)
        assert AFrame.label == "Valid"
        assert self.SAME(AFrame.data,self.VALID)
    
    def test_read_ImageHDU(self):
        """Read an HDU to Frame"""
        HDU = pf.ImageHDU(self.VALID)
        AFrame = self.FRAME.__read__(HDU,"Valid")
        assert isinstance(AFrame,self.FRAME)
        assert AFrame.label == "Valid"
        assert self.SAME(AFrame.data,self.VALID)
        
    
    @nt.raises(AbstractError)
    def test_read_empty_HDU(self):
        """Read an empty HDU to a Frame class fails"""
        HDU = pf.PrimaryHDU()
        AFrame = self.FRAME.__read__(HDU,"Empty")
        
    
    def test_call(self):
        """Calling a frame returns data"""
        AFrame = self.FRAME(self.VALID,"Valid")
        assert AFrame.label == "Valid"
        data = AFrame()
        assert self.SAME(data,self.VALID)


    def test_HDU(self):
        """HDU method generates an  HDU for primary and non-primary"""
        AFrame = self.FRAME(self.VALID,"Valid")
        assert AFrame.label == "Valid"
        HDU = AFrame.__hdu__()
        assert isinstance(HDU,self.HDUTYPE)
        assert self.SAME(HDU.data,self.VALID)
    
    def test_PrimaryHDU(self):
        """docstring for test_PrimaryHDU"""
        AFrame = self.FRAME(self.VALID,"Valid")
        assert AFrame.label == "Valid"
        HDU = AFrame.__hdu__(primary=True)
        assert isinstance(HDU,pf.PrimaryHDU)
        assert self.SAME(HDU.data,self.VALID)


    def test_show(self):
        """Show an ImageFrame should return figure"""
        AFrame = self.FRAME(self.VALID,"Valid")
        assert AFrame.label == "Valid"
        figure = AFrame.__show__()
        assert isinstance(figure,self.SHOWTYPE), "Found type %s" % type(figure)

    def test_string_representation(self):
        """String representation correct for Frame"""
        AFrame = self.FRAME(self.VALID,"Valid")
        assert AFrame.label == "Valid"
        assert str(AFrame) == self.FRAMESTR
        
class API_Base_Object(object):
    """Test grouping for testing the fits object"""
    
    def check_constants(self):
        """API-Based Test Contains Appropriate Constants"""
        passed = True
        attributes = ['FRAMEINST','VALID','INVALID','SAME','SHOWTYPE','HDUTYPE','OBJECTSTR','OBJECT','FRAMELABEL',
        'FRAME','imHDU']
        for attribute in attributes:
            passed &= hasattr(self,attribute)
            
        assert passed
        
    
    @nt.raises(TypeError)
    def test_save_with_none_data(self):
        """Saving to Object fails with none data"""
        AObject = self.OBJECT()
        AObject.save(None)
    
    def test_save_with_data(self):
        """Saving to Object works with image data"""
        AObject = self.OBJECT()
        AObject.save(self.VALID)
        
    @nt.raises(TypeError)
    def test_save_with_invalid_data(self):
        """Saving to Object fails with invalid data"""
        AObject = self.OBJECT()
        AObject.save(self.INVALID)
        
    
    def test_save_with_object(self):
        """Saving to Object should succeed with FRAME"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        assert AObject.statename == self.FRAMELABEL
        assert isinstance(AObject.frame(),self.FRAME)
    
    def test_save_object_with_label(self):
        """Saving an object with an explicit label changes that object's label"""
        NewLabel = "Other"
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,NewLabel)
        assert AObject.statename == NewLabel
        assert AObject.frame().label == NewLabel
        
    
    def test_double_saving_an_object_should_reference(self):
        """Saving the same frame twice should not cause referencing"""
        raise SkipTest("This is a bug, should be fixed in a later version.")
        NewLabel = "Other"
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        AObject.save(self.FRAMEINST,NewLabel)
        assert AObject.statename == NewLabel
        assert AObject.frame().label == NewLabel
        AObject.select(self.FRAMELABEL)
        assert AObject.statename == self.FRAMELABEL
        assert AObject.frame().label == self.FRAMELABEL
        AObject.select(NewLabel)
        assert AObject.statename == NewLabel
        assert AObject.frame().label == NewLabel
        
    
    def test_write_and_read_with_image_HDU(self):
        """Writing and reading empty HDU preserves data"""
        Filename = "TestFile.fits"
        if os.access(Filename,os.F_OK):
            os.remove(Filename)
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        AObject.write(Filename)
        assert os.access(Filename,os.F_OK)
        label = AObject.read(Filename)
        assert label == [Filename]
        assert Filename == AObject.statename
        assert isinstance(AObject.frame(),self.FRAME)
        os.remove(Filename)
        
    
    @nt.raises(IOError)
    def test_read_from_nonexistent_file(self):
        """Read should fail on non-existent file"""
        Filename = "TestFile.fits"
        if os.access(Filename,os.F_OK):
            os.remove(Filename)
        AObject = self.OBJECT()
        AObject.read(Filename)
    
    def test_select_aquires_correct_state(self):
        """Select changes to correct state"""
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
    def test_select_fails_on_unknown_state(self):
        """Select cannont select non-existant states"""
        AObject = self.OBJECT()
        AObject.select(self.FRAMELABEL)
    
    
    def test_data_raises_abstract_error(self):
        """Data should return data object"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        data = AObject.data()
        assert self.SAME(data,self.VALID)
    
    
    @nt.raises(KeyError)
    def test_data_raises_key_error(self):
        """Data should raise key error when no data is present"""
        AObject = self.OBJECT()
        AObject.data()
    
    
    @nt.raises(KeyError)
    def test_object_raises_key_error(self):
        """Object should raise key error when no data is present"""
        AObject = self.OBJECT()
        AObject.frame()
    
    
    @nt.raises(KeyError)
    def test_cannot_duplicate_state_name(self):
        """Save should not allow duplication of state name"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        AObject.save(self.FRAMEINST)
    
    def test_list_statenames(self):
        """List should show all statenames"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,"A")
        AObject.save(self.FRAMEINST,"B")
        assert ["A","B"] == sorted(AObject.list())
    
    
    def test_list_should_show_no_statenames(self):
        """Empty object should return no statenames"""
        AObject = self.OBJECT()
        assert [] == AObject.list()
    
    def test_keep_should_keep_state(self):
        """Keep only a given state"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,"A")
        AObject.save(self.FRAMEINST,"B")
        assert ["A","B"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        AObject.keep("A")
        assert ["A"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        assert "B" not in AObject.states, "States: %s" % AObject.states
        
    
    def test_keep_should_keep_multiple_states(self):
        """Keep a given set of states."""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,"A")
        AObject.save(self.FRAMEINST,"B")
        AObject.save(self.FRAMEINST,"C")
        assert ["A","B","C"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        AObject.keep("A","C")
        assert ["A","C"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        assert "B" not in AObject.states, "States: %s" % AObject.states
    
    @nt.raises(IndexError)
    def test_cannot_keep_non_existant_state(self):
        """Keep fails with non-existent state"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,"A")
        AObject.save(self.FRAMEINST,"B")
        assert ["A","B"] == sorted(AObject.list())
        AObject.keep("C")
    
    def test_remove_should_delete_state(self):
        """Remove Deletes States"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,"A")
        AObject.save(self.FRAMEINST,"B")
        assert ["A","B"] == sorted(AObject.list())
        AObject.remove("A")
        assert ["B"] == sorted(AObject.list())
        assert "A" not in AObject.states, "States: %s" % AObject.states
    
    def test_remove_should_delete_many_states(self):
        """Remove Deletes States"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,"A")
        AObject.save(self.FRAMEINST,"B")
        AObject.save(self.FRAMEINST,"C")
        assert ["A","B","C"] == sorted(AObject.list())
        AObject.remove("A","C")
        assert ["B"] == sorted(AObject.list())
        assert "A" not in AObject.states, "States: %s" % AObject.states
    
    def test_remove_should_leave_object_in_valid_state(self):
        """Remove leaves the object with a valid state selected"""
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST,"A")
        BObject.save(self.FRAMEINST,"B")
        assert ["A","B"] == BObject.list()
        BObject.select("A")
        BObject.remove("A")
        BObject.frame()
    
    @nt.raises(IndexError)
    def test_cannot_remove_nonexistant_state(self):
        """Remove fails with non-existent state"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST,"A")
        AObject.remove("B")
    
    @nt.raises(IndexError)
    def test_cannot_remove_from_empty_object(self):
        """Remove fails with an empty object"""
        AObject = self.OBJECT()
        AObject.remove("B")
    
    @nt.raises(KeyError)
    def test_show_should_raise_key_error(self):
        """Show raises KeyError for an empty object"""
        AObject = self.OBJECT()
        AObject.show()
    
    def test_show_should_complete_and_return_showtype(self):
        """Show calls underlying show method"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        figure = AObject.show()
        assert isinstance(figure,self.SHOWTYPE), "Returned type %s" % type(figure)
    
    @nt.raises(KeyError)
    def test_show_should_raise_key_error_with_wrong_statename(self):
        """Show raises KeyError for a non-existent state name"""
        AObject = self.OBJECT()
        AObject.save(self.FRAMEINST)
        AObject.show(self.FRAMELABEL + "JUNK...")
    

        


