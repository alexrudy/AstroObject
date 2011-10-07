# 
#  Utilities.py
#  Astronomy ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import scipy.constants as spconst
import pyfits
import math
import logging,time,sys


LOG = logging.getLogger(__name__)

def get_padding(*otherxy):
    """This function returns axis values to provide 5-percent padding around the given data."""
    
    xs = ()
    ys = ()
    
    
    if len(otherxy) == 1:
        x,y = otherxy[0]
    else:
        for xad,yad in otherxy:
            xs = tuple(xs) + tuple(xad)
            ys = tuple(ys) + tuple(yad)
    
        x = np.concatenate(xs)
        y = np.concatenate(ys)
    
    return [min(x)-(max(x)-min(x))*0.05, max(x)+(max(x)-min(x))*0.05, min(y)-(max(y)-min(y))*0.05, max(y)+(max(y)-min(y))*0.05]
    

def BlackBody(wl,T):
    """Return black-body flux as a function of wavelength"""
    h = spconst.h
    c = spconst.c
    k = spconst.k
    exponent = (h * c)/(wl * k * T)
    flux = (2.0 * h * c**2.0)/(wl**5.0) * (1.0)/(np.exp(exponent)-1.0)
    return flux

