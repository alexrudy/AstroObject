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
File sets are groups of monitored files, held in a single directory. They can return a list of modified files in the directory, as well as files that have gone missing. File sets can either monitor only files which are explicitly registered with the fileset, or can autodiscover new files. Filesets can clean themselves up, deleting all member files in the fileset.


:class:`FileSet` – Generic Fileset
**********************************
A fileset which simply uses a ``base/name`` explicit directory structure.

.. autoclass::
    AstroObject.file.fileset.FileSet
    :members:
    :inherited-members:
    
    
:class:`TempFileSet` – Temporary File Set
*****************************************
A fileset which uses temporary directories for the fileset. Can use the system temporary file directory as the file base.

.. autoclass::
    AstroObject.file.fileset.TempFileSet
    :members:
    :inherited-members:


:class:`HashedFileSet` – Hahsed File Set
****************************************
A fileset that uses an SHA1 hash to set the name of the directory for use. Files are saved in ``base/hash`` directories. The hash can be updated, which will move the entire fileset to a new ``base/hash`` directory location.

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
    """A set of files to be monitored. The set of files must all be contained in a single parent directory. The file set will monitor the registered files for changes and modifications, and will notify (using :exc:`IOError`) the program if the fileset attempts to close with remianing modifications.
    
    :param string base: The base directory name for use with this file set.
    :param string name: The name of this particular fileset. Filesets are stored in ``base/name/``
    :param bool isopen: Whether to start the fileset as open. Closed filesets are read-only objects.
    :param bool persist: Whether this fileset should try to persist across instantiations.
    :param bool autodiscover: Whether this fileset should check the directory for new files automatically, and register those files.
    :keyword string timeformat: The format string for the :mod:`datetime` module to use when writing/reading from the database. There is no reason to need to change this default, but it is supported just in case.
    :keyword string dbfilebase: The base name of the persistance database. By default it is ``.AOFSdb.yml``. If this filename *could* conflict with other files you might add to the file-set, you might want to change it to a non-conflicting filename. Files should have the ``.yml,.yaml`` extension.
    
    **Persistance**:
    
    Persistant filesets will remember thier state using a database file between application instances. If the fileset is supposed to persist, it will write a database file to the fileset directory. The database file records the currently known modification times for each registered file. The database file will be automatically loaded when the fielset is created, or the directory is changed (with :meth:`move`). The database will also be automatically written whenever changes occur. 
    
    If the load on the program is too heavy due to constant file-set access and modification, you can toggle the persistance mode using the :attr:`persist` attribute. The database is only ever loaded when the fileset is initialized. 
    
    **Autodiscovery**:
    
    If the fileset has autodiscovery enabled, most method calls will cause the fileset to examine its container directory for new files. New files in the container directory which are not registered members of the fileset will be added to the fileset.
    
    If the load on the program is too heavy due to constant file-set access and modification, you can toggle the autodiscovery mode using the :attr:`autodiscover` attribute.
    
    **Closed vs. Open Filesets**:
    Closed filesets are read-only filesets. If the fileset is closed, it will have a directory, but files cannot be registered or unregistered. Calling the :meth:`close` will normally close **and** delete the fileset, unless ``clean=False`` is passed to the close method. 
    """ 
    def __init__(self, base, name="", isopen=True, persist=False, autodiscover=True, timeformat="%Y-%m-%dT%H:%M:%S", dbfilebase=".AOFSdb.yml"):
        super(FileSet, self).__init__()
        # Start both mode variables as false for initialization process.
        self._persistance_value = persist
        self._autodiscover_value = autodiscover
        self._timeformat = timeformat
        self._dbfilebase = dbfilebase
        self._createtime = datetime.now()
        self._files = Configuration({})
        self._open_files = {}
        self._autodiscovery_in_progress = False
        self._set_directory(os.path.join(base,name))
        self._open = isopen
        self.log = __log__
        self.log.log(2,"IRAF File Set created with directory %s" % self._directory)
    
    @property
    def persist(self): #: = False
        """Enable or disable persistance of this fileset. Must be (bool). If the fileset is initialized with ``persist=False`` (the default), then the database will not be reloaded, and will instead be overwritten."""
        return self._persistance_value
        
    @persist.setter
    def persist(self,value):
        self._persistance_value = value
        self._persist()
    
    @property
    def autodiscover(self): #: = True
        """Enable or disable autodiscovery of new files in this fileset. Must be (bool)."""
        return self._autodiscover_value
        
    @autodiscover.setter
    def autodiscover(self,value):
        self._autodiscover_value = value
        self._autodiscover_files()
    
    @property
    def date(self):
        """Creation date for this fileset"""
        return self._createtime
    
    def __len__(self):
        """Number of files contained in this fileset."""
        return len(self._files)
    
    def __contains__(self,filepath):
        """Check whether a filepath is contained in this fileset."""
        return self.get_cpath(filepath) in self._files
        
    def __iter__(self):
        """Returns an iterable over all of the filepaths which are registered in this fileset."""
        return iter(self._files)
        
    def __enter__(self):
        """Enter this fileset's contextual mode. Contextual mode ensures that the fileset is closed on departure. When using a fileset in contextual mode, changes to the files are monitored, but the fileset does not ensure all changes have been registered when the fileset closes. The fileset is guaranteed to close in the end.
        
        ::
            with FileSet("Files", name="Data") as Files:
                Files.register("Somefile.dat")
                fd = Files.open_fd("Somefile.dat","w")
                fd.write("Some Text In the File")
                Files.close_fd("Somefile.dat")
                Files.update("Somefile.dat")
        
        """
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        """Leave the fileset contextual state. Contextual mode ensures that the fileset is closed on departure. When using a fileset in contextual mode, changes to the files are monitored, but the fileset does not ensure all changes have been registered when the fileset closes. The fileset is guaranteed to close in the end. See :meth:`__enter__``."""
        self.close(check=False)
    
    def _persist(self):
        """Write the persistance database to the database file in the fileset directory."""
        if not self.persist:
            return
        self._files["Date"] = self._createtime.strftime(self._timeformat)
        self._files.save(self._dbfilename)
        del self._files["Date"]
        
    def _reload(self):
        """Reload the persistance databse to this object. 
        
        This method should only be called when the fileset is first instantiated. This is because the loading overwrites existing data about modification times, and will not preserve any calls to :meth:`update` made after object initialization. The reload function will preserve the registration of new files into the fileset.
        
        :returns bool: Whether the persistance database was reloaded successfully.
        """
        if os.path.exists(self._dbfilename) and self.persist:
            self._files.load(self._dbfilename)
            os.remove(self._dbfilename)
            self._createtime = datetime.strptime(self._files.pop("Date"),self._timeformat)
            return True
        return False
        
    
        
    def _set_directory(self,base):
        """Set the directory for this fielset from the given base name. This method ensures that the database filename attribute remains consistent."""
        if not os.path.exists(base):
            os.mkdir(base)
        if os.path.basename(base) != "":
            base = os.path.join(base,"")    
        self._directory = os.path.relpath(base)
        self._dbfilename = os.path.join(self.directory,self._dbfilebase)
        self._reload()
        
    def _autodiscover_files(self):
        """Automatically discover files that are in this fileset using :func:`os.walk`. Automatically discovered files are registered with the fileset.
        
        This method automatically short-circuits if the fileset is closed, or if autodiscovery is not enabled. It also automatically prevents recursive calls to itself."""
        if not self.autodiscover or not self.open or self._autodiscovery_in_progress:
            return
        self._autodiscovery_in_progress = True
        for root, dirs, files in os.walk(self.directory):
            for filepath in files:
                fullpath = os.path.join(root,filepath)
                if fullpath not in self and os.path.relpath(fullpath) != self._dbfilename:
                    self.add(fullpath)
        self._autodiscovery_in_progress = False
    
    @property
    def files(self):
        """A list of all of the files registered to this fileset."""
        self._autodiscover_files()
        return self._files.keys()
        
    @property
    def directory(self):
        """The directory name for this fileset. This is a read-only attribute. To change the directory a fileset is stored in, use :meth:`move`."""
        return self._directory
    
    @property
    def open(self):
        """Whether this fileset is open or not. Closed filesets are read-only objects, and cannot be re-opened."""
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
        """A list of files in the fileset have been deleted since registering."""
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
    
    @property
    def active_fd(self):
        """Returns a list of open file descriptors for this fileset. Any file descriptors that have already been closed are removed from the fileset's registry of file descriptors."""
        for fn in self._open_files.keys():
            if not self._open_files[fn].open:
                del self._open_files[fn]
        return self._open_files.keys()
        
    def add(self,filepath):
        """Insert filepath into the fileset. Ensures that filepaths are not duplicated in the fileset."""
        self.register(filepath)
        
    def discard(self,filepath):
        """Remove a filepath from the fileset. If the filepath exists, it will be deleted. This method will raise a :exc:`KeyError` if the filepath is not registered."""
        self.delete(filepath)
        
    def get_cpath(self,filename):
        """Return the cache object-like filepath for the requested filepath. This helps ensure that calls to register, etc. will not fail."""
        fbase, fname = os.path.split(filename)
        if fbase == "" or os.path.relpath(fbase) == self.directory:
            filename = fname
        return os.path.relpath(os.path.join(self.directory,filename))
                
    def register(self,*filenames):
        """Register filenames as a members of this fileset. Multiple filenames can be registered. They are registered by thier relative path by default.
        
        :param string filename: A path to a file to be registered. The path must contain no directory, or contain only the fileset directory, or be provided as a relative path from the base of the fileset directory.
        :raises KeyError: If the file is already registered.
        :raises IOError: If the fileset is closed.
        :returns: A list of all registered files in this fileset.
        """
        if not self.open:
            raise IOError("File set is not open!")
        for filename in filenames:
            fullpath = self.get_cpath(filename)
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
    
    def filename(self,extension=None,prefix='tmp',getfd=False,**kwargs):
        """Return a temporary filename which is a member of this fileset.
        
        :param string extension: The temporary file's extension (actually appears as suffix).
        :param string prefix: The temporary file's prefix. Defualts to ``tmp``.
        :param bool getfd: Whether to return an open file descriptor to this file as well as the filename.
        :keywords: Keyword arguments to pass to :func:`tempfile.mkstemp`
        :returns filename: Relative path filename for the temporary file.
        :returns filename,fileobj: File descriptor for temporary file if ``getfd=True``.
        
         """
        fileobj, filename = tempfile.mkstemp(suffix=extension,prefix=prefix,dir=self.directory,**kwargs)
        if getfd:
            self._open_files[filename] = fileobj
            self.register(filename)
            return filename, fileobj
        else:    
            os.close(fileobj)
            self.register(filename)
            return filename
    
    def delete(self,*filepaths):
        """Remove filepaths from the fileset, and delete the underlying file. Multiple filepaths can be passed in as arguments. This method will raise a :exc:`KeyError` if the filepath is not registered. To delete all files in the fileset, use::
            
            fileset = FileSet("File",name="Data")
            fileset.add("file1.txt")
            fileset.add("file2.txt")
            fileset.delete(*fileset.files)
            
        
        :returns: A list of files in this fileset.
        
        """
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
        """Mark the given filepaths as updated. Multiple filepaths can be passed in as arguments. This method will raise a :exc:`KeyError` if the filepath is not registered.
        
        :returns: A list of files in this fileset.
        
        """
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
    
    
    def open_fd(self,filepath,*args):
        """Return a file descriptor for the given filepath. The file descriptor will be return and monitored by this fileset. If the fileset attempts to close, it will ensure that all attached file descriptors are closed. This is a safer way to get file-descriptors to use over a long period of time. Any other arguments passed to this method will be used for the call to :func:`open` as the file mode, etc.
        
        .. Note:: This method has not been tested with context managers yet, and should not be used as such.
        
        """
        if not self.open:
            raise IOError("File set is not open!")
        if filepath not in self._open_files:
            self._open_files[filepath] = open(filepath,*args)
        elif len(args) > 1:
            self.log.warning("File descriptor already open, not adjusting mode etc.")
        return self._open_files[filepath]
        
    def close_fd(self,*filepaths):
        """Close the file descriptors which are open and registered to the filepaths. Multiple file paths can be passed to this function as a series of arguments.
        
        ::  
            
            fileset = FileSet("File",name="Data")
            fileset.open_fd("file1.txt")
            fileset.open_fd("file2.txt")
            fileset.close_fd("file1.txt","file2.txt")
            
        
        To close all open file descriptors in this fileset::
            
            fileset = FileSet("File",name="Data")
            fileset.open_fd("file1.txt")
            fileset.open_fd("file2.txt")
            fileset.close_fd(*fileset.active_fd)
            
        """
        for filepath in filepaths:
            filepath = os.path.relpath(filepath)
            if self._open_files[filepath].open:
                self._open_files[filepath].close()
            del self._open_files[filepath]
        
    def move(self,base,check=False):
        """Move this fileset to a new base location. The old directory for this fileset will be removed in its entirety.
        
        :param string base: The new base directory to be used.
        :param bool check: Whether to check the old directory for modifications/additions before moving.
        
        Note that with ``check=False``, the entire old directory will be removed. This will remove even files that are not registered to the old fileset."""
        persist, self.persist = self.persist, True
        self._persist()
        shutil.copytree(olddir,base)
        self.close(check=check)
        self._set_directory(base)
        self._open = True
        self._reload()
        self.persist = persist
        self._persist()
    
        
    def close(self, check=True, clean=True):
        """Close this fileset, rendering it as a read-only object. By default, close also deletes all registered files and the persistance database.
        
        :param bool check: Whether to ensure that all files have not been modified. Default ``True``.
        :param bool clean: Whether to delete all registered files from the system. Default ``True``.
        
        If you want to use this fileset as a read-only fileset, call ``fileset.close(check=False,clean=False)``.
        
        With ``check=True``, the close method will first ensure that there are no open file descriptors. Then it will ensure that there are no modified files. With ``check=False``, it will close any open registered file descriptors. With ``clean=True``, it will delete all registered files. If the directory still contains files after all registered files are removed, it will remain. If ``clean=True`` and ``check=False``, it will delete all files in the fileset directory, regardless of whether they have been registered. Closing a fileset with ``clean=True`` will prevent that fileset from persisting.
        """
        if not self.open:
            raise IOError("May only close an open FileSet")
        if self.persist and clean:
            self.log.warning("Closing and cleaning a persistent fileset.")
        
        if check and len(self.active_fd) != 0:
            self.log.debug("Active File Handles Preventing Close: %r" % self.active_fd)
            
            raise IOError("Files have not all been closed.")
        else:
            self.close_fd(*self.active_fd)
            
        if check and len(self.modified) != 0:
            self.log.debug("Modified Files Preventing Close: %r" % self.modified)
            raise IOError("Files have been modified.")
            
        if clean and check:
            self.delete(*self.files)
            if os.path.exists(self._dbfilename):
                os.remove(self._dbfilename)
            try:
                os.rmdir(self.directory)
            except OSError:
                self.log.warning("Directory was not deleted, as it isn't empty.")
        elif clean and not check:
            shutil.rmtree(self.directory)
        self.log.log(2,"File Set closed with directory %s" % self._directory)
        self._open = False
        

