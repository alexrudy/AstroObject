# -*- coding: utf-8 -*-
# 
#  iraftools.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-04-19.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.5.3-p1
# 
u"""
:mod:`iraftools` – IRAF integration facility
============================================

This module provides an interface for using :mod:`AstroObject` with PyIRAF. For documentation of the individual methods provided by this module, see :class:`IRAFToolsMixin`. The next two sections will provide a brief overview of the use of :mod:`iraftools`.

To use :mod:`iraftools`, use the :func:`UseIRAFTools` function.

.. autofunction::
    AstroObject.iraftools.UseIRAFTools

.. _IRAFTools_Filetypes:

File types in :mod:`iraftools`
------------------------------

There are three types of FITS files provided by :mod:`iraftools`:

.. describe:: in-file
    
    :meth:`inpfile <IRAFToolsMixin.iraf.inpfile>` and :meth:`inpatfile <IRAFToolsMixin.iraf.inpatlist>`
    
    ``in`` files are FITS files which are used as input to an ``iraf`` fucntion. They are created immediately, and will exist untill the :mod:`~AstroObject.iraftools` cleanup stage (:meth:`iraf.done <AstroObject.iraftools.IRAFTools.done>`).

.. describe:: out-file
    
    :meth:`outfile <IRAFToolsMixin.iraf.outfile>` and :meth:`outatfile <IRAFToolsMixin.iraf.outatlist>`
    
    ``out`` files are FITS files which will be output targets for ``iraf``. As such, the filename returned does not point to an existing FITS file. Instead, the filename points to a potential file which will be re-read by the parent **stack** during the cleanup stage (:meth:`iraf.done <AstroObject.iraftools.IRAFTools.done>`).

.. describe:: mod-file
    
    :meth:`modfile <IRAFToolsMixin.iraf.modfile>` and :meth:`modatfile <IRAFToolsMixin.iraf.modatlist>`
    
    ``mod`` files are FITS files which will be modified in-place by ``iraf``. These files are created immediately, just like ``in`` files, and are re-loaded automatically during the cleanup stage (:meth:`iraf.done <AstroObject.iraftools.IRAFTools.done>`). To prevent these **frames** from overwriting their original content, use the ``append=`` keyword to append a string to the new **frame** name. You could also make a copy of the original **frame** using
    ::
	
    	Data["newname"] = Data["oldname"]
	
    Since **frame** labels are required to be unique, this will copy the old **frame**.

These file types can be generated individually, or as @lists using functions provided by :class:`IRAFToolsMixin`.

Example use of :mod:`iraftools`
-------------------------------

The best way to understand how :mod:`iraftools` works is to check out the walkthrough example. The example goes a few of the commonly used :mod:`iraftools` methods, and explains their basic operation. The example is explained in detail in :ref:`IRAFToolsWalkthough`.

.. literalinclude:: /../../Examples/iraf-simple.py

A full examle program can be seen in :ref:`IRAFToolsExample`.

:class:`IRAFToolsMixin` – Intefrace to :class:`IRAFTools`
---------------------------------------------------------

.. autoclass::
    AstroObject.iraftools.IRAFToolsMixin
    
    .. method:: iraf.inpfile(framename=None,extension='.fits')
        
        Returns a filename for a ``fits`` file from the given framename which can be used as input for IRAF tasks. This method should be used for files which will not be modified, as modifications will not be captured by the system. For files which are input, but will be modified, use :meth:`imod`.
        
        :param framename: The name of the **frame** to use for input.
        :param extension: The file extension to use.
        :returns: Filename for use with PyRAF
    
    .. method:: iraf.outfile(framename=None,extension='.fits',append=None)
        
        Returns a filename for a ``fits`` file from the given framename which can be used for output for IRAF tasks. The file is not created, but will be read back into this **stack** when :meth:`idone` is called.
        
        :param framename: The name of the **frame** to use for output.
        :param extension: The file extension to use.
        :param append: A string to append to the frame names
        :returns: Filename for use with PyRAF
    
    .. method:: iraf.modfile(framename=None,newframename=None,extension='.fits',append=None)
    
        Returns a filename for a ``fits`` file from the given framename which can be used as input for IRAF tasks which modify a file in-place. The file will be reloaded when :meth:`idone` is called.
        
        :param framename: The name of the **frame** to use for input.
        :param newframename: The name of the **frame** to use fo the output. If ``None``, uses ``framename``
        :param extension: The file extension to use.
        :param append: A string to be appended tp the new frame name.
        :returns: Filename for use with PyRAF
        
    .. method:: iraf.inpatlist(*framenames,extension='.fits')
    
        Returns a filename for an "@"-list. The "@"-list lists fits files for each frame provided. These fitsfiles are created automatically. The "@"-list should not be used for in-place modification, for that, use :meth:`imodat`.
        
        :param framenames: Names of frames to be included in the "@"-list.
        :param extension: The file extension to use.
        :retunrs: Filename of the "@"-list
        
    .. method:: iraf.outatlist(*framenames,append=None,extension='.fits')
        
        Returns a filename for an "@"-list. The "@"-list lists fits files for each frame provided. These fits-files will be output destinations. They will be re-read into the object when :meth:`idone` is called.
        
        :param framenames: Names of frames to be included in the "@"-list.
        :param extension: The file extension to use.
        :param append: A string to append to the frame names
        :retunrs: Filename of the "@"-list
        
    .. method:: iraf.modatlist(*framenames,append=None,extension='.fits')
        
        Returns a filename for an "@"-list. The "@"-list lists fits files for each frame provided. These fits-files will be in-place modification destinations. They will be re-read into the object when :meth:`idone` is called.
        
        :param framenames: Names of frames to be included in the "@"-list.
        :param extension: The file extension to use.
        :param append: A string to append to the frame names
        :retunrs: Filename of the "@"-list
        
    .. method:: iraf.done()
    
        Cleans up the temporary files, reloading any files which need reloading. Should be called after the IRAF command has completed, before attempting to re-use the stage.

.. _IRAFTools_Shortcuts:

Shortcuts for :class:`IRAFToolsMixin`
-------------------------------------

The following shortcuts are bound directly to the **stack** object by the :meth:`IRAFToolsMixin.set_instance_methods`

- :meth:`iraf.infile <IRAFToolsMixin.iraf.infile>` = :meth:`iin`
- :meth:`iraf.outfile <IRAFToolsMixin.iraf.outfile>` = :meth:`iout`
- :meth:`iraf.modfile <IRAFToolsMixin.iraf.modfile>` = :meth:`imod`
- :meth:`iraf.inatfile <IRAFToolsMixin.iraf.inatfile>` = :meth:`iinat`
- :meth:`iraf.outatfile <IRAFToolsMixin.iraf.outatfile>` = :meth:`ioutat`
- :meth:`iraf.modatfile <IRAFToolsMixin.iraf.modatfile>` = :meth:`imodat`

:class:`IRAFTools` – API Implementation of IRAF Tools
-----------------------------------------------------

.. autoclass::
    AstroObject.iraftools.IRAFTools
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
from .util import getVersion
from .file.fileset import TempFileSet
from .AstroObjectBase import BaseStack, Mixin, BaseFrame, NoHDUMixin, NoDataMixin
from .AstroFITS import FITSFrame

__version__ = getVersion()

LOG = logging.getLogger(__name__)

IRAFSet = None
__module__ = sys.modules[__name__]

class IRAFFrame(NoHDUMixin, NoDataMixin, BaseFrame):
    """This frame is meant to hold the place of a data frame for later use. It quite literally can't do anythign, and should never be around for long."""
    pass
        


