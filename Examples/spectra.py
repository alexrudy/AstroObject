#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
#  spectra.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-04-17.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 

import numpy as np
import matplotlib.pyplot as plt


from AstroObject.AstroObjectLogging import *
from AstroObject.AnalyticSpectra import InterpolatedSpectrum,GaussianSpectrum,FlatSpectrum,BlackBodySpectrum,UnitarySpectrum,Resolver
from AstroObject.AstroSpectra import SpectraStack
from AstroObject.util import npArrayInfo

LOG = logging.getLogger('AstroObject')
LOG.configure_from_file('Examples/config.yml')
LOG.start()

WAVELENGTHS = ((np.arange(98)+1)/2.0 + 1.0) * 1e-7
HIGH_R =WAVELENGTHS[1:]/np.diff(WAVELENGTHS)
WAVELENGTHS_LOWR = ((np.arange(23)+0.25)*2.0 + 1.0) * 1e-7
LOWR = WAVELENGTHS_LOWR[1:]/np.diff(WAVELENGTHS_LOWR)/2
VALID = np.array([(np.arange(50) + 1.0) * 1e-7, np.sin(np.arange(50)/2.0)+2.0 + np.arange(50)/25.0])

OBJECT = SpectraStack()

OBJECT["Raw Data"] = VALID
OBJECT.show()
for line in OBJECT["Raw Data"].__info__():
    print line
for line in OBJECT.info("Raw Data"):
    print line
OBJECT["Raw Data"].logarize()
OBJECT["Logarized"] = OBJECT["Raw Data"]
for line in OBJECT["Logarized"].__info__():
    print line
OBJECT.show()
OBJECT["Raw Data"].linearize()
OBJECT["Linearized"] = OBJECT["Raw Data"]
for line in OBJECT["Linearized"].__info__():
    print line
OBJECT.show()
try:
    for line in OBJECT["Raw Data"].__info__():
        print line
    OBJECT["Raw Data"].logarize(strict=True)
    OBJECT["Logarized Strict"] = OBJECT["Raw Data"]
    OBJECT.show()
except Exception, e:
    print e
plt.legend()
plt.show()
