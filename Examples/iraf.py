#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
#  iraftools.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-04-19.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 

from AstroObject.loggers import *
from AstroObject.image import ImageStack
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
Data.iraf.directory("Caches/")

image = np.zeros((1000,1000))
image[450:550,450:550] = np.ones((100,100))
image[490:510,490:510] = np.ones((20,20)) * 0.5
flat = np.ones((1000,1000))
flat[490:510,490:510] = np.ones((20,20)) * 0.5

Data["Basic"] = image
Data["Other"] = image
Data["Flat"] = flat
Data["Final"] = image / (flat / np.max(flat))

iraf.ccdproc(
    Data.imodat("Basic","Other",append = "_flat"), 
    ccdtype = "", fixpix = False, overscan = False, trim = False,
    zerocor = False, darkcor = False, flatcor = True, 
    flat = Data.imod("Flat",append="_flat"))
Data.idone()

Data.show("Basic")
plt.figure()
Data.show("Flat")
plt.figure()
Data.show("Basic_flat")
plt.figure()
Data.show("Other_flat")
plt.figure()
Data.show("Flat_flat")
plt.figure()
Data.show("Final")
print "Showing data..."
plt.show()
