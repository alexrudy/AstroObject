# -*- coding: utf-8 -*-
# 
#  iraftools.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-04-19.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.0.0
# 
u"""
:mod:`iraftools` – IRAF integration facility
============================================

This module provides an interface for using :mod:`AstroObject` with PyIRAF

:class:`IRAFObject` – Intefrace to :class:`IrafTools`
-----------------------------------------------------

.. class::
    AstroObject.iraftools.IRAFObject
    This is an example class which has used :func:`UseIRAFTools`
    
    .. method:: iin(statename=None,extension='.fits')
        
        Returns a filename for a ``fits`` file from the given statename which can be used as input for IRAF tasks. This method should be used for files which will not be modified, as modifications will not be captured by the system. For files which are input, but will be modified, use :meth:`imod`.
        
        :param statename: The name of the **frame** to use for input.
        :param extension: The file extension to use.
        :returns: Filename for use with PyRAF
    
    .. method:: iout(statename=None,extension='.fits',append=None)
        
        Returns a filename for a ``fits`` file from the given statename which can be used for output for IRAF tasks. The file is not created, but will be read back into this **object** when :meth:`idone` is called.
        
        :param statename: The name of the **frame** to use for output.
        :param extension: The file extension to use.
        :param append: A string to append to the state names
        :returns: Filename for use with PyRAF
    
    .. method:: imod(statename=None,newstatename=None,extension='.fits',append=None)
    
        Returns a filename for a ``fits`` file from the given statename which can be used as input for IRAF tasks which modify a file in-place. The file will be reloaded when :meth:`idone` is called.
        
        :param statename: The name of the **frame** to use for input.
        :param newstatename: The name of the **frame** to use fo the output. If ``None``, uses ``statename``
        :param extension: The file extension to use.
        :param append: A string to be appended tp the new state name.
        :returns: Filename for use with PyRAF
        
    .. method:: iinat(*statenames,extension='.fits')
    
        Returns a filename for an "@"-list. The "@"-list lists fits files for each frame provided. These fitsfiles are created automatically. The "@"-list should not be used for in-place modification, for that, use :meth:`imodat`.
        
        :param statenames: Names of states to be included in the "@"-list.
        :param extension: The file extension to use.
        :retunrs: Filename of the "@"-list
        
    .. method:: ioutat(*statenames,append=None,extension='.fits')
        
        Returns a filename for an "@"-list. The "@"-list lists fits files for each frame provided. These fits-files will be output destinations. They will be re-read into the object when :meth:`idone` is called.
        
        :param statenames: Names of states to be included in the "@"-list.
        :param extension: The file extension to use.
        :param append: A string to append to the state names
        :retunrs: Filename of the "@"-list
        
    .. method:: imodat(*statenames,append=None,extension='.fits')
        
        Returns a filename for an "@"-list. The "@"-list lists fits files for each frame provided. These fits-files will be in-place modification destinations. They will be re-read into the object when :meth:`idone` is called.
        
        :param statenames: Names of states to be included in the "@"-list.
        :param extension: The file extension to use.
        :param append: A string to append to the state names
        :retunrs: Filename of the "@"-list
        
    .. method:: idone()
    
        Cleans up the temporary files, reloading any files which need reloading. Should be called after the IRAF command has completed, before attempting to re-use the stage.

:class:`IrafTools` – Implementation of IRAF Tools
-------------------------------------------------

.. autoclass::
    AstroObject.iraftools.IrafTools
    :members:

"""

# Standard Scipy Toolkits
import numpy as np
import pyfits as pf
import scipy as sp

# Scipy Extras
from scipy import ndimage
from scipy.spatial.distance import cdist
from scipy.linalg import norm

# Standard Python Modules
import math, copy, sys, time, logging, os
import tempfile
import shutil

# Submodules from this system
from .Utilities import *
from .AstroObjectBase import BaseObject
from .AstroFITS import FITSFrame

__version__ = getVersion()

LOG = logging.getLogger(__name__)

IRAFSet = None
__module__ = sys.modules[__name__]

