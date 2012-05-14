# -*- coding: utf-8 -*-
# 
#  AstroImage.py
#  Astronomy ObjectModel
#  
#  Created by Alexander Rudy on 2011-04-28.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.5.2
# 
"""
:mod:`AstroImage` — Image Stacks and Storage 
============================================

**Stacks** and **frames** for manipulating and managing images. Images are simply defined as a two-dimensional numpy array. Image **stacks** have two special methods, :meth:`ImageStack.loadFromFile` and :meth:`ImageStack.show3D`.

To understand IRAF integration of this module, see the methods provided by :mod:`~.iraftools`, including :func:`~.iraftools.UseIRAFTools`.

.. inheritance-diagram::
    AstroObject.AstroImage.ImageStack
    AstroObject.AstroImage.ImageFrame
    :parts: 1

:class:`ImageStack` — Image **stacks**
--------------------------------------

.. autoclass::
    AstroObject.AstroImage.ImageStack
    :members:
    :inherited-members:

:class:`ImageFrame` — Image **frames**
--------------------------------------

.. autoclass::
    AstroObject.AstroImage.ImageFrame
    :members:
    :special-members:

"""
# Parent Modules
from .AstroObjectBase import HDUHeaderMixin, BaseFrame, BaseStack

# Standard Scipy Toolkits
import numpy as np
import pyfits as pf
import scipy as sp

# Python Modules
import os

# Module Utilites
from .util import getVersion, npArrayInfo
from . import AstroObjectLogging as logging

__all__ = [ "ImageFrame", "ImageStack" ]

__version__ = getVersion()

LOG = logging.getLogger(__name__)

class ImageFrame(HDUHeaderMixin,BaseFrame):
    """
    A single frame of a FITS image.
    Frames are known as Header Data Units, or HDUs when written to a FITS file.
    This frame accepts (generally) 2-dimensional numpy arrays (``ndarray``), and will show those arrays as images. Currently, the system makes no attempt to ensure/check the data type of your data arrays. As such, data saved will often be saved as ``np.float`` rather than more compact data types such as ``np.int16``. Pyfits handles the typing of your data automatically, so saving an array with the correct type will generate the proper FITS file.
    This object requires *array*, the data, a *label*, and can optionally take *headers* and *metadata*.
    
    """
    def __init__(self, data=None, label=None, header=None, metadata=None, **kwargs):
        self.data = data # The image data
        self.size = data.size # The size of this image
        self.shape = data.shape # The shape of this image
        super(ImageFrame, self).__init__(data=None, label=label, header=header, metadata=metadata, **kwargs)
        
    
    def __call__(self):
        """Returns the data for this frame, which should be a ``numpy.ndarray``."""
        return self.data
        
    def __valid__(self):
        """Runs a series of assertions which ensure that the data for this frame is valid"""
        assert isinstance(self.data,np.ndarray), "Frame data is not correct type: %s" % type(self.data)
        if len(self.data.shape) != 2:
            LOG.warning("The data appears to be %d dimensional. This object expects 2 dimensional data." % len(self.data.shape))
        return super(ImageFrame, self).__valid__()
        
    
    def __hdu__(self,primary=False):
        """Retruns an HDU which represents this frame. HDUs are either ``pyfits.PrimaryHDU`` or ``pyfits.ImageHDU`` depending on the *primary* keyword."""
        if primary:
            LOG.log(5,"Generating a primary HDU for %s" % self)
            HDU = pf.PrimaryHDU(self())
        else:
            LOG.log(5,"Generating an image HDU for %s" % self)
            HDU = pf.ImageHDU(self())
        return HDU
    
    def __show__(self):
        """Plots the image in this frame using matplotlib's ``imshow`` function. The color map is set to an inverted binary, as is often useful when looking at astronomical images. The figure object is returned, and can be manipulated further.
        
        .. Note::
            This function serves as a quick view of the current state of the frame. It is not intended for robust plotting support, as that can be easily accomplished using ``matplotlib``. Rather, it attempts to do the minimum possible to create an acceptable image for immediate inspection.
        """
        LOG.log(2,"Plotting %s using matplotlib.pyplot.imshow" % self)
        import matplotlib as mpl
        import matplotlib.pyplot as plt
        figure = plt.imshow(self(),interpolation="nearest")
        plt.title(r'\verb-'+self.label+r'-')
        figure.set_cmap('binary_r')
        plt.colorbar()
        return figure
    
    @classmethod
    def __save__(cls,data,label):
        """Attempts to create a :class:`ImageFrame` object from the provided data. This requres some type checking to ensure that the provided data meets the general sense of such an image. If the data does not appear to be correct, this method will raise an :exc:`NotImplementedError` with a message describing why the data did not validate. Generally, this error will be intercepted by the caller, and simply provides an indication that this is not the right class for a particular piece of data.
        
        If the data is saved successfully, this method will return an object of type :class:`ImageFrame`
        
        The validation requires that the data be a type ``numpy.ndarray`` and that the data have 2 and only 2 dimensions.
        """
        LOG.log(2,"Attempting to save as %s" % cls)
        if not isinstance(data,np.ndarray):
            msg = "ImageFrame cannot handle objects of type %s, must be type %s" % (type(data),np.ndarray)
            raise NotImplementedError(msg)
        try:
            Object = cls(data,label)
        except AttributeError as AE:
            msg = "%s data did not validate: %s" % (cls.__name__,AE)
            raise NotImplementedError(msg)
        LOG.log(2,"Saved %s with size %d" % (Object,data.size))
        return Object
    
    @classmethod
    def __read__(cls,HDU,label):
        """Attempts to convert a given HDU into an object of type :class:`ImageFrame`. This method is similar to the :meth:`__save__` method, but instead of taking data as input, it takes a full HDU. The use of a full HDU allows this method to check for the correct type of HDU, and to gather header information from the HDU. When reading data from a FITS file, this is the prefered method to initialize a new frame.
        """
        LOG.log(2,"Attempting to read as %s" % cls)
        if not isinstance(HDU,(pf.ImageHDU,pf.PrimaryHDU)):
            msg = "Must save a PrimaryHDU or ImageHDU to a %s, found %s" % (cls.__name__,type(HDU))
            raise NotImplementedError(msg)
        try:
            Object = cls(HDU.data,label)
        except AttributeError as AE:
            msg = "%s data did not validate: %s" % (cls.__name__,AE)
            raise NotImplementedError(msg)
        LOG.log(2,"Created %s" % Object)
        return Object
    


