# 
#  AstroSpectra.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 


import AstroImage
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

class FITSSpectra(AstroImage.FITSImage):
    """A subclass of FITS image with specific facilites for displaying spectra"""
    def __init__(self, dimensions=None, array=None, filename=None):
        super(FITSSpectra, self).__init__(dimensions, array, filename)
        
        
    def showSpectrum(self):
        """Shows a 2-D plot of a spectrum"""
        x,y = self.data() #Slice Data
        axis = get_padding((x,y))
        plt.plot(x,y,'k-')
        plt.axis(axis)
        plt.gca().ticklabel_format(style="sci",scilimits=(3,3))
        


class SpectraFrame(AstroImage.FITSFrame):
    """docstring for SpectraFrame"""
    def __init__(self, array, label, header=None, metadata=None):
        super(SpectraFrame, self).__init__(array, label, header, metadata)
        
        
    def validate(self):
        """Validates this spectra as a valid spectrum, not an image object"""
        return True
        
    

            