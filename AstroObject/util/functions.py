# -*- coding: utf-8 -*-
# 
#  functions.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-05-08.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 

import numpy as np
import scipy as sp
import scipy.constants as spconst

def BlackBody(wl,T):
    """Return black-body flux as a function of wavelength. Usese constants from Scipy Constants, and expects SI units"""
    h = spconst.h
    c = spconst.c
    k = spconst.k
    exponent = (h * c)/(wl * k * T)
    exponential=np.exp(exponent)
    flux = np.nan_to_num((2.0 * h * c**2.0)/(wl**5.0) * (1.0)/(exponential-1.0))
    
    return flux

def Gaussian(x,mean,stdev,height):
    """Rertun a gaussian at postion x, whith mean, stdev, and height"""
    return height*np.exp(-(x-mean)**2.0/(2.0*stdev**2.0))