class IRAFTools(object):
    """A class for managing interaction with IRAF"""
    def __init__(self,Object):
        super(IRAFTools, self).__init__()
        if not isinstance(Object,BaseStack):
            raise ValueError("Object must be an instance of %r" % BaseStack.__name__)
        self.object = Object
        self.module = __module__
        self.FileSet = self.module.TempFileSet
        self._directory = None
        self._collect = {}
        if IRAFFrame not in self.object.data_classes:
            self.object.add_data_class(IRAFFrame)
    
    def __del__(self):
        """Remove the reference to object, to prevent circularity"""
        del self.object
        del self.module
        del self.FileSet
    
    @property
    def active(self):
        """If the set is active for this group of iraftools"""
        return self.module.IRAFSet is not None
        
    @property
    def set(self):
        """Unique new set stored at the module level."""
        if self.module.IRAFSet is None or (not self.module.IRAFSet.open):
            self.module.IRAFSet = self.FileSet(base=self._directory)
        return self.module.IRAFSet
    
    def wrap(self,func):
        """Wrap the function below this with the done protocol"""
        def newfunc(*args,**kwargs):
             rvalue = func(*args,**kwargs)
             self.done()
             return rvalue
        newfunc = make_decorator(func)(newfunc)
        return newfunc
    
    def directory(self,directory=None):
        """Set the IRAFSet directory for this object."""
        if directory is None:
            self._directory = None
            return
        if not os.path.exists(directory):
            os.mkdir(directory)
        if os.path.basename(directory) != "":
            directory = os.path.join(directory,"")    
        self._directory = os.path.relpath(directory)
        
    def inpfile(self,framename=None,extension='.fits',**kwargs):
        """Returns a filename for a ``fits`` file from the given framename which can be used as input for IRAF tasks. This method should be used for files which will not be modified, as modifications will not be captured by the system. For files which are input, but will be modified, use :meth:`modfile`.
        
        :param framename: The name of the **frame** to use for input.
        :param extension: The file extension to use.
        :returns: Filename for use with PyRAF
        
        """
        if framename is None:
            framename = self.object.framename
        filename = self.set.filename(extension=extension,prefix=framename)
        self.object.write(frames=[framename],filename=filename,clobber=True)
        LOG.log(2,"Created infile for frame %s named %s" % (framename,filename))
        return filename
    
    infile = inpfile
        
    def outfile(self,framename=None,append=None,extension='.fits',**kwargs):
        """
        Returns a filename for a ``fits`` file from the given framename which can be used for output for IRAF tasks. The file is not created, but will be read back into this **stack** when :meth:`done` is called.
        
        :param framename: The name of the **frame** to use for output.
        :param extension: The file extension to use.
        :param append: A string to append to the frame names
        :returns: Filename for use with PyRAF
    
        """
        if framename is None:
            framename = self.object.framename + "-iraf"
        if append is not None:
            framename += append
        if framename in self.object:
            raise KeyError("Cannot register frame \'%s\' for output, frame already exists in %s." % (framename,self.object))
        filename = self.set.filename(extension=extension,prefix=framename)
        os.unlink(filename)
        self.object.save(IRAFFrame(data=None,label=framename))
        self._collect[framename] = filename
        LOG.log(2,"Created outfile for frame %s named %s" % (framename,filename))
        return filename
        
    def modfile(self,framename,newframename=None,append=None,extension='.fits',**kwargs):
        """Returns a filename for a ``fits`` file from the given framename which can be used as input for IRAF tasks which modify a file in-place. The file will be reloaded when :meth:`done` is called.
        
        :param framename: The name of the **frame** to use for input.
        :param newframename: The name of the **frame** to use fo the output. If ``None``, uses ``framename``
        :param extension: The file extension to use.
        :param append: A string to be appended tp the new frame name.
        :returns: Filename for use with PyRAF
        """
        if newframename is None:
            newframename = framename
        if append is not None:
            newframename += append
        if framename is None:
            framename = self.object.framename
        filename = self.set.filename(extension=extension,prefix=framename)
        self.object.write(frames=[framename],filename=filename,clobber=True)
        if newframename not in self.object:
            self.object.save(IRAFFrame(data=None,label=newframename))
        LOG.log(2,"Created modfile for frame %s named %s" % (framename,filename))
        self._collect[newframename] = filename
        return filename
        
    def _atfile(self,*framenames,**kwargs):
        """Generic atfile creation routine"""
        if len(framenames) < 1:
            framenames = self.object.list()
        atlist = self.set.filename(extension='.list')

        function = kwargs.pop('function',None)
        if function is None:
            raise TypeError("Must provide a filename creation function")
        
        with open(atlist,'w') as stream:
            for framename in framenames:
                filename = function(framename,**kwargs)
                stream.write("%s\n" % filename)
        LOG.log(2,"Created atlist for frames %s named %s" % (framenames,atlist))
        return "@" + atlist

    def modatlist(self,*framenames,**kwargs):
        """File list for modification"""
        kwargs.pop("function",None)
        return self._atfile(*framenames,function=self.modfile,**kwargs)
    
    modatfile = modatlist
    
    def inpatlist(self,*framenames,**kwargs):
        """Return a filename with @ appended, for a file which lists a series of fitsfiles."""
        kwargs.pop("function",None)
        return self._atfile(*framenames,function=self.infile,**kwargs)
    
    inatfile = inpatlist
    
    def outatlist(self,*framenames,**kwargs):
        """Return a filename with @ appended, for a file which lists a series of fitsfiles"""
        kwargs.pop("function",None)
        return self._atfile(*framenames,function=self.outfile,**kwargs)
        
    outatfile = outatlist
        
    def done(self):
        """Finish the IRAF framename."""
        if not self.active:
            return
        for framename,filename in self._collect.iteritems():
            frames = self.object.read(filename=filename,framename=framename,clobber=True)
            self.set.updated(filename)
            LOG.log(2,"Collected file for frame %s named %s" % (framename,filename))
            LOG.log(2,"States created: %s" % frames)
        self._collect = {}
        if self.set.modified:
            LOG.warning("Files remain modified by IRAF: %r" % self.set.modified)
        self.set.close(check=False)

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

