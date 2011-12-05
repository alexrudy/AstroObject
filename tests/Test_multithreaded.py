#!/usr/bin/env python
# 
#  Test_multithreaded.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-11-24.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 

import math, copy, sys, time, logging, os, argparse

sys.path.append(os.path.abspath('.'))

from AstroObject.tests.Test_AstroObjectAPI import *

from AstroObject.AstroObjectThreadedBase import *
from AstroObject.AstroObjectBase import *
from multiprocessing import Process, Pool




import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt

def new((obj,frame,count)):
    """Create a new FITSFrame object and save it..."""
    obj.save(frame(None,"Empty"),"%d" % count)
    

if __name__ == '__main__':
    Obj = ThreadObject()
    pool = Pool()
    
    i = range(10)
    
    selves = [Obj] * max(i)
    frames = [FITSFrame] * max(i)
    
    args = zip(selves,frames,i)
    
    pool.map(new,args)
    
    assert Obj.list() == "none"

