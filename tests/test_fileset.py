# -*- coding: utf-8 -*-
# 
#  test_fileset.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-06-07.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 

import os
import tempfile

from AstroObject.file.fileset import FileSet

class BaseFileSetTests(object):
    """Base fileset testing API"""
    
    FsClass = None
    FsInstance = None
    BASE = os.path.join(os.getcwd(),"test_fileset_base/")
    NAME = "test_fileset_directory"
    ALT_TIMEFORMAT = "DATE:%Y-%m-%d TIME:%H:%M:%S"
    ALT_DBFILENAME = "visible.db.yaml"
    STATIC_FILE = "random-static-file.txt"
    
    def setup(self):
        """Set up the testing environment"""
        assert issubclass(self.FsClass,FileSet), "Must declare a FileSet class as self.FsClass"
                
        # Set up directory strucuture
        try:
            os.mkdir(self.BASE)
        except OSError: pass
        try:
            os.mkdir(os.path.join(self.BASE,self.NAME))
        except OSError: pass
        
        # Add a random static file
        with open(os.path.join(self.BASE,self.NAME,self.STATIC_FILE),'w') as stream:
            stream.write("Some Bogus Text In This File Is Here To Have A PartAAY")
        
        # Print Fileset Type Name for Logging
        print "Class: %s" % self.FsClass.__name__
        
        
    def teardown(self):
        """Clean up the testing environment"""
        if isinstance(self.FsInstance,FileSet):
            if self.FsInstance.open:
                self.FsInstance.close(check=False,clean=True)
        if os.path.exists(os.path.join(self.BASE,self.NAME,self.STATIC_FILE)):
            # This file may have been removed in the above close command.
            os.remove(os.path.join(self.BASE,self.NAME,self.STATIC_FILE))
        if os.path.exists(os.path.join(self.BASE,self.NAME)):
            # This directory may have been removed in the close command.
            os.rmdir(os.path.join(self.BASE,self.NAME))
        # The base directory should not be removed during testing, as such, we won't catch errors here.
        os.rmdir(self.BASE)
        
    def test_init_with_defaults(self):
        """__init__ with default values."""
        self.FsInstance = self.FsClass(self.BASE,self.NAME)
        
    def test_init_with_non_defaults(self):
        """__init__ with non-default values"""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,
            isopen=False,persist=True,autodiscover=False,
            timeformat=self.ALT_TIMEFORMAT,dbfilebase=self.ALT_DBFILENAME)
        
    def test_directory_attribute(self):
        """.directory attribute is read-only"""
        self.FsInstance = self.FsClass(self.BASE,self.NAME)
        assert self.FsInstance.directory == os.path.join(self.BASE,self.NAME), "Directory is set correctly"
        
        try: self.FsInstance.directory = "Other/Dir/Path/"
        except AttributeError: pass
        else:
            assert False, "Setting self.FsInstance.directory should be illegal."
        
    def test_persist_attribute(self):
        """.persist attribute does nothing when read, creates persistance database when set"""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,dbfilebase=self.ALT_DBFILENAME)
        assert not self.FsInstance.persist, "Fileset should default to non-persistance"
        assert not os.path.exists(os.path.join(self.FsInstance.directory,self.ALT_DBFILENAME)), "Database should not yet exist"
        self.FsInstance.persist = True
        assert self.FsInstance.persist
        assert os.path.exists(os.path.join(self.FsInstance.directory,self.ALT_DBFILENAME)), "Database should exist, after triggering persistance"
        
    def test_autodiscover_attribute(self):
        """.autodiscover attribut does nothing when read, starts autodiscovery when set."""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False)
        assert not self.FsInstance.autodiscover, "FileSet should be explicitly NOT autodiscovering."
        assert len(self.FsInstance) == 0
        self.FsInstance.autodiscover = True
        assert self.FsInstance.autodiscover, "FileSet should have set AutoDiscovery"
        assert len(self.FsInstance) == 1
        assert self.STATIC_FILE in self.FsInstance, "Static File should be present in fileset. Files: %r" % self.FsInstance.files 
        
        
        
        
class test_FileSet(BaseFileSetTests):
    """AstroObject.file.fileset.FileSet"""
    FsClass = FileSet
    