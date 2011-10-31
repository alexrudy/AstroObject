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

__all__ = ['API_Abstract_Frame','API_Abstract_Object']

class API_Abstract_Frame(object):
    """Tests an Abstract Frame"""
        
    def check_constants(self):
        """API-Based Test Contains Appropriate Constants"""
        passed = True
        attributes = ['FRAME','DATA','INVALID','FRAMESTR']
        for attribute in attributes:
            passed &= hasattr(self,attribute)
            
            
        assert passed
    
    @nt.raises(AbstractError)
    def test_save(self):
        """Save to an abstract base class raises an AbstractError"""
        self.FRAME.__save__(self.DATA,"None")
    
    
    @nt.raises(AbstractError)
    def test_hdu(self):
        """HDU method raises an AbstractError"""
        BFrame = self.FRAME("Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.__hdu__()
    
    @nt.raises(AbstractError)
    def test_primary_hdu(self):
        """HDU primary raises an AbstractError"""
        BFrame = self.FRAME("Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.__hdu__(primary=True)
    
    @nt.raises(AbstractError)
    def test_read_empty_HDU(self):
        """Reads an empty HDU raises an AbstractError"""
        HDU = pf.PrimaryHDU()
        BFrame = self.FRAME.__read__(HDU,"Empty")
        assert isinstance(BFrame,self.FRAME)
        assert BFrame.label == "Empty"
    
    @nt.raises(AbstractError)
    def test_read_image_HDU(self):
        """Read an ImageHDU fails"""
        HDU = pf.ImageHDU()
        self.FRAME.__read__(HDU,"Empty")
    

    @nt.raises(AbstractError)
    def test_read_non_empty_HDU(self):
        """Read a not empty HDU to an abstract base class fails"""
        HDU = pf.PrimaryHDU(self.INVALID)
        BFrame = self.FRAME.__read__(HDU,"Not Empty")
    

    @nt.raises(AbstractError)
    def test_call_should_fail(self):
        """Calling a base frame should raise an AbstractError"""
        BFrame = self.FRAME("Empty")
        assert BFrame.label == "Empty"
        BFrame()
    



    

    @nt.raises(AbstractError)
    def test_show_should_fail(self):
        """Showing a base frame should fail"""
        BFrame = self.FRAME("Empty")
        assert BFrame.label == "Empty"
        BFrame.__show__()

    def test_string_representation(self):
        """String representation"""
        BFrame = self.FRAME("Empty")
        assert BFrame.label == "Empty"
        assert str(BFrame) == self.FRAMESTR


class API_Abstract_Object(object):
    """Tests an Abstract Object"""
    
    
    def check_constants(self):
           """API-Based Test Contains Appropriate Constants"""
           passed = True
           attributes = ['FRAME','DATA','INVALID','OBJECT']
           for attribute in attributes:
               passed &= hasattr(self,attribute)
               
               
           assert passed
    
    @nt.raises(TypeError)
    def test_save_with_data(self):
        """Saving to FITSObject fails with None data"""
        BObject = self.OBJECT()
        BObject.save(None)
        
    
    def test_save_with_object(self):
        """Saving to FITSObject should succeed with FITSFRAME"""
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST)
        assert BObject.statename == self.FRAMELABEL
        assert isinstance(BObject.frame(),self.FRAME)
    
    def test_save_object_with_label(self):
        """Saving an object with an explicit label should change that object's label"""
        NewLabel = "Other"
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST,NewLabel)
        assert BObject.statename == NewLabel
        assert BObject.frame().label == NewLabel
        
    
    def test_double_saving_an_object_should_reference(self):
        """Saving the same frame twice should cause referencing"""
        raise SkipTest("This is a bug, should be fixed in a later version.")
        NewLabel = "Other"
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST)
        BObject.save(self.FRAMEINST,NewLabel)
        assert BObject.statename == NewLabel
        assert BObject.frame().label == NewLabel
        BObject.select(self.FRAMELABEL)
        assert BObject.statename == self.FRAMELABEL
        assert BObject.frame().label == self.FRAMELABEL
        BObject.select(NewLabel)
        assert BObject.statename == NewLabel
        assert BObject.frame().label == NewLabel
        
    
    def test_write_and_read_with_empty_HDU(self):
        """Writing and reading empty HDU"""
        if os.access(self.FILENAME,os.F_OK):
            os.remove(self.FILENAME)
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST)
        BObject.write(self.FILENAME)
        assert os.access(self.FILENAME,os.F_OK)
        label = BObject.read(self.FILENAME)
        assert label == [self.FILENAME]
        assert self.FILENAME == BObject.statename
        assert isinstance(BObject.frame(),self.FRAME)
        os.remove(self.FILENAME)
        
    
    @nt.raises(IOError)
    def test_read_from_nonexistant_file(self):
        """Read should fail on non-existent file"""
        self.FILENAME = "TestFile.fits"
        if os.access(self.FILENAME,os.F_OK):
            os.remove(self.FILENAME)
        AObject = self.OBJECT()
        AObject.read(self.FILENAME)
    
    def test_select_aquires_correct_state(self):
        """Select changes to correct state"""
        Label = "Other"
        FRAME = self.FRAME(Label)
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST)
        BObject.save(FRAME,Label)
        assert BObject.statename == Label
        assert BObject.frame().label == Label
        BObject.select(self.FRAMELABEL)
        assert BObject.statename == self.FRAMELABEL
        assert BObject.frame().label == self.FRAMELABEL
        
    
    @nt.raises(IndexError)
    def test_select_fails_on_unknown_state(self):
        """Select cannont select non-existant states"""
        BObject = self.OBJECT()
        BObject.select(self.FRAMELABEL)
        
    
    @nt.raises(AbstractError)
    def test_data_raises_abstract_error(self):
        """Data should raise underlying abstract error with frame saved"""
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST)
        BObject.data()
        
    
    @nt.raises(KeyError)
    def test_data_raises_key_error(self):
        """Data should raise key error when no data is present"""
        BObject = self.OBJECT()
        BObject.data()
        
    
    @nt.raises(KeyError)
    def test_object_raises_key_error(self):
        """Object should raise key error when no data is present"""
        BObject = self.OBJECT()
        BObject.frame()
        
    
    @nt.raises(KeyError)
    def test_cannot_duplicate_state_name(self):
        """Save should not allow duplication of state name"""
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST)
        BObject.save(self.FRAMEINST)
    
    def test_list_statenames(self):
        """List should show all statenames"""
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST,"A")
        BObject.save(self.FRAMEINST,"B")
        assert ["A","B"] == BObject.list()
        
    
    def test_list_should_show_no_statenames(self):
        """Empty object should return no statenames"""
        BObject = self.OBJECT()
        assert [] == BObject.list()
        
    def test_remove_should_delete_state(self):
        """Remove Deletes States"""
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST,"A")
        BObject.save(self.FRAMEINST,"B")
        assert ["A","B"] == BObject.list()
        BObject.remove("A")
        assert ["B"] == BObject.list()
        assert "A" not in BObject.states, "States: %s" % BObject.states
        
    @nt.raises(IndexError)
    def test_cannot_remove_nonexistant_state(self):
        """Cannot Remove Non-Existant State"""
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST,"A")
        BObject.remove("B")
        
    
    @nt.raises(KeyError)
    def test_show_should_raise_key_error(self):
        """Show should raise KeyError for an empty object"""
        BObject = self.OBJECT()
        BObject.show()
        
    @nt.raises(AbstractError)
    def test_show_should_raise_abstract_error_with_frame(self):
        """Show should call underlying show method, raising an abstract error"""
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST)
        BObject.show()

    @nt.raises(KeyError)
    def test_show_should_raise_key_error_with_wrong_statename(self):
        """Show should raise KeyError for a non-existent state name"""
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST)
        BObject.show(self.FRAMELABEL + "JUNK...")
        
    def test_object_call_exists(self):
        """Depreciated .object() call exists and works."""
        BObject = self.OBJECT()
        BObject.save(self.FRAMEINST)
        assert BObject.object() == BObject.frame()



