# 
#  AstroSimulator.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-12-14.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.3.0
# 

# Standard Scipy Toolkits
import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt

# Matplolib Extras
import matplotlib.image as mpimage
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter

# Scipy Extras
from scipy import ndimage
from scipy.spatial.distance import cdist
from scipy.linalg import norm

# Standard Python Modules
import math, copy, sys, time, logging, os

# Submodules from this system
from Utilities import *

__all__ = ["Simulator","Stage"]

class Stage(object):
    """Run a single segment of a simulator"""
    def __init__(self):
        super(Stage, self).__init__()
        
    def do(self,conf):
        """Do the logic of this stage"""
    pass

class Simulator(object):
    """A Simulator, used for running large segements of code with detailed logging and progress checking"""
    
    name = "Simulator"
    
    
    def __init__(self):
        super(Simulator, self).__init__()
        self.stages = []
    
    def register(self,stage,position=None):
        """Adds a stage object to this simulator"""
    pass