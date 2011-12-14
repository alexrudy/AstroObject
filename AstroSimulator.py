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

__all__ = ["Simulator"]

class Stage(object):
    """docstring for Stage"""
    def __init__(self,stage):
        super(Stage, self).__init__()
        self.do = stage

class Simulator(object):
    """A Simulator, used for running large segements of code with detailed logging and progress checking"""
    
    name = "Simulator"
    
    config = {
        "Logging" : {
          "Console" : {
              "Enable" : True,
              "Message" : "...%(message)s",
              "Level" : None,
          },
          "File" : {
              "Enable" : True,
              "Message" : "...%(message)s",
              "Level" : None,
              "FileName" : "Astro-Object-Simulator"
          },
        },
    }
    
    def __init__(self):
        super(Simulator, self).__init__()
        self.stages = {}
        self.orders = {}
    
    def register(self,stage,name=None,description=None,position=None):
        """Adds a stage object to this simulator"""
        if position != None:
            position = len(self.stages)
        if name == None:
            raise ValueError("Stage must have a name")
        
        stageObject = Stage(stage)
        stageObject.name = name
        stageObject.description = description
        self.stages[position] = stageObject
        
    def configure(self,filename="config.yaml"):
        """A master configuration function"""
        
        
        
        