class test_FITSFrame(API_Abstract_Frame):
    """AstroObjectBase.FITSFrame"""
    def setUp(self):
        self.FRAME = AOB.FITSFrame
        self.FRAMESTR = "<'FITSFrame' labeled 'Empty'>"
        self.DATA = None
        self.INVALID = np.array([1,2,3]).astype(np.int16)
    
        self.check_constants()
    
    def test_hdu(self):
        """Calling the HDU method should generate an empty HDU for primary and non-primary"""
        BFrame = self.FRAME("Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.__hdu__()
        assert isinstance(HDU,pf.ImageHDU)
        assert HDU.data == None
        
    def test_read_empty_HDU(self):
        """Reads an empty HDU"""
        HDU = pf.PrimaryHDU()
        BFrame = self.FRAME.__read__(HDU,"Empty")
        assert isinstance(BFrame,self.FRAME)
        assert BFrame.label == "Empty"
        
    def test_primary_hdu(self):
        """Generates an empty Primary HDU"""
        BFrame = self.FRAME("Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.__hdu__(primary=True)
        assert isinstance(HDU,pf.PrimaryHDU)
        assert HDU.data == None


class test_FITSObject(API_Abstract_Object):
    """AstroObjectBase.FITSObject"""
    def setUp(self):
        self.FILENAME = "TestFile.fits"
        self.FRAME = AOB.FITSFrame
        self.OBJECT = AOB.FITSObject
        self.FRAMESTR = "<'FITSFrame' labeled 'Empty'>"
        self.DATA = None
        self.INVALID = np.array([1,2,3]).astype(np.int16)
        self.FRAMELABEL = "Empty"
        self.FRAMEINST = self.FRAME("Empty")
        self.HDU = pf.PrimaryHDU()
        self.imHDU = pf.ImageHDU()
        self.check_constants()
    
    def tearDown(self):
        """Clean Up!"""
        if os.access(self.FILENAME,os.F_OK):
            os.remove(self.FILENAME)
















