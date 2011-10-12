# 
#  AstroSpectra.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 


import AstroObject
from Utilities import *

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

LOG = logging.getLogger(__name__)

class SpectraObject(AstroObject.FITSObject):
    """A subclass of FITS image with specific facilites for displaying spectra"""
    def __init__(self, dimensions=None, filename=None):
        super(SpectraObject, self).__init__()
        self.dataClass = SpectraFrame
        
        
        
    def showSpectrum(self):
        """Shows a 2-D plot of a spectrum"""
        x,y = self.data() #Slice Data
        axis = get_padding((x,y))
        plt.plot(x,y,'k-')
        plt.axis(axis)
        plt.gca().ticklabel_format(style="sci",scilimits=(3,3))
        


class SpectraFrame(AstroObject.FITSFrame):
    """docstring for SpectraFrame"""
    def __init__(self, array, label, header=None, metadata=None):
        super(SpectraFrame, self).__init__(label, header, metadata)
        if array != None:
            self.data = array # The image data
            self.size = array.size # The size of this image
            self.shape = array.shape # The shape of this image
        
    def validate(self):
        """Validates this spectra as a valid spectrum, not an image object"""
        return True
        
    def __call__(self):
        """Returns the spectrum's data"""
        return self.data

            