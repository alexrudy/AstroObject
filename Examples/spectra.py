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
from AstroObject.util.functions import get_resolution_spectrum

LOG = logging.getLogger('AstroObject')
LOG.configure_from_file('Examples/config.yml')
LOG.start()

WAVELENGTHS = ((np.arange(98)+1)/2.0 + 1.0) * 1e-7
HIGH_R =WAVELENGTHS[1:]/np.diff(WAVELENGTHS)
WAVELENGTHS_LOWR = ((np.arange(23)+0.25)*2.0 + 1.0) * 1e-7
LOWR = WAVELENGTHS_LOWR[1:]/np.diff(WAVELENGTHS_LOWR)/2
VALID = np.array([(np.arange(50) + 1.0) * 1e-7, np.sin(np.arange(50)/2.0)+2.0 + np.arange(50)/25.0])

OBJECT = SpectraStack()

OBJECT.read("Examples/SNIa.R1000.dat")
OBJECT["Interpolateable"] = InterpolatedSpectrum(OBJECT.d,"Interpolateable")
wl, rs = get_resolution_spectrum(np.min(OBJECT.f.wavelengths),np.max(OBJECT.f.wavelengths),200)
OBJECT["Raw Data"] = OBJECT.f(wavelengths = wl, resolution = rs, method = 'resample')
OBJECT.show()
wl, rs = get_resolution_spectrum(np.min(OBJECT.f.wavelengths),np.max(OBJECT.f.wavelengths),50)
OBJECT["Low Res Data"] = OBJECT["Interpolateable"](wavelengths = wl, resolution = rs, method = 'resample')
OBJECT.show()
for line in OBJECT.info():
    print line
print "Valid:",OBJECT.valid()
OBJECT["Raw Data"].logarize()
OBJECT["Logarized"] = OBJECT["Raw Data"]
for line in OBJECT.info():
    print line
print "Valid:",OBJECT.valid()
OBJECT.show()
OBJECT["Raw Data"].linearize()
OBJECT["Linearized"] = OBJECT["Raw Data"]
for line in OBJECT.info():
    print line
print "Valid:",OBJECT.valid()
OBJECT.show()
try:
    for line in OBJECT.info():
        print line
    print "Valid:",OBJECT.valid()
    print "Is Log:",OBJECT.f.x_is_log()
    print "Is Linear:",OBJECT.f.x_is_linear()
    print "dx, dlogx:",np.mean(OBJECT.f.dx()),np.mean(OBJECT.f.dlogx())
    OBJECT["Raw Data"].logarize(strict=True)
    OBJECT["Logarized Strict"] = OBJECT["Raw Data"]
    OBJECT.show()
except Exception, e:
    print e
plt.legend(loc=2)
plt.title("Wavelength Scale Tests")
plt.show()