class TempFileSet(FileSet):
    """A set of files to be monitored in a temporary directory. The set of files must all be contained in a single parent directory. The file set will monitor the registered files for changes and modifications, and will notify (using :exc:`IOError`) the program if the fileset attempts to close with remianing modifications.
    
    :param string base: The base directory name for use with this file set. If ``None``, will use the operating systems temporary directory.
    :param string name: The name of this particular fileset. Filesets are stored in ``base/name/``
    :param bool isopen: Whether to start the fileset as open. Closed filesets are read-only objects.
    :param bool persist: Whether this fileset should try to persist across instantiations. Persistance is not supported in operating system temporary directories.
    :keyword bool autodiscover: Whether this fileset should check the directory for new files automatically, and register those files.
    :keyword string timeformat: The format string for the :mod:`datetime` module to use when writing/reading from the database. There is no reason to need to change this default, but it is supported just in case.
    :keyword string dbfilebase: The base name of the persistance database. By default it is ``.AOFSdb.yml``. If this filename *could* conflict with other files you might add to the file-set, you might want to change it to a non-conflicting filename. Files should have the ``.yml,.yaml`` extension.
    
    **Persistance**:
    
    Persistant filesets will remember thier state using a database file between application instances. If the fileset is supposed to persist, it will write a database file to the fileset directory. The database file records the currently known modification times for each registered file. The database file will be automatically loaded when the fielset is created, or the directory is changed (with :meth:`move`). The database will also be automatically written whenever changes occur.
    
    If the load on the program is too heavy due to constant file-set access and modification, you can toggle the persistance mode using the :attr:`persist` attribute. The database is only ever loaded when the fileset is initialized. 
    
    .. Warning:: Persistance is not supported when the temporary fileset is initialized with ``base=None``, as persistance is not supported in operating system level temporary directories. This is to prevent stray temporary file directories from appearing in difficult-to-find locations.
    
    **Autodiscovery**:
    
    If the fileset has autodiscovery enabled, most method calls will cause the fileset to examine its container directory for new files. New files in the container directory which are not registered members of the fileset will be added to the fileset.
    
    If the load on the program is too heavy due to constant file-set access and modification, you can toggle the autodiscovery mode using the :attr:`autodiscover` attribute.
    
    **Closed vs. Open Filesets**:
    
    Closed filesets are read-only filesets. If the fileset is closed, it will have a directory, but files cannot be registered or unregistered. Calling the :meth:`close` will normally close **and** delete the fileset, unless ``clean=False`` is passed to the close method."""
    def __init__(self, base=None, name='tmp', persist = False, **kwargs):
        self._temporary_base_directory = False
        if base is None:
            self._temporary_base_directory = True
        base = tempfile.mkdtemp(prefix=name, dir=base)
        super(TempFileSet, self).__init__(base = base, persist = persist, **kwargs)
        
        
    
    @property
    def persist(self):
        """Enable or disable persistance of this fileset. Must be (bool). If the fileset is initialized with ``persist=False`` (the default), then the database will not be reloaded, and will instead be overwritten.
        
        .. Warning:: Persistance is not supported when the temporary fileset is initialized with ``base=None``, as persistance is not supported in operating system level temporary directories. This is to prevent stray temporary file directories from appearing in difficult-to-find locations.
        """
        return self._persistance_value
    
    @persist.setter
    def persist(self,value):
        if value and self._temporary_base_directory:
            raise AttributeError("Temporary File Sets cannot persist across processes, as they are not defined outside of a single process. ")
        self._persistance_value = value
        self._persist()
            
