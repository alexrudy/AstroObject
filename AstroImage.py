# 
#  image.py
#  Astronomy ObjectModel
#  
#  Created by Alexander Rudy on 2011-04-28.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 
import matplotlib.pyplot as plt
import matplotlib.image as mpimage
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
from scipy import ndimage
from scipy.spatial.distance import cdist
from scipy.linalg import norm
import numpy as np
import math, copy

class FITSImage(object):
    """Holds on to a regular numpy-formated feature list image."""
    def __init__(self,dimensions=2,array=None,filename=None):
        super(FITSImage, self).__init__()
        # Image data variables.
        self.DIMEN = dimensions     # Total number of dimensions, i.e. x and y, or wavelength
        self.states = {}            # Storage for all of the images
        self.format = {}            # Format for each image
        self.sides = {}             # Length of the sides on each image, should be of the format np.shape()
        self.sizes = {}             # The total size of the image (should be equivalent to np.prod(sides))
        self.statename = None       # The active state name
        self.filename = filename    # The filename to use for file loading
        self.plt = plt
        
        if array != None:
            self.save(array)        # Save the initializing data
    
    
    ##############################
    # Basic Image Mode Functions #
    ##############################
    def save(self,array,statename="Original",side=None):
        """Saves the given image to this object"""
        # Error checking for provided arguments
        if statename in self.states:
            raise IndexError("Cannot Duplicate State Name: %s \nUse remove(\'%s\') to clear" % (statename,statename))
        if type(array) != np.ndarray:
            raise TypeError("Array to be saved is not a numpy array \nCheck that you are saving a numpy image array \nType: %s" % type(array))
        if side != None and type(side) != tuple:
            raise TypeError("Side must be a tuple. Side: %s" % side)        
        
        # Set the format and size
        self.format[statename] = format
        self.sizes[statename] = array.size
        self.sides[statename] = array.shape
        
        # Save the actual state
        self.states[statename] = array
        # Activate the saved state as the current state
        self.statename = statename
    
    def data(self,statename=None):
        """Returns the numpy image for this object"""
        # Load the current stat if no state provided
        if not statename:
            statename = self.statename
        if statename != None and statename in self.states:
            return self.states[statename]
        else:
            raise KeyError("Image not instantiated with any data...")
    
    def select(self,image):
        """Sets the default image to the given name"""
        if image not in self.states:
            raise IndexError("Image %s does not exist!" % image)
        self.statename = image
        return
    
    def list(self):
        """Provides a list of the available images"""
        return self.states.keys()
    
    def remove(self,image):
        """Removes the specified image from the object"""
        if image not in self.states:
            raise IndexError("Image %s does not exist!" % image)
        self.states.pop(image)
        self.sizes.pop(image)
        self.format.pop(image)
        self.sides.pop(image)
    
    
    #####################
    # Loading Functions #
    #####################
    def loadFromFile(self,filename=None,statename=None):
        """docstring for loadFromFile"""
        if not filename:
            filename = self.filename
        self.save(mpimage.imread(filename),statename)
    
    
    ##########################
    # Manipulating Functions #
    ##########################
    def mask(self,left,top,right=None,bottom=None):
        """Masks the image by the distances provided"""
        if not right:
            right = left
        if not bottom:
            bottom = top
        shape  = self.states[self.statename].shape
        masked = self.states[self.statename][left:shape[0]-right,top:shape[1]-bottom]
        self.save(masked,"Masked")
    
    def crop(self,x,y,xsize,ysize=None):
        """Crops the provided image to twice the specified size, centered around the x and y coordinates provided."""
        if not ysize:
            ysize = xsize
        cropped = self.states[self.statename][x-xsize:x+xsize,y-ysize:y+ysize]
        self.save(cropped,"Cropped")
    
    
    ######################
    # Plotting Functions #
    ######################
    def show(self):
        """Shows the image"""
        plt.imshow(self.states[self.statename],interpolation="nearest")
        plt.colorbar()
    
    def show3D(self):
        """Shows a 3D contour of the image"""
        X = np.arange(self.states[self.statename].shape[0])
        Y = np.arange(self.states[self.statename].shape[1])
        X,Y = np.meshgrid(X,Y)
        Z = self.states[self.statename]
        ax = plt.gca(projection='3d')
        surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.jet,linewidth=0, antialiased=False)
        plt.colorbar(surf, shrink=0.5, aspect=5)
    




                