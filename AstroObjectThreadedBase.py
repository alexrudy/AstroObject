# 
#  AstroObjectThreadedBase.py
#  AstroObject
#
#  This object is designed to be a threaded implementation of AstroObjectBase
#  As the overhead is more significant, it should only be used in instances where threading is required.
#  
#  Created by Alexander Rudy on 2011-11-24.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.2.2
# 

import math, copy, sys, time, logging, os, argparse

from multiprocessing import Process, Manager

import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt

# Submodules from this system
from Utilities import *

import AstroObjectBase

class ThreadObject(AstroObjectBase.FITSObject):
    """A threaded implementation of FITSObject"""
    def __init__(self):
        super(ThreadObject, self).__init__()
        self.Manager = Manager()
        self.states = self.Manager.dict()
        self.do_select = False #disable state-selection on action
        