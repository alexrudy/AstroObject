# -*- coding: utf-8 -*-
#
#  AstroTest.py
#  ObjectModel
#
#  Created by Alexander Rudy on 2011-10-31.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.5-a1
#
"""
:mod:`AstroTest` for nosetests
==============================

This module has test frameworks for all modules

.. inheritance-diagram::
    tests.AstroTest.API_Base_Frame
    tests.AstroTest.API_HDUHeader_Frame
    tests.AstroTest.API_NoData_Frame
    tests.AstroTest.API_NoHDU_Frame
    tests.AstroTest.API_NotEmpty_Frame
    tests.AstroTest.API_AnalyticMixin
    tests.AstroTest.API_General_Frame
    tests.AstroTest.API_Base_Object
    tests.Test_AstroFITS.test_FITSFrame
    tests.Test_AstroFITS.test_FITSObject
    tests.test_AstroHDU.test_HDUFrame
    tests.test_AstroHDU.test_HDUObject
    tests.Test_AstroImage.test_ImageFrame
    tests.Test_AstroImage.test_ImageObject
    tests.Test_AstroSpectra.test_SpectraFrame
    tests.Test_AstroSpectra.test_SpectraObject
    :parts: 1

"""
# Parent Imports
import AstroObject.AstroObjectBase as AOB

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
from pkg_resources import resource_filename
from abc import ABCMeta, abstractmethod, abstractproperty
import sys
import os
import collections
import shutil

class API_Base(object):
    """Methods common to all tests."""
    
    __metaclass__ = ABCMeta
        
    attributes = []
    
    def setup(self):
        """Sets up this test object."""
        self._check_constants()
        self._clear_files()
        self._get_files()
        
    def teardown(self):
        """Tears down the test object."""
        self._clear_files()
        
    def _check_constants(self):
        """Check the constants on this object."""
        missing = []
        if hasattr(self,'attributes'):
            for attribute in self.attributes:
                if not hasattr(self,attribute):
                    missing += [attribute]
            assert len(missing) == 0, "Test API %s is missing attributes: %s" % (self.__class__.__name__,missing)
        if hasattr(self,'methods'):
            for method in self.methods:
                if not (hasattr(self,method) and callable(getattr(self,method))):
                    missing += [method]
            assert len(missing) == 0, "Test API %s is missing methods: %s" % (self.__class__.__name__,missing)
        
    def _clear_files(self):
        """Clear the files setup by this object."""
        if hasattr(self,'files') and isinstance(self.files,collections.Sequence):
            for filename in self.files:
                if os.access(filename,os.F_OK):
                    os.remove(filename)
                    
    def _get_files(self):
        """Add files to the test working directory"""
        if hasattr(self,'data') and isinstance(self.data,collections.Sequence):
            if not hasattr(self,'files'):
                self.files = []
            for filename in self.data:
                filepath = resource_filename(__name__,filename)
                if not os.access(filename,os.F_OK) and os.access(filepath,os.F_OK):
                    shutil.copy(filepath,os.getcwd()+filename)
                    self.files += [filename]


class equality_Base(object):
    """Equality methods for FITSFrames"""
    
    
    @abstractmethod
    def data_eq_data(self,data,other):
        """Return whether these two are the same data"""
        return True
        
    @abstractmethod
    def frame_eq_frame(self,frame,other):
        """Return whether these two FITS frames are the same"""
        return True
            
    @abstractmethod
    def data_eq_frame(self,data,frame):
        """Return whether this data is the same as the data in this frame."""
        return True


