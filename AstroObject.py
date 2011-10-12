# 
#  AstroObject.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-12.
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
import pyfits
import math, copy, sys, time, logging, os
from Utilities import *

LOG = logging.getLogger(__name__)

class FITSFrame(object):
    """A single frame of a FITS image"""
    def __init__(self, label, header=None, metadata=None):
        super(FITSFrame, self).__init__()
        self.label = label # A label for this frame, for selection in parent object
        self.header = header # A dictionary of header keys and values for use in 
        self.metadata = metadata # An optional metadata dictionary
        self.time = time.strftime("%Y-%m-%dT%H:%M:%S")
        
        
        if self.metadata == None:
            self.metadata = {}
        if self.header == None:
            self.header = {}
        
class FITSObject(object):
    """Holds on to a regular numpy-formated feature list image."""
    def __init__(self,dimensions=2,filename=None):
        super(FITSObject, self).__init__()
        # Image data variables.
        self.dataClass = FITSFrame
        self.DIMEN = dimensions     # Total number of dimensions, i.e. x and y, or wavelength
        self.states = {}            # Storage for all of the images
        self.statename = None       # The active state name
        self.filename = filename    # The filename to use for file loading and writing
        self.plt = plt
        self.outputData = False
        self.inputData = False


    ##############################
    # Basic Image Mode Functions #
    ##############################
    def save(self,array,statename="Original"):
        """Saves the given image to this object"""
        # Error checking for provided arguments
        if statename in self.states:
            raise IndexError("Cannot Duplicate State Name: %s \nUse remove(\'%s\') to clear" % (statename,statename))
        if type(array) != np.ndarray:
            raise TypeError("Array to be saved is not a numpy array \nCheck that you are saving a numpy image array \nType: %s" % type(array))

        # Save the actual state
        self.states[statename] = self.dataClass(array,statename)
        # Activate the saved state as the current state
        self.select(statename)
        LOG.debug("Saved frame with label %s" % statename)

    def data(self,statename=None):
        """Returns the numpy image for this object"""
        # Load the current stat if no state provided
        if not statename:
            statename = self.statename
        if statename != None and statename in self.states:
            return self.states[statename]()
        else:
            raise KeyError("Image not instantiated with any data...")

    def object(self,statename=None):
        """Returns the FITSFrame Specfied"""
        if not statename:
            statename = self.statename
        if statename != None and statename in self.states:
            return self.states[statename]
        else:
            raise KeyError("Image not instantiated with any data...")

    def select(self,statename):
        """Sets the default image to the given name"""
        if statename not in self.states:
            raise IndexError("Image %s does not exist!" % statename)
        self.statename = statename
        LOG.debug("Selected state %s" % statename)
        return

    def list(self):
        """Provides a list of the available images"""
        return self.states.keys()

    def remove(self,statename):
        """Removes the specified image from the object"""
        if image not in self.states:
            raise IndexError("Image %s does not exist!" % statename)
        LOG.debug("Removing image with label %s" % (statename))
        self.states.pop(statename)