class IRAFFileSet(object):
    """An IRAF File Set"""
    def __init__(self,directory=None):
        super(IRAFFileSet, self).__init__()
        self._directory = tempfile.mkdtemp()
        if directory is not None:
            dbase,fname = os.path.split(directory)
            dparent = "".join(dbase.split("/")[:-1])
            if fname is not None:
                if os.exists(directory):
                    self._directory = directory
                elif os.exists(dparent):
                    os.mkdir(directory)
                    self._directory = directory        
        self._files = []
        self._open = True
        LOG.log(2,"IRAF File Set created with directory %s" % self._directory)
        
    @property
    def directory(self):
        """Name of FileSet is open"""
        return self._directory
        
    @property
    def open(self):
        """If the FileSet is open"""
        return self._open
        
    def close(self):
        """Close this IRAFFileSet"""
        assert self.open, "May only close an open IRAFFileSet"
        shutil.rmtree(self.directory)
        LOG.log(2,"IRAF File Set closed with directory %s" % self._directory)
        self._directory = None
        self._open = False
        
    def filename(self,extension=None,prefix=None):
        """Get a new filename for this set."""
        assert self.open, "File objects can only be created from open sets."
        if prefix == None:
            prefix = 'tmp'
        fileobj, filename = tempfile.mkstemp(suffix=extension,prefix=prefix,dir=self.directory)
        os.close(fileobj)
        self._files.append(filename)
        return filename
        