class ImageStack(BaseStack):
    """This object tracks a number of data frames. This class is a simple subclass of :class:`AstroObjectBase.BaseStack` and usese all of the special methods implemented in that base class. This object sets up an image object class which has two special features. First, it uses only the :class:`ImageFrame` class for data. As well, it accepts an array in the initializer that will be saved immediately.
    """
    def __init__(self, array=None,dataClasses=[ImageFrame], **kwargs):
        super(ImageStack, self).__init__(dataClasses=dataClasses,**kwargs)
        if array != None:
            raise NotImplemented("Cannot initialize with data")        # Save the initializing data
            
    def loadFromFile(self, filename=None, framename=None):
        """This function can be used to load an image file (but not a FITS file) into this image frame. Image files should be formats accepatble to the Python Image Library, but that generally applies to most common image formats, such as .png and .jpg .
        This method takes a *filename* and a *framename* parameter. If either is not given, they will be generated using sensible defaults."""
        if not filename:
            filename = self.filename
        if framename == None:
            framename = os.path.basename(filename)
            LOG.log(2,"Set framename for image from filename: %s" % framename)
        import matplotlib.image as mpimage
        self.save(mpimage.imread(filename),framename)
        LOG.log(5,"Loaded Image from file: "+filename)
    
    def show3D(self, framename=None):
        """Shows a 3D contour of the image"""
        if not framename:
            framename = self.framename
        if framename != None and framename in self:
            import matplotlib as mpl
            import matplotlib.pyplot as plt
            from matplotlib import cm            
            X = np.arange(self.data(framename).shape[0])
            Y = np.arange(self.data(framename).shape[1])
            X,Y = np.meshgrid(X,Y)
            Z = self.data(framename)
            LOG.log(2,"3D Plotting: Axis Size %s %s %s" % (X.size, Y.size, Z.size))
            ax = plt.gca(projection='3d')
            surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.jet, linewidth=0, antialiased=False)
            plt.colorbar(surf, shrink=0.5, aspect=5)
            LOG.log(2,"Plot Image in 3D: %s" % framename)
        else:
            self._key_error(framename)
    
    ##########################
    # Manipulating Functions #
    ##########################
    def mask(self, left, top, right=None, bottom=None, label=None, clobber=True):
        """Masks the image by the distances provided. This function masks the current frame. Use :meth:`select` to change which frame this method acts on. Masks cut out the edges of images by the specified width.
        
        :param float left: Size to mask off of the left of the image.
        :param float top: Size to mask off the top of the image.
        :param float right: Size to mask off the right of the image. If no size is given, will use ``left``.
        :param float bottom: Size to mask off the bottom of the image. If no size is given, will use ``right``.
        :keyword label: The label to use for saving this masked image.
        :keyword bool clobber: Whether to overwrite the named frame in this stack.
        
        """
        if not right:
            right = left
        if not bottom:
            bottom = top
        shape  = self.d.shape
        masked = self.d[left:shape[0]-right,top:shape[1]-bottom]
        if label == None:
            label = "Masked"
        LOG.log(2,"Masked masked and saved image")
        self.save(masked,label,clobber=clobber)
        
    def crop(self,x,y,xsize,ysize=None,label=None,clobber=True):
        """Crops the provided image to twice the specified size, centered around the x and y coordinates provided.
        
        :param int x: The x position of the desired center.
        :param int y: The y position of the desired center.
        :param int xsize: The size of the x direction. This results in indexing like [x-xsize:x+xsize].
        :param int ysize: The size of the y direction. If ``None``, will use ``xsize``.
        :keyword label: The label to use for saving this cropped image.
        :keyword clobber: Whether to overwrite the named frame in this stack.
        
        """
        if not ysize:
            ysize = xsize
        cropped = self.d[x-xsize:x+xsize,y-ysize:y+ysize]
        if label == None:
            label = "Cropped"
        self.save(cropped,label,clobber=clobber)

                
