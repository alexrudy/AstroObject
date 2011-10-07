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
from gaussfit import *
from progressbar import ProgressBar
import math, copy

class Image(object):
    """Holds on to a regular numpy-formated feature list image."""
    def __init__(self,dimensions=3,sparsity=2,array=None,filename=None):
        super(Image, self).__init__()
        # Image data variables.
        self.DIMEN = dimensions     # Total number of dimensions, i.e. x,y and value
        self.SPARSITY = sparsity    # Number of dimensions in an image array, i.e x,y
        self.FORMAT = ["NP","MP","AR"]   # Image formats, supported types are MP for matplotlib image, and NP for numpy feature list
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
    def save(self,array,statename="Original",side=None,format=None):
        """Saves the given image to this object"""
        # Error checking for provided arguments
        if statename in self.states:
            raise IndexError("Cannot Duplicate State Name: %s \nUse remove(\'%s\') to clear" % (statename,statename))
        if type(array) != np.ndarray:
            raise TypeError("Array to be saved is not a numpy array \nCheck that you are saving a numpy array of features \nType: %s" % type(array))
        if side != None and type(side) != tuple:
            raise TypeError("Side must be a tuple. Side: %s" % side)        
        
        # Set the format and size
        self.format[statename] = format
        self.sizes[statename] = array.size
        
        # Set the side length
        if side:
            self.sides[statename] = side
        elif format=="AR":
            self.sides[statename] = tuple([self.sizes[statename] ** (1.0/float(self.SPARSITY))]*self.SPARSITY)
            warning = "[WARN] No default size provided, assuming square image with shape ("
            for aside in self.sides[statename]:
                warning += "%5.3f " % aside
            warning += ")"
            print warning
        elif format=="MP":    
            self.sides[statename] = array.shape
        elif format=="NP":
            self.sides[statename] = tuple([array[:,i].max() for i in range(array.ndim-1)])
        
        # Save the actual state
        self.states[statename] = array
        # Activate the saved state as the current state
        self.statename = statename
    
    def load(self,statename=None):
        """Returns the numpy image for this object"""
        # Load the current stat if no state provided
        if not statename:
            statename = self.statename
        if statename != None and statename in self.states:
            return self.states[statename]
        else:
            raise KeyError("Image not instantiated with any data...")
    
    def set(self,image):
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
    
    def requireFormat(self,format):
        """Requires the given format, throws an error if the current state is not in the appropriate format."""
        if self.format[self.statename] != format:
            raise TypeError("Current Image is not in %s format.\n Current format: %s" % (format,self.format[self.statename]))
        return
    
    
    ########################
    # Conversion Functions #
    ########################
    def nptoar(self,statename="ARImage"):
        """Converts a numpy image to an array of image values"""
        self.requireFormat("NP")
        self.save(self.states[self.statename][:,self.states[self.statename].ndim],statename,side=self.sides[self.statename],format="AR")
    
    def mptoar(self,statename="ARImage"):
        """Converts an mpimage into an array of image values"""
        self.requireFormat("MP")
        self.save(self.states[self.statename].flatten(),statename,side=self.sides[self.statename],format="AR")
    
    def artomp(self,statename="MPImage"):
        """Converts an array image to an MP image"""
        self.requireFormat("AR")
        self.save(self.states[self.statename].reshape(self.sides[self.statename]),statename,format="MP")
    
    def artonp(self,statename="NPImage"):
        """Converts an array image to an NP image"""
        self.requireFormat("AR")
        xind,yind = np.indices(self.sides[self.statename])
        image = np.vstack((xind.flatten(),yind.flatten(),self.load())).T
        self.save(image,statename,self.sides[self.statename],format="NP")
        
    
    def nptomp(self,statename="MPImage",side=None):
        """Returns a matplotlib image format for this image."""
        self.requireFormat("NP")
        #Image Data
        image = self.states[self.statename]
        if not(side):
            side = self.sides[self.statename]
        mpimage = image[:,2].reshape(side)
        self.save(mpimage,statename,format="MP")
        
    
    def mptonp(self,statename="NPImage"):
        """Saves the current mpimage back to the numpy format"""
        self.requireFormat("MP")
        side = self.sides[self.statename]
        values = np.asarray(self.states[self.statename].flatten(),dtype=np.float32)
        xind,yind = np.indices(self.sides[self.statename])
        image = np.vstack((xind.flatten(),yind.flatten(),values)).T
        self.save(image,statename,side,format="NP")
        
    
    #####################
    # Loading Functions #
    #####################
    def loadFromFile(self,filename=None):
        """docstring for loadFromFile"""
        if not filename:
            filename = self.filename
        self.save(mpimage.imread(filename),format="MP")
    
    
    ##########################
    # Manipulating Functions #
    ##########################
    def mask(self,left,top,right=None,bottom=None):
        """Masks the image by the distances provided"""
        self.requireFormat("MP")
        if not right:
            right = left
        if not bottom:
            bottom = top
        shape  = self.states[self.statename].shape
        masked = self.states[self.statename][left:shape[0]-right,top:shape[1]-bottom]
        self.save(masked,"Masked",format="MP")
    
    def crop(self,x,y,xsize,ysize=None):
        """Crops the provided image to twice the specified size, centered around the x and y coordinates provided."""
        self.requireFormat("MP")
        if not ysize:
            ysize = xsize
        cropped = self.states[self.statename][x-xsize:x+xsize,y-ysize:y+ysize]
        self.save(cropped,"Cropped",format="MP")
    
    
    ######################
    # Plotting Functions #
    ######################
    def show(self):
        """Shows the image"""
        self.requireFormat("MP")
        plt.imshow(self.states[self.statename],interpolation="nearest")
        plt.colorbar()
    
    def show3D(self):
        """Shows a 3D contour of the image"""
        self.requireFormat("MP")
        X = np.arange(self.states[self.statename].shape[0])
        Y = np.arange(self.states[self.statename].shape[1])
        X,Y = np.meshgrid(X,Y)
        Z = self.states[self.statename]
        ax = plt.gca(projection='3d')
        surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.jet,linewidth=0, antialiased=False)
        plt.colorbar(surf, shrink=0.5, aspect=5)
    




                