class HashedFileSet(FileSet):
    """A set of files to be monitored contained in a directory with an SHA1 hash name. The file set will monitor the registered files for changes and modifications, and will notify (using :exc:`IOError`) the program if the fileset attempts to close with remianing modifications.
    
    :param string base: The base directory name for use with this file set.
    :param string hashable: The string to be used for the SHA1 hash folder name.
    :keyword bool isopen: Whether to start the fileset as open. Closed filesets are read-only objects.
    :keyword bool persist: Whether this fileset should try to persist across instantiations.
    :keyword bool autodiscover: Whether this fileset should check the directory for new files automatically, and register those files.
    :keyword string timeformat: The format string for the :mod:`datetime` module to use when writing/reading from the database. There is no reason to need to change this default, but it is supported just in case.
    :keyword string dbfilebase: The base name of the persistance database. By default it is ``.AOFSdb.yml``. If this filename *could* conflict with other files you might add to the file-set, you might want to change it to a non-conflicting filename. Files should have the ``.yml,.yaml`` extension.
    
    **Persistance**:
    
    Persistant filesets will remember thier state using a database file between application instances. If the fileset is supposed to persist, it will write a database file to the fileset directory. The database file records the currently known modification times for each registered file. The database file will be automatically loaded when the fielset is created, or the directory is changed (with :meth:`move`). The database will also be automatically written whenever changes occur. 
    
    If the load on the program is too heavy due to constant file-set access and modification, you can toggle the persistance mode using the :attr:`persist` attribute. The database is only ever loaded when the fileset is initialized. 
    
    **Autodiscovery**:
    
    If the fileset has autodiscovery enabled, most method calls will cause the fileset to examine its container directory for new files. New files in the container directory which are not registered members of the fileset will be added to the fileset.
    
    If the load on the program is too heavy due to constant file-set access and modification, you can toggle the autodiscovery mode using the :attr:`autodiscover` attribute.
    
    **Closed vs. Open Filesets**:
    Closed filesets are read-only filesets. If the fileset is closed, it will have a directory, but files cannot be registered or unregistered. Calling the :meth:`close` will normally close **and** delete the fileset, unless ``clean=False`` is passed to the close method.
    
    """
    def __init__(self, base, hashable = __name__, **kwargs):
        _hash = hashlib.sha1()
        _hash.update(hashable)
        self._hashhex = _hash.hexdigest()
        self._prehashbase = base
        base = os.path.join(self._prehashbase,self.hash)
        super(HashedFileSet, self).__init__(base, **kwargs)
    
    @property
    def hash(self):
        """Returns the hexadecimal hash digest (the SHA1 which becomes the directory name). If set, set the hashable string, and it will update the hashhex to the new value, and move the fileset to that new location using :meth:`move`."""
        return self._hashhex
        
    @hash.setter    
    def hash(self,hashable):
        _hash = hashlib.sha1()
        _hahs.update(hashable)
        self._hashhex = _hash.hexdigest()
        self.move(self._hashhex)
        
    def move(self,base,check=False):
        """Move this fileset to a new base location. The old directory for this fileset will be removed in its entirety. The new location will have the hashable base added to the directory by default.
        
        :param string base: The new base directory to be used.
        :param bool check: Whether to check the old directory for modifications/additions before moving.
        
        Note that with ``check=False``, the entire old directory will be removed. This will remove even files that are not registered to the old fileset."""
        super(HashedFileSet, self).move(os.path.join(base,self.hash), check)
        
        
        