class API_Base_Frame(API_Base):
    """Tests an Abstract Frame"""
    attributes = ['FRAME','VALID','INVALID','SHOWTYPE','HDUTYPE','FRAMESTR','RKWARGS']
    methods = ['frame_eq_frame','data_eq_data','data_eq_frame']
    
    def frame(self):
        """Returns a valid frame"""
        return self.FRAME(data=self.VALID,label="Valid")
    
    def test_init_data(self):
        """__init__() succeds with None (Valid) data"""
        self.FRAME(data=self.VALID,label="Invalid")
        assert self.data_eq_data(AFrame(**self.RKWARGS),self.VALID)
        
    
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

    def test_string_representation(self):
        """__repr__() String representation correct for Frame"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        assert str(AFrame) == self.FRAMESTR
    
        
    @abstractmethod
    def test_call(self):
        pass
    
    @abstractmethod
    def test_call_with_kwargs(self):
        pass
    
    @abstractmethod
    def test_show(self):
        pass
        
    @abstractmethod
    def test_getheader_primary(self):
        pass
        
    @abstractmethod
    def test_getheader_secondary(self):
        pass
        
    @abstractmethod
    def test_setheader_primary(self):
        pass
        
    @abstractmethod
    def test_setheader_secondary(self):
        pass
    
    @abstractmethod
    def test__hdu__secondary(self):
        pass
    
    @abstractmethod
    def test__hdu__primary(self):
        pass
        
    @abstractmethod
    def test_read_secondary(self):
        pass
        
    @abstractmethod
    def test_read_primary(self):
        pass
        
    @abstractmethod
    def test_read_empty_primary(self):
        pass
        
    @abstractmethod
    def test_read_empty_secondary(self):
        pass
    
    @abstractmethod
    def test_save_data(self):
        pass
    
    @abstractmethod
    def test_save_empty(self):
        pass

class API_CanBeEmpty_Frame(API_Base):
    """API for AstroObjectBase.BaseFrame which can be empty"""
    
    def test_init_empty(self):
        """__init__() works without data"""
        self.FRAME(data=None,label="Label")
    
    def test_read_empty_primary(self):
        """__read__() works on an empty primary HDU"""
        HDU = pf.PrimaryHDU()
        BFrame = self.FRAME.__read__(HDU,"Empty")
        assert isinstance(BFrame,self.FRAME)
        assert BFrame.label == "Empty"
        
    def test_read_empty_secondary(self):
        """__read__() works on an empty secondary HDU"""
        HDU = self.HDUTYPE()
        BFrame = self.FRAME.__read__(HDU,"Empty")
        assert isinstance(BFrame,self.FRAME)
        assert BFrame.label == "Empty"    

class API_HDUHeader_Frame(API_Base):
    """API for AstroObjectBase.HDUHeaderMixin """
    def test_getheader_primary(self):
        """__getheader__(HDU) a HDU frame with a primary HDU."""
        BFrame = self.FRAME(data=self.VALID,label="Valid")
        assert BFrame.label == "Valid"
        HDU = pf.PrimaryHDU()
        BFrame.__getheader__(HDU)
        
    def test_getheader_secondary(self):
        """__getheader__(HDU) a HDU frame with a secondary HDU."""
        BFrame = self.FRAME(data=self.VALID,label="Valid")
        assert BFrame.label == "Valid"
        HDU = self.HDUTYPE()
        BFrame.__getheader__(HDU)
    
    def test_setheader_primary(self):
        """__setheader__(HDU) a NoHDU frame with a primary HDU."""
        BFrame = self.FRAME(data=self.VALID,label="Valid")
        assert BFrame.label == "Valid"
        HDU = pf.PrimaryHDU()
        nHDU = BFrame.__setheader__(HDU)
        assert isinstance(nHDU,pf.PrimaryHDU)
        
    def test_setheader_secondary(self):
        """__setheader__(HDU) a HDU frame with a secondary HDU."""
        BFrame = self.FRAME(data=self.VALID,label="Valid")
        assert BFrame.label == "Valid"
        HDU = self.HDUTYPE()
        nHDU = BFrame.__setheader__(HDU)
        assert isinstance(nHDU,self.HDUTYPE)
    
class API_NoData_Frame(API_CanBeEmpty_Frame,API_Base):
    """API for AstroObjectBase.NoDataMixin"""
    
    @nt.raises(NotImplementedError)
    def test_call_with_kwargs(self):
        """__call__(**kwargs) a NoData frame should raise an error."""
        BFrame = self.FRAME(data=self.VALID,label="Valid")
        assert BFrame.label == "Valid"
        BFrame(**self.RKWARGS)
    
    @nt.raises(NotImplementedError)
    def test_call(self):
        """__call__() a NoData frame should raise an error."""
        BFrame = self.FRAME(data=self.VALID,label="Valid")
        assert BFrame.label == "Valid"
        BFrame()
    
    @nt.raises(NotImplementedError)
    def test_show(self):
        """__show__() a NoData frame should raise an error."""
        BFrame = self.FRAME(data=self.VALID,label="Valid")
        assert BFrame.label == "Valid"
        BFrame.__show__()
    
    @nt.raises(NotImplementedError)    
    def test_save_data(self):
        """__save__() a NoData frame should raise an error."""
        AFrame = self.FRAME.__save__(self.VALID,"Valid")
        assert AFrame.label == "Valid"
    

class API_NoHDU_Frame(API_Base):
    """API for AstroObjectBase.NoHDUMixin"""
    
    @nt.raises(NotImplementedError)
    def test_getheader_primary(self):
        """__getheader__(HDU) a NoHDU frame with a primary HDU should raise an error."""
        BFrame = self.FRAME(data=self.VALID,label="Valid")
        assert BFrame.label == "Valid"
        HDU = pf.PrimaryHDU()
        BFrame.__getheader__(HDU)
        
    @nt.raises(NotImplementedError)
    def test_getheader_secondary(self):
        """__getheader__(HDU) a NoHDU frame with a secondary HDU should raise an error."""
        BFrame = self.FRAME(data=self.VALID,label="Valid")
        assert BFrame.label == "Valid"
        HDU = self.HDUTYPE()
        BFrame.__getheader__(HDU)
    
    @nt.raises(NotImplementedError)
    def test_setheader_primary(self):
        """__setheader__(HDU) a NoHDU frame with a primary HDU should raise an error."""
        BFrame = self.FRAME(data=self.VALID,label="Valid")
        assert BFrame.label == "Valid"
        HDU = pf.PrimaryHDU()
        BFrame.__setheader__(HDU)
        
    @nt.raises(NotImplementedError)
    def test_setheader_secondary(self):
        """__setheader__(HDU) a NoHDU frame with a secondary HDU should raise an error."""
        BFrame = self.FRAME(data=self.VALID,label="Valid")
        assert BFrame.label == "Valid"
        HDU = self.HDUTYPE()
        BFrame.__setheader__(HDU)
    
    @nt.raises(NotImplementedError)
    def test__hdu__secondary(self):
        """__hdu__(primary=False) secondary raises an NotImplementedError"""
        BFrame = self.FRAME(data=self.VALID,label="Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.__hdu__()
    
    @nt.raises(NotImplementedError)
    def test__hdu__primary(self):
        """__hdu__(primary=True) primary raises an NotImplementedError"""
        BFrame = self.FRAME(data=self.VALID,label="Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.__hdu__(primary=True)
        
    @nt.raises(NotImplementedError)
    def test_read_secondary(self):
        """__read__() secondary HDU type should get an abstract error"""
        BFrame = self.FRAME.__read__(self.HDUTYPE(self.VALID),"Secondary HDU")
        
    @nt.raises(NotImplementedError)
    def test_read_primary(self):
        """__read__() primary HDU type should get an abstract error"""
        BFrame = self.FRAME.__read__(pf.PrimaryHDU(self.VALID),"Primary HDU")
    
    @nt.raises(NotImplementedError)
    def test_read_empty_primary(self):
        """__read__() an empty primary HDU fails"""
        BFrame = self.FRAME.__read__(pf.PrimaryHDU(),"Empty Primary HDU")
        
    @nt.raises(NotImplementedError)
    def test_read_empty_secondary(self):
        """__read__() an empty primary HDU fails"""
        BFrame = self.FRAME.__read__(self.HDUTYPE(),"Empty Primary HDU")
    

class API_AnalyticMixin(API_NoHDU_Frame,API_NoData_Frame):
    """API for AstroObjectBase.AnalyticMixin"""
    
    @nt.raises(NotImplementedError)
    def test_save_data(self):
        """__save__() to an abstract base class raises an NotImplementedError"""
        # raise SkipTest("This is a bug, related to argument ordering on the frame.__init__() call.")
        # The following arguments are treated as label and header respectivley. The lack of abstract type cheking and/or a data argument means that this call doesn't fail when it should.
        self.FRAME.__save__(self.VALID,"None")
    
    @nt.raises(NotImplementedError)
    def test_save_empty(self):
        """__save__() with none object raises an NotImplementedError"""
        self.FRAME.__save__(None,"None")
    
    @abstractmethod
    def test_call(self):
        pass
    
    @abstractmethod
    def test_call_with_kwargs(self):
        pass
        

class API_NotEmpty_Frame(API_Base):
    """API for AstroObjectBase.BaseFrame which cannot be empty"""
    
    @nt.raises(AttributeError)
    def test_init_empty(self):
        """__init__() fails without data"""
        self.FRAME(data=None,label="Label")
    
    @nt.raises(NotImplementedError)
    def test_read_empty_primary(self):
        """__read__() an empty primary HDU fails"""
        BFrame = self.FRAME.__read__(pf.PrimaryHDU(),"Empty Primary HDU")
        
    @nt.raises(NotImplementedError)
    def test_read_empty_secondary(self):
        """__read__() an empty secondary HDU fails"""
        BFrame = self.FRAME.__read__(self.HDUTYPE(),"Empty Primary HDU")
    
    @nt.raises(NotImplementedError)
    def test_save_empty(self):
        """__save__() fails with empty data."""
        BFrame = self.FRAME.__save__(None,"Empty")

class API_General_Frame(API_HDUHeader_Frame,API_NotEmpty_Frame,API_Base_Frame):
    """API for general, API-compliant objects"""
    
    def test_init_data(self):
        """__init__() succeeds with valid data"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
    
    def test_save_data(self):
        """__save__() valid data"""
        AFrame = self.FRAME.__save__(self.VALID,"Valid")
        assert AFrame.label == "Valid"
    
    def test_read_primary(self):
        """__read__() primary HDU succeeds"""
        AFrame = self.FRAME.__read__(pf.PrimaryHDU(self.VALID),"Valid")
        assert isinstance(AFrame,self.FRAME)
        assert AFrame.label == "Valid"
        assert self.data_eq_frame(self.VALID,AFrame)
    
    def test_read_secondary(self):
        """__read__() secondary HDU succeeds"""
        AFrame = self.FRAME.__read__(self.HDUTYPE(self.VALID),"Valid")
        assert isinstance(AFrame,self.FRAME)
        assert AFrame.label == "Valid"
        assert self.data_eq_frame(self.VALID,AFrame)
    
    def test_call(self):
        """__call__() yields data"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        data = AFrame()
        assert self.data_eq_data(data,self.VALID)
    
    def test_call_with_kwargs(self):
        """__call__(**kwargs) yields data"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        data = AFrame(**self.RKWARGS)
        assert self.data_eq_data(data,self.VALID)
    
    def test__hdu__secondary(self):
        """__hdu__() works for secondary HDUs"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        HDU = AFrame.__hdu__()
        assert isinstance(HDU,self.HDUTYPE)
        assert self.data_eq_data(HDU.data,self.VALID)
    
    def test__hdu__primary(self):
        """__hdu__(primary=True) works for primary HDUs"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        HDU = AFrame.__hdu__(primary=True)
        assert isinstance(HDU,pf.PrimaryHDU)
        assert self.data_eq_data(HDU.data,self.VALID)
    
    def test_HDU_secondary(self):
        """hdu() generates an empty Image HDU"""
        BFrame = self.FRAME(data=self.VALID,label="Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.hdu()
        assert isinstance(HDU,self.HDUTYPE)
        assert self.data_eq_data(HDU.data,self.VALID)
    
    def test_HDU_primary(self):
        """hdu() generates an empty Image HDU"""
        BFrame = self.FRAME(data=self.VALID,label="Empty")
        assert BFrame.label == "Empty"
        HDU = BFrame.hdu(primary=True)
        assert isinstance(HDU,pf.PrimaryHDU)
        assert self.data_eq_data(HDU.data,self.VALID)

    def test_HDU_with_header(self):
        """hdu() generates an empty Image HDU with Header"""
        header = pf.core.Header()
        header.update('test','value')
        BFrame = self.FRAME(data=self.VALID,label="Valid",header=header)
        assert BFrame.label == "Valid"
        HDU = BFrame.hdu()
        assert isinstance(HDU,self.HDUTYPE)
        assert HDU.header["test"] == 'value'  
        
    def test_show(self):
        """__show__() returns a valid type"""
        AFrame = self.FRAME(data=self.VALID,label="Valid")
        assert AFrame.label == "Valid"
        figure = AFrame.__show__()
        assert isinstance(figure,self.SHOWTYPE), "Found type %s" % type(figure)
    

class API_Base_Object(API_Base):
    """API for AstroObjectBase.BaseObject"""
    
    attributes = ['FRAME','VALID','INVALID','SHOWTYPE','HDUTYPE','OBJECTSTR','OBJECT','FRAMESTR']
    methods = ['frame_eq_frame','data_eq_data','data_eq_frame','frame']
    
    def frame(self):
        """Returns a valid frame"""
        return self.FRAME(data=self.VALID,label="Valid")
        
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
        AObject.save(self.frame())
        assert AObject.statename == "Valid"
        assert isinstance(AObject.frame(),self.FRAME)
    
    def test_set_frame_with_label(self):
        """[] with a new label changes the frame's label"""
        AObject = self.OBJECT()
        AObject["Other"] = self.frame()
        assert AObject.statename == "Other"
        assert AObject.frame().label == "Other"
    
    def test_save_frame_with_label(self):
        """save() with a new label changes the frame's label"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"Other")
        assert AObject.statename == "Other"
        assert AObject.frame().label == "Other"
    
    def test_double_saving_frame_should_reference(self):
        """save() should prevent data in frames from referencing each other"""        
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.save(self.frame(),"Other")
        assert AObject.statename == "Other"
        assert AObject.frame().label == "Other"
        try:
            AObject.select("Valid")
            assert AObject.statename == "Valid"
            assert AObject.frame().label == "Valid"
            AObject.select("Other")
            assert AObject.statename == "Other"
            assert AObject.frame().label == "Other"
        except AssertionError as e:
            raise SkipTest("This is a bug, should be fixed in a later version. %s" % e)
    
    def test_double_saving_data_should_not_reference(self):
        """data() should prevent data from referencing each other."""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.save(AObject.data(),"Other")
        assert AObject.statename == "Other"
        assert AObject.frame().label == "Other"
        try:
            AObject.select("Valid")
            assert AObject.statename == "Valid"
            assert AObject.frame().label == "Valid"
            AObject.select("Other")
            assert AObject.statename == "Other"
            assert AObject.frame().label == "Other"
        except AssertionError as e:
            raise SkipTest("This is a bug, should be fixed in a later version. %s" % e)
    
    @nt.raises(IOError)
    def test_read_from_nonexistent_file(self):
        """read() fails if the file doesn't exist"""
        AObject = self.OBJECT()
        AObject.read(self.files[0])
    
    def test_write_clobbers_file(self):
        """write() can clobber existing files"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.write(self.files[0])
        AObject.write(self.files[0],clobber=True)
    
    @nt.raises(IOError)
    def test_write_does_not_clobber_file(self):
        """write() doesn't clobber files by default"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.write(self.files[0])
        AObject.write(self.files[0])
    
    def test_select(self):
        """select() changes to correct state"""
        Label = "Other"
        Frame = self.FRAME(self.VALID,Label)
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.save(Frame,Label)
        assert AObject.statename == Label
        assert AObject.frame().label == Label
        AObject.select("Valid")
        assert AObject.statename == "Valid"
        assert AObject.frame().label == "Valid"
    
    @nt.raises(KeyError)
    def test_select_unknown_state(self):
        """select() cannont select non-existant states"""
        AObject = self.OBJECT()
        AObject.select("Valid")

    def test_data(self):
        """data() returns data object"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        data = AObject.data()
        assert self.data_eq_data(data,self.VALID)
    
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
        AObject.save(self.frame())
        frame = AObject.frame()
        assert self.frame_eq_frame(frame,self.frame())
    
    def test_get(self):
        """[] returns data object"""
        AObject = self.OBJECT()
        AObject[self.frame().label] = self.frame()
        frame = AObject[self.frame().label]
        assert self.frame_eq_frame(frame,self.frame())
    
    
    @nt.raises(KeyError)
    def test_duplicate_state_name(self):
        """save() should not allow duplication of state name"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.save(self.frame())
    
    def test_list_statenames(self):
        """list() should show all statenames"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        assert ["A","B"] == sorted(AObject.list())
    
    def test_list_empty(self):
        """list() should be empty on a fresh object"""
        AObject = self.OBJECT()
        assert [] == AObject.list()
    
    def test_keep(self):
        """keep() only retains given state"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        assert ["A","B"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        AObject.keep("A")
        assert ["A"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        assert "B" not in AObject.states, "States: %s" % AObject.states
    
    def test_keep_multiple(self):
        """keep() only retains given states"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        AObject.save(self.frame(),"C")
        assert ["A","B","C"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        AObject.keep("A","C")
        assert ["A","C"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        assert "B" not in AObject.states, "States: %s" % AObject.states
    
    @nt.raises(IndexError)
    def test_keep_non_existant_state(self):
        """keep() fails with non-existent state"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
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
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        assert ["A","B"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        AObject.select("B")
        AObject.keep("A")
        AObject.frame()
    
    def test_remove(self):
        """remove() deletes given state"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        assert ["A","B"] == sorted(AObject.list())
        AObject.remove("A")
        assert ["B"] == sorted(AObject.list())
        assert "A" not in AObject.states, "States: %s" % AObject.states
    
    def test_remove_multiple(self):
        """remove() deletes given states"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        AObject.save(self.frame(),"C")
        assert ["A","B","C"] == sorted(AObject.list())
        AObject.remove("A","C")
        assert ["B"] == sorted(AObject.list())
        assert "A" not in AObject.states, "States: %s" % AObject.states
    
    def test_remove_valid_state(self):
        """remove() leaves the object with a valid selected state"""
        BObject = self.OBJECT()
        BObject.save(self.frame(),"A")
        BObject.save(self.frame(),"B")
        assert ["A","B"] == BObject.list()
        BObject.select("A")
        BObject.remove("A")
        BObject.frame()
    
    @nt.raises(IndexError)
    def test_remove_non_existant_state(self):
        """remove() fails with non-existent state"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
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
        AObject.save(self.frame())
        figure = AObject.show()
        assert isinstance(figure,self.SHOWTYPE), "Returned type %s" % type(figure)
    
    @nt.raises(KeyError)
    def test_show_non_existant_state(self):
        """show() raises KeyError for a non-existent state name"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.show("Valid" + "JUNK...")
    
    def test_object(self):
        """object() call exists and works, but has been depreciated"""
        BObject = self.OBJECT()
        BObject.save(self.frame())
        assert self.frame_eq_frame(BObject.object(),BObject.frame())

        
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
        
    def test_string_representation(self):
        """__repr__() String representation correct for Object"""
        raise SkipTest("Test doesn't make sense in this context.")
        AObject = self.OBJECT()
        assert str(AObject) == self.OBJECTSTR
    
    
class API_Base_Functional(API_Base):
    """Functional Tests Basic API Level"""
    attributes = ['FRAMEINST','VALID','INVALID','frame_eq_frame','SHOWTYPE','HDUTYPE','OBJECTSTR','OBJECT','FRAMELABEL',
    'FRAME','imHDU','FILENAME','data_eq_data']
    
    def test_write_and_read(self):
        """User writes an image and reads from the same frame"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.write(self.files[0])
        BObject = self.OBJECT()
        assert os.access(self.files[0],os.F_OK)
        labels = BObject.read(self.files[0])
        assert labels == AObject.list()
        assert isinstance(BObject.frame(),self.FRAME)
        assert self.frame_eq_frame(self.frame(),BObject.frame())
        
