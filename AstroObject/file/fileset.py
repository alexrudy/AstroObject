# -*- coding: utf-8 -*-
# 
#  fileset.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-05-17.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 
u"""
:mod:`file.fileset` – File Group management
-------------------------------------------
File sets are groups of monitored files, held in a single directory.
.. autoclass::
    AstroObject.file.fileset.FileSet
    :members:
    :inherited-members:
    
.. autoclass::
    AstroObject.file.fileset.TempFileSet
    :members:
    :inherited-members:
    
.. autoclass::
    AstroObject.file.fileset.HashedFileSet
    :members:
    :inherited-members:

    
"""
# Standard Python Modules
import sys
from datetime import datetime
import logging
import os
import tempfile
import hashlib
import shutil
import collections

from ..AstroConfig import Configuration

__log__ = logging.getLogger(__name__)

class FileSet(collections.MutableSet):
    """Set of files which should be tracked. The set as a whole can then be opened or closed."""
    def __init__(self, base, name="", isopen=True, persist=False, autodiscover=True):
        super(FileSet, self).__init__()
        self.persist = persist
        self.autodiscover = autodiscover
        self._timeformat = "%Y-%m-%dT%H:%M:%S"
        self._createtime = datetime.now()
        self._files = Configuration({})
        self._open_files = {}
        self._set_directory(os.path.join(base,name))
        self._open = isopen
        self.log = __log__
        self.log.log(2,"IRAF File Set created with directory %s" % self._directory)
    
    def __len__(self):
        """Length of this fileset."""
        return len(self._files)
    
    def __contains__(self,filepath):
        """Containment check"""
        return os.path.relpath(filepath) in self._files
        
    def __iter__(self):
        """Iterable implementation"""
        return iter(self._files)
        
    def __enter__(self):
        """Enter this file-set's contextual mode."""
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        """Leave the fileset contextual state."""
        self.close(check=False)
        
    def add(self,filepath):
        """Insert filepath into the set"""
        self.register(filepath)
        
    def discard(self,filepath):
        """docstring for discard"""
        self.delete(filepath)
    
    def _persist(self):
        """Write the persistance database to a file in the directory."""
        if not self.persist:
            return
        self._files["Date"] = self._createtime.strftime(self._timeformat)
        self._files.save(self._dbfilename)
        del self._files["Date"]
        
    def _reload(self):
        """Reload the persistance databse to this object."""
        if os.path.exists(self._dbfilename) and self.persist:
            self._files.load(self._dbfilename)
            os.remove(self._dbfilename)
            self._createtime = datetime.strptime(self._files.pop("Date"),self._timeformat)
            return True
        return False
        
    @property
    def files(self):
        """A list of all of the files."""
        self._autodiscover_files()
        return self._files.keys()
        
    @property
    def directory(self):
        """Name of FileSet is open"""
        return self._directory
        
    def _set_directory(self,base):
        """Set the directory from the given base."""
        if not os.path.exists(base):
            os.mkdir(base)
        if os.path.basename(base) != "":
            base = os.path.join(base,"")    
        self._directory = os.path.relpath(base)
        self._dbfilename = os.path.join(self.directory,".AOFSdb.yml")
        self._reload()
        
    def _autodiscover_files(self):
        """Automatically discover files that are in this fileset."""
        if not self.autodiscover:
            return
        for root, dirs, files in os.walk(self.directory):
            for filepath in files:
                fullpath = os.path.join(root,filepath)
                if fullpath not in self and os.path.relpath(fullpath) != self._dbfilename:
                    self.add(fullpath)
        
    @property
    def open(self):
        """If the FileSet is open"""
        return self._open
        
    @property
    def modified(self):
        """A list of files in the fileset that have been modified since registering."""
        self._autodiscover_files()
        modified = []
        for filepath in self._files:
            filepath = os.path.relpath(filepath)
            if os.path.exists(filepath) and not filepath == self._dbfilename:
                if os.stat(filepath).st_mtime > self._files[filepath]:
                    modified += [filepath]
        if len(modified) > 0:
            self._persist()
        return modified
        
    @property
    def deleted(self):
        """If any files in the fileset have been deleted since registering."""
        self._autodiscover_files()
        deleted = []
        for filepath in self._files:
            filepath = os.path.relpath(filepath)
            if not os.path.exists(filepath):
                deleted += [filepath]
                self._files[filepath] = 0.0
        if len(deleted) > 0:
            self._persist()
        return deleted
    
    def open_fd(self,*args):
        """Return a file descriptor for the given filepath."""
        if not self.open:
            raise IOError("File set is not open!")
        args = list(args)
        filepath = args[0]
        if filepath not in self._open_files:
            self._open_files[filepath] = open(*args)
        elif len(args) > 1:
            self.log.warning("File descriptor already open, not adjusting mode etc.")
        return self._open_files[filepath]
        
    def close_fd(self,*filepaths):
        """docstring for closefd"""
        for filepath in filepaths:
            filepath = os.path.relpath(filepath)
            if self._open_files[filepath].open:
                self._open_files[filepath].close()
            del self._open_files[filepath]
            
    @property
    def active_fd(self):
        """Whether this set has any active File Descriptors"""
        for fn in self._open_files.keys():
            if not self._open_files[fn].open:
                del self._open_files[fn]
        return self._open_files.keys()
    
    def delete(self,*filepaths):
        """Remove filepaths from the fileset"""
        if not self.open:
            raise IOError("File set is not open!")        
        for filepath in filepaths:
            filepath = os.path.relpath(filepath)
            if filepath in self._open_files:
                self.close_fd(filepath)
            del self._files[filepath]
            if os.path.exists(filepath):
                os.remove(filepath)
        self._persist()
        return self._files.keys()
        
    def updated(self,*filepaths):
        """Mark the given filepaths as updated."""
        if not self.open:
            raise IOError("File set is not open!")
        for filepath in filepaths:
            filepath = os.path.relpath(filepath)
            if filepath not in self:
                raise KeyError("Cannot update unregistered file!")
            if os.path.exists(filepath):
                self._files[filepath] = os.stat(filepath).st_mtime
            else:
                self._files[filepath] = 0.0
        self._persist()
        return self._files.keys()
        
        
    def close(self,check=True):
        """Close this FileSet"""
        if not self.open:
            raise IOError("May only close an open FileSet")
        
        if check and len(self.active_fd) != 0:
            self.log.debug("Active File Handles Preventing Close: %r" % self.active_fd)
            
            raise IOError("Files have not all been closed.")
        else:
            self.close_fd(*self.active_fd)
            
        if check and len(self.modified) != 0:
            self.log.debug("Modified Files Preventing Close: %r" % self.modified)
            raise IOError("Files have been modified.")
        
        shutil.rmtree(self.directory)
        self.log.log(2,"File Set closed with directory %s" % self._directory)
        self._directory = None
        self._files = Configuration({})
        self._open = False
        
    def move(self,base,check=True):
        """Move this FileSet to a new base location."""
        files = self._files
        shutil.copytree(olddir,base)
        self.close()
        self._set_directory(base)
        self._open = True
        self._files = files
        self._persist()
    
    def filename(self,extension=None,prefix=None,getfd=False,**kwargs):
        """Return a filename which is a member of this fileset. The filename will be created with mkstemp"""
        if prefix == None:
            prefix = 'tmp'
        fileobj, filename = tempfile.mkstemp(suffix=extension,prefix=prefix,dir=self.directory,**kwargs)
        if getfd:
            self._open_files[filename] = fileobj
            self.register(filename)
            return filename, fileobj
        else:    
            os.close(fileobj)
            self.register(filename)
            return filename
        
    def register(self,*filenames):
        """Register a filename as a member of this fileset."""
        if not self.open:
            raise IOError("File set is not open!")
        for filename in filenames:
            fbase, fname = os.path.split(filename)
            if fbase == "" or fbase == self.directory:
                filename = fname
            fullpath = os.path.relpath(os.path.join(self.directory,filename))
            if fullpath in self._files:
                raise KeyError("Filepath %s already exists in fileset." % filename)
            if fullpath == self._dbfilename:
                raise KeyError("Cannot add DB to database.")
            if os.path.exists(fullpath):
                self._files[fullpath] = os.stat(fullpath).st_mtime
            else:
                self._files[fullpath] = 0.0
        self._persist()
        return self._files.keys()

class TempFileSet(FileSet):
    """A set of temporary files."""
    def __init__(self, base=None, name='tmp', persist = False, **kwargs):
        base = tempfile.mkdtemp(prefix=name, dir=base)
        if persist and base is None:
            raise AttributeError("Temporary File Sets cannot persist across processes, as they are not defined outside of a single process. ")
        super(TempFileSet, self).__init__(base = base, persist = persist, **kwargs)
        
            
class HashedFileSet(FileSet):
    """A set of files in a folder with a hashed name"""
    def __init__(self, base, hashable = __name__, **kwargs):
        _hash = hashlib.sha1()
        _hash.update(hashable)
        self._hashhex = _hash.hexdigest()
        self._prehashbase = base
        base = os.path.join(self._prehashbase,self.hash)
        super(HashedFileSet, self).__init__(base, **kwargs)
    
    @property
    def hash(self):
        """Returns the hexadecimal hash. If set, set the hashable string, and it will update the hashhex"""
        return self._hashhex
        
    @hash.setter    
    def hash(self,hashable):
        """Set a new hash for this object."""
        _hash = hashlib.sha1()
        _hahs.update(hashable)
        self._hashhex = _hash.hexdigest()
        self.move(os.path.join(self._prehashbase,self.hash))
        
        