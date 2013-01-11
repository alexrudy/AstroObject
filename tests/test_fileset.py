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
from datetime import datetime
import time

import nose.tools as nt

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
    MISSING_FILE = "random-missing-file.txt"
    
    def setup(self):
        """Set up the testing environment"""
        self.STATIC_FILE_PATH = os.path.join(self.BASE,self.NAME,self.STATIC_FILE)

        assert issubclass(self.FsClass,FileSet), "Must declare a FileSet class as self.FsClass, got %s" % self.FsClass.__name__
                
        # Set up directory strucuture
        try:
            os.mkdir(self.BASE)
        except OSError: pass
        try:
            os.mkdir(os.path.join(self.BASE,self.NAME))
        except OSError: pass
        
        # Add a random static file
        with open(self.STATIC_FILE_PATH,'w') as stream:
            stream.write("Some Bogus Text In This File Is Here To Have A PartAAY")
        
        # Print Fileset Type Name for Logging
        print "Class: %s" % self.FsClass.__name__
        
        
    def teardown(self):
        """Clean up the testing environment"""
        if isinstance(self.FsInstance,FileSet):
            if self.FsInstance.open:
                self.FsInstance.close(check=False,clean=True)
        if os.path.exists(self.STATIC_FILE_PATH):
            # This file may have been removed in the above close command.
            os.remove(self.STATIC_FILE_PATH)
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
            assert False, ".directory attribute should be read-only."
        
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
        
    def test_date_attribute(self):
        """.date returns a date and is not settable."""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False)
        assert isinstance(self.FsInstance.date,datetime)
        
        try: self.FsInstance.date = datetime.now()
        except AttributeError: pass
        else:
            assert False, ".date attribute should be read-only."
            
    def test_length_property(self):
        """len() works on fileset."""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False)
        assert len(self.FsInstance) == 0
        self.FsInstance.autodiscover = True
        assert len(self.FsInstance) == 1
    
    def test_contains_property(self):
        """x in FileSet works"""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False)
        assert self.STATIC_FILE not in self.FsInstance
        assert self.MISSING_FILE not in self.FsInstance
        self.FsInstance.add(self.STATIC_FILE)
        assert self.STATIC_FILE in self.FsInstance
        assert self.MISSING_FILE not in self.FsInstance
        
    def test_iterator_method(self):
        """for x in fileset works"""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False)
        ll = []
        for ff in self.FsInstance:
            ll.append(ff)
        assert len(ll) == 0
        self.FsInstance.add(self.STATIC_FILE)
        for ff in self.FsInstance:
            ll.append(ff)
        assert len(ll) == 1
    
    def test_files_attribute(self):
        """.files is a list of files and cannot be set."""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False)
        assert self.FsInstance.files == []
        self.FsInstance.add(self.STATIC_FILE)
        assert self.FsInstance.files == [ self.STATIC_FILE ]
        try: self.FsInstance.files = [ self.MISSING_FILE ]
        except AttributeError: pass
        else:
            assert False, ".files attribute should be read-only."
        
    def test_open_attribute(self):
        """.open is readable, correct and cannot be set."""
        self.FsInstance = self.FsClass(self.BASE,self.NAME)
        assert self.FsInstance.open
        self.FsInstance.close(check=False)
        assert not self.FsInstance.open
        try: self.FsInstance.open = True
        except AttributeError: pass
        else:
            assert False, ".open attribute should be read-only."
            
    def test_modified_attribute(self):
        """.modified is a list of modified files."""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False)
        assert self.FsInstance.modified == []
        self.FsInstance.autodiscover = True
        assert self.STATIC_FILE in self.FsInstance
        assert self.FsInstance.modified == [], "Unexpected .modified == %r " % self.FsInstance.modified
        time.sleep(1.0)
        with open(self.STATIC_FILE_PATH,'a') as stream:
            stream.write("\nOTHER BOGUS TEXT IN THIS FILE!")
        assert self.FsInstance.modified == [ self.STATIC_FILE ], "Unexpected .modified == %r " % self.FsInstance.modified
        try: self.FsInstance.modified = [ self.MISSING_FILE ]
        except AttributeError: pass
        else:
            assert False, ".modifed attribute should be read-only."
        
        
    def test_deleted_attribute(self):
        """.deleted is a list of missing files."""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False)
        assert self.FsInstance.modified == []
        self.FsInstance.autodiscover = True
        assert self.STATIC_FILE in self.FsInstance
        assert self.FsInstance.modified == [], "Unexpected .deleted == %r " % self.FsInstance.modified
        os.remove(self.STATIC_FILE_PATH)
        assert self.FsInstance.deleted == [ self.STATIC_FILE ], "Unexpected .deleted == %r " % self.FsInstance.modified
        try: self.FsInstance.deleted = [ self.MISSING_FILE ]
        except AttributeError: pass
        else:
            assert False, ".deleted attribute should be read-only."
            
    def test_add_method(self):
        """.add() method should work like set-add"""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False,dbfilebase=self.ALT_DBFILENAME)
        assert self.STATIC_FILE not in self.FsInstance
        self.FsInstance.add(self.STATIC_FILE_PATH)
        assert self.STATIC_FILE in self.FsInstance
        self.FsInstance.add(self.STATIC_FILE)
        assert self.STATIC_FILE in self.FsInstance
        assert self.STATIC_FILE_PATH in self.FsInstance
        assert len(self.FsInstance) == 1
        self.FsInstance.add(self.ALT_DBFILENAME)
        assert self.ALT_DBFILENAME not in self.FsInstance
        assert len(self.FsInstance) == 1
        self.FsInstance.add(self.MISSING_FILE)
        assert len(self.FsInstance) == 2
        
    def test_discard_method(self):
        """.discard() method should work like set remove/delete"""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False,dbfilebase=self.ALT_DBFILENAME)
        assert self.STATIC_FILE not in self.FsInstance
        self.FsInstance.add(self.STATIC_FILE_PATH)
        assert self.STATIC_FILE in self.FsInstance
        self.FsInstance.discard(self.STATIC_FILE)
        assert self.STATIC_FILE not in self.FsInstance
        self.FsInstance.discard(self.STATIC_FILE)
        
    def test_register_method(self):
        """.register() works with single and multiple filenames"""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False,dbfilebase=self.ALT_DBFILENAME)
        assert self.STATIC_FILE not in self.FsInstance
        self.FsInstance.register(self.STATIC_FILE_PATH)
        assert self.STATIC_FILE in self.FsInstance
        self.FsInstance.register(self.MISSING_FILE,"OtherFile.txt","RandomFile.txt")
        assert self.MISSING_FILE in self.FsInstance
        
    @nt.raises(KeyError)
    def test_register_keyerror(self):
        """.register() raises KeyError for duplicates"""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False,dbfilebase=self.ALT_DBFILENAME)
        assert self.STATIC_FILE not in self.FsInstance
        self.FsInstance.register(self.STATIC_FILE_PATH)
        assert self.STATIC_FILE in self.FsInstance
        self.FsInstance.register(self.STATIC_FILE)
        
    @nt.raises(KeyError)
    def test_register_keyerror_dbfile(self):
        """.register() raises KeyError for DB Filename"""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False,dbfilebase=self.ALT_DBFILENAME)
        assert self.ALT_DBFILENAME not in self.FsInstance
        self.FsInstance.register(self.ALT_DBFILENAME)
        
    def test_filename_method(self):
        """.filename() returns a tempfile filename."""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False,dbfilebase=self.ALT_DBFILENAME)
        FileName = self.FsInstance.filename(extension=".txt")
        assert FileName.endswith('.txt')
        assert os.path.basename(FileName).startswith('tmp')
        
    def test_filename_method_with_fd(self):
        """.filename() returns a tempfile filename and a file descriptor"""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False,dbfilebase=self.ALT_DBFILENAME)
        FileName, FileObjc = self.FsInstance.filename(extension=".txt",getfd=True)
        FileObjc.write("HI THERE\n")
        assert os.path.basename(FileName).startswith('tmp')
        assert FileName.endswith('.txt')
        
    def test_delete_method(self):
        """.delete() method should work like set remove/delete"""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False,dbfilebase=self.ALT_DBFILENAME)
        assert self.STATIC_FILE not in self.FsInstance
        self.FsInstance.add(self.STATIC_FILE_PATH)
        self.FsInstance.add(self.MISSING_FILE)
        assert self.STATIC_FILE in self.FsInstance
        assert self.MISSING_FILE in self.FsInstance
        self.FsInstance.delete(self.STATIC_FILE,self.MISSING_FILE)
        assert self.STATIC_FILE not in self.FsInstance
        assert self.MISSING_FILE not in self.FsInstance
        
        
    @nt.raises(KeyError)
    def test_delete_keyerror(self):
        """.delete() method raises a KeyError for duplicate deletes"""
        self.FsInstance = self.FsClass(self.BASE,self.NAME,autodiscover=False,dbfilebase=self.ALT_DBFILENAME)
        assert self.STATIC_FILE not in self.FsInstance
        self.FsInstance.delete(self.STATIC_FILE_PATH)
        
        
class test_FileSet(BaseFileSetTests):
    """AstroObject.file.fileset.FileSet"""
    FsClass = FileSet
    