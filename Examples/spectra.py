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
from AstroObject.AstroSpectra import SpectraObject

LOG = logging.getLogger('AstroObject')
LOG.configure()
LOG.start()

WAVELENGTHS = ((np.arange(98)+1)/2.0 + 1.0) * 1e-7
HIGH_R =WAVELENGTHS[1:]/np.diff(WAVELENGTHS)
WAVELENGTHS_LOWR = ((np.arange(23)+0.25)*2.0 + 1.0) * 1e-7
LOWR = WAVELENGTHS_LOWR[1:]/np.diff(WAVELENGTHS_LOWR)/2
VALID = np.array([(np.arange(50) + 1.0) * 1e-7, np.sin(np.arange(50)/2.0)+2.0 + np.arange(50)/25.0])

OBJECT = SpectraObject()

OBJECT["Raw Data"] = VALID
OBJECT.show()
OBJECT["Interpolated"] = InterpolatedSpectrum(VALID,label="Interpolated")
OBJECT.show()
OBJECT["Post Interpolation"] = OBJECT.frame()(wavelengths=WAVELENGTHS)
OBJECT.show()
OBJECT["Resampled"] = OBJECT.frame("Interpolated")(wavelengths=WAVELENGTHS_LOWR[1:],resolution=LOWR,method='resample')
OBJECT.show()
plt.legend()
plt.figure(2)
OBJECT["Integrated"] = OBJECT.frame("Interpolated")(wavelengths=WAVELENGTHS[1:],resolution=HIGH_R,method='integrate')
OBJECT.show()
OBJECT["Integrated Quad"] = OBJECT.frame("Interpolated")(wavelengths=WAVELENGTHS[1:],resolution=HIGH_R,method='integrate_quad')
OBJECT.show()
OBJECT["R and Integrated"] = OBJECT.frame("Interpolated")(wavelengths=WAVELENGTHS[1:],resolution=HIGH_R,method='resolve_and_integrate')
OBJECT.show()
OBJECT["Integrated LR"] = OBJECT.frame("Interpolated")(wavelengths=WAVELENGTHS_LOWR[1:],resolution=LOWR,method='integrate')
OBJECT.show()
OBJECT["Integrated Quad LR"] = OBJECT.frame("Interpolated")(wavelengths=WAVELENGTHS_LOWR[1:],resolution=LOWR,method='integrate_quad')
OBJECT.show()
OBJECT["R and Integrated LR"] = OBJECT.frame("Interpolated")(wavelengths=WAVELENGTHS_LOWR[1:],resolution=LOWR,method='resolve_and_integrate')
OBJECT.show()

plt.legend()
plt.show()
