#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
#  iraftools.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-04-19.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 

from AstroObject.AstroObjectLogging import *
from AstroObject.AstroImage import ImageStack
from AstroObject.iraftools import UseIRAFTools

import numpy as np
import matplotlib.pyplot as plt
from pyraf import iraf
from pyraf.iraf import imred, ccdred

LOG = logging.getLogger('AstroObject')
LOG.configure()
LOG.start()


ImageStack = UseIRAFTools(ImageStack)

Data = ImageStack()

image = np.zeros((1000,1000))
image[450:550,450:550] = np.ones((100,100))
flat = np.ones((1000,1000))
flat [490:510,490:510] = np.ones((20,20)) * 0.5

Data["Basic"] = image
Data["Other"] = image
Data["Flat"] = flat

iraf.ccdproc(
    Data.imodat("Basic","Other",append = "_flat"), 
    ccdtype = "", fixpix = False, overscan = False, trim = False,
    zerocor = False, darkcor = False, flatcor = True, 
    flat = Data.iin("Flat"))
Data.idone()

Data.show("Basic")
plt.figure()
Data.show("Flat")
plt.figure()
Data.show("Basic_flat")
plt.figure()
Data.show("Other_flat")
print "Showing data..."
plt.show()