class IrafTools(object):
    """A class for managing interaction with IRAF"""
    def __init__(self,Object):
        super(IrafTools, self).__init__()
        if not isinstance(Object,BaseObject):
            raise ValueError("Object must be an instance of %r" % BaseObject.__class__.__name__)
        self.object = Object
        self.module = __module__
        self.IRAFFileSet = self.module.IRAFFileSet
        self._directory = None
        self._collect = {}
        if FITSFrame not in self.object.dataClasses:
            self.object.dataClasses += [FITSFrame]
    
    @property
    def active(self):
        """If the set is active for this group of iraftools"""
        return self.module.IRAFSet is not None
        
    @property
    def set(self):
        """Unique new set stored at the module level."""
        if self.module.IRAFSet is None or (not self.module.IRAFSet.open):
            self.module.IRAFSet = self.IRAFFileSet(directory=self._directory)
        return self.module.IRAFSet
    
    def wrap(self,func):
        """Wrap the function below this with the done protocol"""
        def newfunc(*args,**kwargs):
             rvalue = func(*args,**kwargs)
             self.done()
             return rvalue
        newfunc = make_decorator(func)(newfunc)
        return newfunc
    
    def directory(self,directory):
        """Set the IRAFSet directory for this object."""
        if directory is not None:
            dbase,fname = os.path.split(directory)
            dparent = "".join(dbase.split("/")[:-1])
            if fname is not None:
                if os.exists(directory):
                    self._directory = directory
                elif os.exists(dparent):
                    os.mkdir(directory)
                    self._directory = directory
                else:
                    raise ValueError("Can't find directory to set: %s" % dbase)
        else:
            self._directory = None
        
    def infile(self,statename=None,extension='.fits',**kwargs):
        """Returns a filename for a ``fits`` file from the given statename which can be used as input for IRAF tasks. This method should be used for files which will not be modified, as modifications will not be captured by the system. For files which are input, but will be modified, use :meth:`modfile`.
        
        :param statename: The name of the **frame** to use for input.
        :param extension: The file extension to use.
        :returns: Filename for use with PyRAF
        
        """
        if statename is None:
            statename = self.object.statename
        filename = self.set.filename(extension=extension,prefix=statename)
        self.object.write(states=[statename],filename=filename,clobber=True)
        LOG.log(2,"Created infile for state %s named %s" % (statename,filename))
        return filename
        
    def outfile(self,statename=None,append=None,extension='.fits',**kwargs):
        """
        Returns a filename for a ``fits`` file from the given statename which can be used for output for IRAF tasks. The file is not created, but will be read back into this **object** when :meth:`done` is called.
        
        :param statename: The name of the **frame** to use for output.
        :param extension: The file extension to use.
        :param append: A string to append to the state names
        :returns: Filename for use with PyRAF
    
        """
        if statename is None:
            statename = self.object.statename + "-iraf"
        if append is not None:
            statename += append
        if statename in self.object:
            raise KeyError("Cannot register state \'%s\' for output, state already exists in %s." % (statename,self.object))
        filename = self.set.filename(extension=extension,prefix=statename)
        os.unlink(filename)
        self.object.save(FITSFrame(data=None,label=statename))
        self._collect[statename] = filename
        LOG.log(2,"Created outfile for state %s named %s" % (statename,filename))
        return filename
        
    def modfile(self,statename,newstatename=None,append=None,extension='.fits',**kwargs):
        """Returns a filename for a ``fits`` file from the given statename which can be used as input for IRAF tasks which modify a file in-place. The file will be reloaded when :meth:`done` is called.
        
        :param statename: The name of the **frame** to use for input.
        :param newstatename: The name of the **frame** to use fo the output. If ``None``, uses ``statename``
        :param extension: The file extension to use.
        :param append: A string to be appended tp the new state name.
        :returns: Filename for use with PyRAF
        """
        if newstatename is None:
            newstatename = statename
        if append is not None:
            newstatename += append
        if statename is None:
            statename = self.object.statename
        filename = self.set.filename(extension=extension,prefix=statename)
        self.object.write(states=[statename],filename=filename,clobber=True)
        self.object.save(FITSFrame(data=None,label=newstatename))
        LOG.log(2,"Created modfile for state %s named %s" % (statename,filename))
        self._collect[newstatename] = filename
        return filename
        
    def _atfile(self,*statenames,**kwargs):
        """Generic atfile creation routine"""
        if len(statenames) > 1:
            statenames = self.object.list()
        atlist = self.set.filename(extension='.list')

        function = kwargs.pop('function',None)
        if function is None:
            raise TypeError("Must provide a filename creation function")
        
        with open(atlist,'w') as stream:
            for statename in statenames:
                filename = function(statename,**kwargs)
                stream.write("%s\n" % filename)
        LOG.log(2,"Created atlist for states %s named %s" % (statenames,atlist))
        return "@" + atlist

    def modatfile(self,*statenames,**kwargs):
        """File list for modification"""
        kwargs.pop("function",None)
        return self._atfile(*statenames,function=self.modfile,**kwargs)
    
    def inatfile(self,*statenames,**kwargs):
        """Return a filename with @ appended, for a file which lists a series of fitsfiles."""
        kwargs.pop("function",None)
        return self._atfile(*statenames,function=self.infile,**kwargs)

    def outatfile(self,*statenames,**kwargs):
        """Return a filename with @ appended, for a file which lists a series of fitsfiles"""
        kwargs.pop("function",None)
        return self._atfile(*statenames,function=self.outfile,**kwargs)
        
    def done(self):
        """Finish the IRAF statename."""
        if not self.active:
            return
        for statename,filename in self._collect.iteritems():
            self.object.remove(statename,clobber=True)
            states = self.object.read(filename=filename,statename=statename)
            LOG.log(2,"Collected file for state %s named %s" % (statename,filename))
            LOG.log(2,"States created: %s" % states)
        self._collect = {}
        self.set.close()

    def set_instance_methods(self):
        """Sets the instance shortcut methods on the object."""
        self.object.iin = self.infile
        self.object.iout = self.outfile
        self.object.iinat = self.inatfile
        self.object.ioutat = self.outatfile
        self.object.imod = self.modfile
        self.object.imodat = self.modatfile
        self.object.idone = self.done
        self.object.idir = self.directory
        self.object.i = self.wrap


def UseIRAFTools(objclass):
    """Class wrapper which allows classes to use IRAF tools."""
    assert issubclass(objclass,BaseObject)
    class _IRAFClass(objclass):
        """An object which contains the IRAF Tools"""
        def __new__(cls,*args,**kwargs):
            obj = objclass(*args,**kwargs)
            obj.iraf = IrafTools(obj)
            obj.iraf.set_instance_methods()
            return obj
    return _IRAFClass