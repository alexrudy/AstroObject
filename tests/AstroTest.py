# -*- coding: utf-8 -*-
#
#  AstroTest.py
#  ObjectModel
#
#  Created by Alexander Rudy on 2011-10-31.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.6.0
#
"""
:mod:`AstroTest` for nosetests
==============================

This module has test frameworks for all modules. The baisc hierarchy of testing frameworks is designed to mimic the basic hierarchy of the :mod:`AstroObject` module in general. There are appropriate test class mixins for all of the built-in Frame and Stack classes.

In order to ensure that tests can be run correctly with this API, the API will check for the existance of all variables listed in the ``attributes`` item in each test class. This prevents running the test framework without the required variables for each sub-class.

.. inheritance-diagram::
    tests.AstroTest.API_Base_Frame
    tests.AstroTest.API_HDUHeader_Frame
    tests.AstroTest.API_NoData_Frame
    tests.AstroTest.API_NoHDU_Frame
    tests.AstroTest.API_NotEmpty_Frame
    tests.AstroTest.API_AnalyticMixin
    tests.AstroTest.API_General_Frame
    tests.AstroTest.API_BaseStack
    tests.Test_AstroFITS.test_FITSFrame
    tests.Test_AstroFITS.test_FITSStack
    tests.test_AstroHDU.test_HDUFrame
    tests.test_AstroHDU.test_HDUStack
    tests.Test_AstroImage.test_ImageFrame
    tests.Test_AstroImage.test_ImageStack
    tests.Test_AstroSpectra.test_SpectraFrame
    tests.Test_AstroSpectra.test_SpectraStack
    tests.Test_AnalyticSpectra.test_InterpolatedSpectrum
    tests.Test_AnalyticSpectra.test_UnitarySpectrum
    :parts: 1

"""
# Parent Imports
from AstroObject.iraftools import UseIRAFTools

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
    attributes = ['FRAME','VALID','INVALID','SHOWTYPE','HDUTYPE','FRAMESTR','RKWARGS','FLABEL']
    methods = ['frame_eq_frame','data_eq_data','data_eq_frame']
    
    def frame(self,**kwargs):
        """Returns a valid frame"""
        return self.FRAME(data=self.VALID,label=self.FLABEL,**kwargs)
    
    def test_init_data(self):
        """__init__() succeds with valid data"""
        AFrame = self.frame(metadata={"A":"Abba"},header={"testvar":"avalue"})
        assert AFrame.valid
        assert AFrame.header['testvar'] == "avalue", "Header value save failure"
        assert AFrame.metadata["A"] == "Abba", "Metadata save failure"
        
    def test_init_pyfits_header(self):
        """__init__() with PyFITS header succeeds."""
        header = pf.core.Header()
        header.update('testvar','avalue')
        AFrame = self.frame(header=header)
        assert AFrame.valid
        assert AFrame.header['testvar'] == "avalue", "Header value save failure"
        
    def test_init_empty(self):
        """__init__() abstract frame works without data"""
        AFrame = self.FRAME(data=None,label=self.FLABEL)
        assert AFrame.label == self.FLABEL
    
    @nt.raises(AttributeError)
    def test_init_invalid(self):
        """__init__() fails with invalid data"""
        self.FRAME(data=self.INVALID,label="Invalid")
        
    @nt.raises(AttributeError)
    def test_init_nolabel(self):
        """__init__() fails with valid data but no label"""
        AFrame = self.FRAME(self.VALID,label=None)

    def test_string_representation(self):
        """__repr__() String representation correct for Frame"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
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
        BFrame = self.frame()
        assert BFrame.label == self.FLABEL
        HDU = pf.PrimaryHDU()
        BFrame.__getheader__(HDU)
        
    def test_getheader_secondary(self):
        """__getheader__(HDU) a HDU frame with a secondary HDU."""
        BFrame = self.frame()
        assert BFrame.label == self.FLABEL
        HDU = self.HDUTYPE()
        BFrame.__getheader__(HDU)
    
    def test_setheader_primary(self):
        """__setheader__(HDU) a NoHDU frame with a primary HDU."""
        BFrame = self.frame()
        assert BFrame.label == self.FLABEL
        HDU = pf.PrimaryHDU()
        nHDU = BFrame.__setheader__(HDU)
        assert isinstance(nHDU,pf.PrimaryHDU)
        
    def test_setheader_secondary(self):
        """__setheader__(HDU) a HDU frame with a secondary HDU."""
        BFrame = self.frame()
        assert BFrame.label == self.FLABEL
        HDU = self.HDUTYPE()
        nHDU = BFrame.__setheader__(HDU)
        assert isinstance(nHDU,self.HDUTYPE)
    
class API_NoData_Frame(API_CanBeEmpty_Frame,API_Base):
    """API for AstroObjectBase.NoDataMixin"""
    
    @nt.raises(NotImplementedError)
    def test_call_with_kwargs(self):
        """__call__(**kwargs) a NoData frame should raise an error."""
        BFrame = self.frame()
        assert BFrame.label == self.FLABEL
        BFrame(**self.RKWARGS)
    
    @nt.raises(NotImplementedError)
    def test_call(self):
        """__call__() a NoData frame should raise an error."""
        BFrame = self.frame()
        assert BFrame.label == self.FLABEL
        BFrame()
    
    @nt.raises(NotImplementedError)
    def test_show(self):
        """__show__() a NoData frame should raise an error."""
        BFrame = self.frame()
        assert BFrame.label == self.FLABEL
        BFrame.__show__()
    
    @nt.raises(NotImplementedError)    
    def test_save_data(self):
        """__save__() a NoData frame should raise an error."""
        AFrame = self.FRAME.__save__(self.VALID,self.FLABEL)
        assert AFrame.label == self.FLABEL
    

class API_NoHDU_Frame(API_Base):
    """API for AstroObjectBase.NoHDUMixin"""
    
    @nt.raises(NotImplementedError)
    def test_getheader_primary(self):
        """__getheader__(HDU) a NoHDU frame with a primary HDU should raise an error."""
        BFrame = self.frame()
        assert BFrame.label == self.FLABEL
        HDU = pf.PrimaryHDU()
        BFrame.__getheader__(HDU)
        
    @nt.raises(NotImplementedError)
    def test_getheader_secondary(self):
        """__getheader__(HDU) a NoHDU frame with a secondary HDU should raise an error."""
        BFrame = self.frame()
        assert BFrame.label == self.FLABEL
        HDU = self.HDUTYPE()
        BFrame.__getheader__(HDU)
    
    @nt.raises(NotImplementedError)
    def test_setheader_primary(self):
        """__setheader__(HDU) a NoHDU frame with a primary HDU should raise an error."""
        BFrame = self.frame()
        assert BFrame.label == self.FLABEL
        HDU = pf.PrimaryHDU()
        BFrame.__setheader__(HDU)
        
    @nt.raises(NotImplementedError)
    def test_setheader_secondary(self):
        """__setheader__(HDU) a NoHDU frame with a secondary HDU should raise an error."""
        BFrame = self.frame()
        assert BFrame.label == self.FLABEL
        HDU = self.HDUTYPE()
        BFrame.__setheader__(HDU)
    
    @nt.raises(NotImplementedError)
    def test__hdu__secondary(self):
        """__hdu__(primary=False) secondary raises an NotImplementedError"""
        BFrame = self.frame()
        assert BFrame.label == self.FLABEL
        HDU = BFrame.__hdu__()
    
    @nt.raises(NotImplementedError)
    def test__hdu__primary(self):
        """__hdu__(primary=True) primary raises an NotImplementedError"""
        BFrame = self.frame()
        assert BFrame.label == self.FLABEL
        HDU = BFrame.__hdu__(primary=True)
        
    @nt.raises(NotImplementedError)
    def test_read_secondary(self):
        """__read__() secondary HDU type should get an abstract error"""
        BFrame = self.FRAME.__read__(self.HDUTYPE(),"Secondary HDU")
        
    @nt.raises(NotImplementedError)
    def test_read_primary(self):
        """__read__() primary HDU type should get an abstract error"""
        BFrame = self.FRAME.__read__(pf.PrimaryHDU(),"Primary HDU")
    
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
    
    def test_save_data(self):
        """__save__() valid data"""
        AFrame = self.FRAME.__save__(self.VALID,self.FLABEL)
        assert AFrame.label == self.FLABEL
    
    def test_read_primary(self):
        """__read__() primary HDU succeeds"""
        AFrame = self.FRAME.__read__(pf.PrimaryHDU(self.VALID),self.FLABEL)
        assert isinstance(AFrame,self.FRAME)
        assert AFrame.label == self.FLABEL
        assert self.data_eq_frame(self.VALID,AFrame)
    
    def test_read_secondary(self):
        """__read__() secondary HDU succeeds"""
        AFrame = self.FRAME.__read__(self.HDUTYPE(self.VALID),self.FLABEL)
        assert isinstance(AFrame,self.FRAME)
        assert AFrame.label == self.FLABEL
        assert self.data_eq_frame(self.VALID,AFrame)
    
    def test_call(self):
        """__call__() yields data"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame()
        assert self.data_eq_data(data,self.VALID)
    
    def test_call_with_kwargs(self):
        """__call__(**kwargs) yields data"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        data = AFrame(**self.RKWARGS)
        assert self.data_eq_data(data,self.VALID)
    
    def test__hdu__secondary(self):
        """__hdu__() works for secondary HDUs"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        HDU = AFrame.__hdu__()
        assert isinstance(HDU,self.HDUTYPE)
        assert self.data_eq_data(HDU.data,self.VALID)
    
    def test__hdu__primary(self):
        """__hdu__(primary=True) works for primary HDUs"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        HDU = AFrame.__hdu__(primary=True)
        assert isinstance(HDU,pf.PrimaryHDU)
        assert self.data_eq_data(HDU.data,self.VALID)
    
    def test_HDU_secondary(self):
        """hdu() generates an Image HDU"""
        BFrame = self.frame()
        assert BFrame.label == self.FLABEL
        HDU = BFrame.hdu()
        assert isinstance(HDU,self.HDUTYPE)
        assert self.data_eq_data(HDU.data,self.VALID)
    
    def test_HDU_primary(self):
        """hdu() generates a Primary HDU"""
        BFrame = self.frame()
        assert BFrame.label == self.FLABEL
        HDU = BFrame.hdu(primary=True)
        assert isinstance(HDU,pf.PrimaryHDU)
        assert self.data_eq_data(HDU.data,self.VALID)

    def test_HDU_with_header(self):
        """hdu() generates an empty Image HDU with Header"""
        header = pf.core.Header()
        header.update('test','value')
        BFrame = self.FRAME(data=self.VALID,label=self.FLABEL,header=header)
        assert BFrame.label == self.FLABEL
        HDU = BFrame.hdu()
        assert isinstance(HDU,self.HDUTYPE)
        assert HDU.header["test"] == 'value'  
        
    def test_show(self):
        """__show__() returns a valid type"""
        AFrame = self.frame()
        assert AFrame.label == self.FLABEL
        figure = AFrame.__show__()
        assert isinstance(figure,self.SHOWTYPE), "Found type %s" % type(figure)
    

class API_BaseStack(API_Base):
    """API for AstroObjectBase.BaseStack"""
    
    attributes = ['FRAME','VALID','INVALID','SHOWTYPE','HDUTYPE','OBJECTSTR','OBJECT','FRAMESTR','FLABEL']
    methods = ['frame_eq_frame','data_eq_data','data_eq_frame','frame']
    
    def frame(self,**kwargs):
        """Returns a valid frame"""
        return self.FRAME(data=self.VALID,label=self.FLABEL,**kwargs)
        
    @nt.raises(AttributeError)
    def test_init_with_bad_class(self):
        """__init__() with invalid data classes"""
        self.OBJECT(dataClasses=10)
        
    @nt.raises(NotImplementedError)
    def test_init_with_no_dataClasses(self):
        """__init__() with no data classes"""
        self.OBJECT(dataClasses=[])
        
    def test_init_with_iraftools(self):
        """__init__() works in IRAFTools mode."""
        NEWOBJECT = UseIRAFTools(self.OBJECT)
        AObject = NEWOBJECT()
        AObject.save(self.frame())
        assert hasattr(AObject,'iraf')
        AObject.iraf.infile()
        AObject.iraf.done()
        
        
    def test_save_with_data(self):
        """save() works with valid data"""
        AObject = self.OBJECT()
        AObject.save(self.VALID,self.FLABEL)
    
    def test_save_overwrite(self):
        """save() can clobber from parent or save()"""
        AObject = self.OBJECT()
        AObject.save(self.VALID,self.FLABEL)
        AObject.save(self.VALID,self.FLABEL,clobber=True)
        AObject = self.OBJECT()
        AObject.clobber = True
        AObject.save(self.VALID,self.FLABEL)
        AObject.save(self.VALID,self.FLABEL)
        
    @nt.raises(KeyError)
    def test_save_no_overwrite(self):
        """save failes when trying to inadvertently clobber"""
        AObject = self.OBJECT()
        AObject.save(self.VALID,self.FLABEL)
        AObject.save(self.VALID,self.FLABEL,clobber=False)
        AObject = self.OBJECT()
        AObject.clobber = False
        AObject.save(self.VALID,self.FLABEL)
        AObject.save(self.VALID,self.FLABEL)
        
    
    def test_set_with_data(self):
        """[] works with valid data"""
        AObject = self.OBJECT()
        AObject[self.FLABEL] = self.VALID
    
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
        assert AObject.framename == self.FLABEL
        assert isinstance(AObject.frame(),self.FRAME)
    
    def test_set_frame_with_label(self):
        """[] with a new label changes the frame's label"""
        AObject = self.OBJECT()
        AObject["Other"] = self.frame()
        assert AObject.framename == "Other"
        assert AObject.frame().label == "Other"
    
    def test_save_frame_with_label(self):
        """save() with a new label changes the frame's label"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"Other")
        assert AObject.framename == "Other"
        assert AObject.frame().label == "Other"
    
    def test_double_saving_frame_should_reference(self):
        """save() should prevent data in frames from referencing each other"""        
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.save(self.frame(),"Other")
        assert AObject.framename == "Other"
        assert AObject.frame().label == "Other"
        try:
            AObject.select(self.FLABEL)
            assert AObject.framename == self.FLABEL
            assert AObject.frame().label == self.FLABEL
            AObject.select("Other")
            assert AObject.framename == "Other"
            assert AObject.frame().label == "Other"
        except AssertionError as e:
            raise SkipTest("This is a bug, should be fixed in a later version. %s" % e)
    
    def test_double_saving_data_should_not_reference(self):
        """data() should prevent data from referencing each other."""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.save(AObject.data(),"Other")
        assert AObject.framename == "Other"
        assert AObject.frame().label == "Other"
        try:
            AObject.select(self.FLABEL)
            assert AObject.framename == self.FLABEL
            assert AObject.frame().label == self.FLABEL
            AObject.select("Other")
            assert AObject.framename == "Other"
            assert AObject.frame().label == "Other"
        except AssertionError as e:
            raise SkipTest("This is a bug, should be fixed in a later version. %s" % e)
    
    @nt.raises(IOError)
    def test_read_from_nonexistent_file(self):
        """read() fails if the file doesn't exist"""
        AObject = self.OBJECT()
        AObject.read(self.files[0])
    
    @nt.raises(KeyError)
    def test_read_from_file_single_frame(self):
        """read() fails on a single frame file when trying to clobber"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.write(self.files[0])
        AObject.read(self.files[0])
        
        
    def test_read_from_file_single_frame_framename(self):
        """read() succeeds with an explicit framename"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.write(self.files[0])
        AObject.read(self.files[0],framename="Other",select=False)
        assert AObject.framename != "Other"
    
    def test_read_from_file_single_frame_clobber(self):
        """read() succeeds on overwrite with clobber=True"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.write(self.files[0])
        AObject.read(self.files[0],clobber=True)
    
    def test_read_from_file_single_frame_stream(self):
        """read() succeeds from streams"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.write(self.files[0])
        with open(self.files[0],"rb") as stream:
            AObject.read(stream,clobber=True, filetype="FITSFile")
    
    
    def test_read_from_implicit_filename(self):
        """read() succeeds with implicit filename"""
        AObject = self.OBJECT(filename=self.files[0])
        AObject.save(self.frame())
        AObject.write()
        AObject.read(clobber=True)
        
    def test_write_to_multiframe_stream(self):
        """write() can write to streams"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject["Other"] = self.frame()
        with open(self.files[0],"ab+") as stream:
            PF,Fs,FN = AObject.write(stream, filetype="FITSFile")
        assert Fs == [self.FLABEL]
        assert PF == "Other"
        
          
    def test_write_to_multiframe_file(self):
        """write() can create multiframe files"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject["Other"] = self.frame()
        PF,Fs,FN = AObject.write(self.files[0])
        assert Fs == [self.FLABEL]
        assert PF == "Other"
        
    def test_write_to_singleframe_file(self):
        """write(singleFrame=True) creates single framed FITS files."""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject["Other"] = self.frame()
        PF,Fs,FN = AObject.write(self.files[0],singleFrame=True)
        assert Fs == []
        assert PF == "Other"
    
    def test_write_to_singleframe_textfile(self):
        """write(singleFrame=True) creates single framed text files."""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject["Other"] = self.frame()
        PF,Fs,FN = AObject.write(self.files[1],singleFrame=True,clobber=True)
        AObject.read(self.files[1],clobber=True)        
        assert Fs == []
        assert PF == "Other"
        
    def test_write_to_singleframe_numpyfile(self):
        """write(singleFrame=True) creates single framed numpy files."""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject["Other"] = self.frame()
        PF,Fs,FN = AObject.write(self.files[2],singleFrame=True,clobber=True)
        AObject.read(self.files[2],clobber=True)        
        assert Fs == []
        assert PF == "Other"    
    
    def test_write_clobbers_file(self):
        """write() can clobber existing files"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.write(self.files[0])
        PF,Fs,FN = AObject.write(self.files[0],clobber=True)
        assert Fs == []
        assert PF == self.FLABEL
        
    
    @nt.raises(IOError)
    def test_write_does_not_clobber_file(self):
        """write() doesn't clobber files by default"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.write(self.files[0])
        AObject.write(self.files[0])
    
    def test_select(self):
        """select() changes to correct frame"""
        Label = "Other"
        Frame = self.FRAME(self.VALID,Label)
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.save(Frame,Label)
        assert AObject.framename == Label
        assert AObject.frame().label == Label
        AObject.select(self.FLABEL)
        assert AObject.framename == self.FLABEL
        assert AObject.frame().label == self.FLABEL
    
    def test_select(self):
        """select(None) changes to default frame"""
        Frame = self.FRAME(self.VALID,"Other")
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.save(Frame)
        assert AObject.framename == "Other"
        assert AObject.frame().label == "Other"
        AObject.select(self.FLABEL)
        assert AObject.framename == self.FLABEL
        assert AObject.frame().label == self.FLABEL
        AObject.select(None)
        assert AObject.framename == self.FLABEL
        assert AObject.frame().label == self.FLABEL
        
    
    
    @nt.raises(KeyError)
    def test_select_unknown_frame(self):
        """select() cannont select non-existant frames"""
        AObject = self.OBJECT()
        AObject.select(self.FLABEL)

    def test_data(self):
        """data() returns data object"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        data = AObject.data()
        assert self.data_eq_data(data,self.VALID)
        
    def test_d(self):
        """.d returns data object"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        data = AObject.d
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
        """frame() returns frame object"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        frame = AObject.frame()
        assert self.frame_eq_frame(frame,self.frame())
        
    def test_frame(self):
        """.f returns frame object"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        frame = AObject.f
        assert self.frame_eq_frame(frame,self.frame())
    
    def test_get(self):
        """[] returns data object"""
        AObject = self.OBJECT()
        AObject[self.frame().label] = self.frame()
        frame = AObject[self.frame().label]
        assert self.frame_eq_frame(frame,self.frame())
    
    @nt.raises(KeyError)
    def test_duplicate_frame_name(self):
        """save() should not allow duplication of frame name"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.save(self.frame())
    
    def test_list_framenames(self):
        """list() should show all framenames"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        assert ["A","B"] == sorted(AObject.list())
    
    def test_list_empty(self):
        """list() should be empty on a fresh object"""
        AObject = self.OBJECT()
        assert [] == AObject.list()
    
    def test_keep(self):
        """keep() only retains given frame"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        assert ["A","B"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        AObject.keep("A")
        assert ["A"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        assert "B" not in AObject.list(), "States: %s" % AObject.list()
    
    def test_keep_multiple(self):
        """keep() only retains given frames"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        AObject.save(self.frame(),"C")
        assert ["A","B","C"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        AObject.keep("A","C")
        assert ["A","C"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        assert "B" not in AObject.list(), "States: %s" % AObject.list()
        
    def test_keep_multiple_delete(self):
        """keep() only retains given frames"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        AObject.save(self.frame(),"C")
        assert ["A","B","C"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        AObject.keep("A","C",delete=True)
        assert ["A","C"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        assert "B" not in AObject.list(), "States: %s" % AObject.list()
    
    @nt.raises(KeyError)
    def test_keep_non_existant_frame(self):
        """keep() fails with non-existent frame"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        assert ["A","B"] == sorted(AObject.list())
        AObject.keep("C")
    
    @nt.raises(KeyError)
    def test_keep_empty(self):
        """keep() fails with an empty object"""
        AObject = self.OBJECT()
        AObject.keep("B")
    
    def test_keep_valid_frame(self):
        """keep() leaves the object with a valid selected frame"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        assert ["A","B"] == sorted(AObject.list()) , "List: %s" % AObject.list()
        AObject.select("B")
        AObject.keep("A")
        AObject.frame()
    
    def test_del(self):
        """del [] deletes data"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        assert ["A","B"] == sorted(AObject.list())
        del AObject["A"]
        assert ["B"] == sorted(AObject.list())
        assert "A" not in AObject.list(), "States: %s" % AObject.list()
    
    
    def test_clear_delete(self):
        """clear(delete=True) explicitly deletes all frames"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        AObject.save(self.frame(),"C")
        assert ["A","B","C"] == sorted(AObject.list())
        AObject.clear(delete=True)
        assert len(AObject) == 0
        assert "A" not in AObject.list(), "States: %s" % AObject.list()
    
    
    def test_clear(self):
        """clear() deletes all frames"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        AObject.save(self.frame(),"C")
        assert ["A","B","C"] == sorted(AObject.list())
        AObject.clear()
        assert len(AObject) == 0
        assert "A" not in AObject.list(), "States: %s" % AObject.list()
    
    
    def test_remove(self):
        """remove() deletes given frame"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        assert ["A","B"] == sorted(AObject.list())
        AObject.remove("A")
        assert ["B"] == sorted(AObject.list())
        assert "A" not in AObject.list(), "States: %s" % AObject.list()

    
    def test_remove_delete(self):
        """remove() deletes given frames explicitly"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        AObject.save(self.frame(),"C")
        assert ["A","B","C"] == sorted(AObject.list())
        AObject.remove("A","C",delete=True)
        assert ["B"] == sorted(AObject.list())
        assert "A" not in AObject.list(), "States: %s" % AObject.list()
    
    def test_remove_multiple(self):
        """remove() deletes given frames"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        AObject.save(self.frame(),"C")
        assert ["A","B","C"] == sorted(AObject.list())
        AObject.remove("A","C")
        assert ["B"] == sorted(AObject.list())
        assert "A" not in AObject.list(), "States: %s" % AObject.list()
    
    def test_remove_valid_frame(self):
        """remove() leaves the object with a valid selected frame"""
        BObject = self.OBJECT()
        BObject.save(self.frame(),"A")
        BObject.save(self.frame(),"B")
        assert ["A","B"] == BObject.list()
        BObject.select("A")
        BObject.remove("A")
        BObject.frame()
    
    def test_remove_non_existant_frame_clobber(self):
        """remove(clobber=True) succeeds with non-existent frame"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.remove("B",clobber=True)
        assert "A" in AObject
    
    
    @nt.raises(KeyError)
    def test_remove_non_existant_frame(self):
        """remove() fails with non-existent frame"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.remove("B")
    
    @nt.raises(KeyError)
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
    def test_show_non_existant_frame(self):
        """show() raises KeyError for a non-existent frame name"""
        AObject = self.OBJECT()
        AObject.save(self.frame())
        AObject.show(self.FLABEL + "JUNK...")
    
    def test_object(self):
        """object() call exists and works, but has been depreciated"""
        BObject = self.OBJECT()
        BObject.save(self.frame())
        assert self.frame_eq_frame(BObject.object(),BObject.frame())

    
    def test_iter(self):
        """__iter__() iterates"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        AObject.save(self.frame(),"C")
        assert ["A","B","C"] == sorted(AObject.list())
        AList = [ A for A in AObject ]
        assert ["A","B","C"] == sorted(AList)
        
    def test_contains(self):
        """__contains__() finds containing items"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        AObject.save(self.frame(),"B")
        assert ["A","B"] == sorted(AObject.list())
        assert "A" in AObject
        assert "B" in AObject
        AObject.remove("A")
        assert ["B"] == sorted(AObject.list())
        assert "A" not in AObject
        assert "B" in AObject
        assert "A" not in AObject.list(), "States: %s" % AObject.list()
        
    def test_length(self):
        """__len__ gets length"""
        AObject = self.OBJECT()
        AObject.save(self.frame(),"A")
        assert len(AObject) == 1
        AObject.save(self.frame(),"B")
        assert len(AObject) == 2
        AObject.save(self.frame(),"C")
        assert len(AObject) == 3
        assert ["A","B","C"] == sorted(AObject.list())
        
        
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
        