class IRAFToolsMixin(Mixin):
    """This mixin class enables IRAFTools. By default, tools are only enabled in the ``class.iraf`` namespace, so to call :meth:`~iraf.infile`, use :meth:`iraf.infile <IRAFToolsMixin.iraf.infile>`. To use the IRAFTools shortcuts (documented in :ref:`IRAFTools_Shortcuts`), pass ``shortcuts=True`` to any constructor form for each object, or explicitly call :meth:`iraf.set_instance_methods`."""
    def __init__(self, *args, **kwargs):
        shortcuts = kwargs.pop('shortcuts',False)
        super(IRAFToolsMixin, self).__init__(*args,**kwargs)
        self.iraf = IRAFTools(self)
        if shortcuts:
            self.iraf.set_instance_methods()
    
    def __new__(cls,*args,**kwargs):
        obj = cls.__new__(*args,**kwargs)
        if not hasattr(obj,'iraf'):
            obj.iraf = IRAFTools(obj)
            if kwargs.pop('shortcuts',False):
                obj.iraf.set_instance_methods()
        return obj
        
    def __array_finalize__(self,obj):
        """NDArray Finalization function"""
        super(IRAFToolsMixin, self).__array_finalize__(obj)
        self.iraf = IRAFTools(self)
            
        

def UseIRAFTools(klass):
    """Class wrapper which allows classes to use IRAF tools. Takes a single parameter, the class name which should have IRAF tools, and creates a dummy class which activates IRAF tools during initialization.
    
    :param klass: The class to apply :mod:`iraftools` to.
    
    Example::
        
        from AstroObject.iraftools import UseIRAFTools
        from AstroObject.AstroImage import ImageStack
        ImageStack = UseIRAFTools(ImageStack)
        
    """
    assert issubclass(klass,BaseStack)
    class _IRAFClass(klass):
        """An object which contains the IRAF Tools"""
        def __new__(cls,*args,**kwargs):
            obj = klass(*args,**kwargs)
            obj.iraf = IRAFTools(obj)
            obj.iraf.set_instance_methods()
            return obj
    return _IRAFClass
