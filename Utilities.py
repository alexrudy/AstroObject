# 
#  Utilities.py
#  Astronomy ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.2.4
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

def disable_Console():
    """Disables console Logging"""
    logging.getLogger('').removeHandler(console)

def enable_Console():
    """docstring for enable_Console"""
    logging.getLogger('').addHandler(console)
    

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
    


def expandLim(axis,scale=0.05):
    """Expands Axis Limits by *scale*"""
    xmin,xmax,ymin,ymax = axis
    xran = abs(xmax-xmin)
    yran = abs(ymax-ymin)

    xmax += xran*scale
    xmin -= xran*scale
    ymax += yran*scale
    ymin -= yran*scale

    axis = (xmin,xmax,ymin,ymax)
    return axis

def BlackBody(wl,T):
    """Return black-body flux as a function of wavelength"""
    h = spconst.h
    c = spconst.c
    k = spconst.k
    exponent = (h * c)/(wl * k * T)
    exponential=np.exp(exponent)
    flux = np.nan_to_num((2.0 * h * c**2.0)/(wl**5.0) * (1.0)/(exponential-1.0))
    
    return flux


def Gaussian(x,mean,stdev,height):
    """Rertun a gaussian at postion x"""
    return height*np.exp(-(x-mean)**2.0/(2.0*stdev**2.0))

def validate_filename(string,extension=".fits"):
    """Validates a string as an acceptable filename, stripping path components,etc."""
    if string[-len(extension):] == extension:
        string = string[:-len(extension)]
    return string+extension
    

def rangemsg(array,name):
    """Message describing this array"""
    MSG = "Array named %(name)-10s has %(elements)8d els with shape %(shape)11s. Range %(range)10s. Zeros %(zeros)d (%(zper)3d%%). NaNs %(nans)d (%(nper)3d%%). Type %(type)3s"
    fmtr = {}
    fmtr["elements"] = array.size
    fmtr["shape"] = str(array.shape)
    fmtr["name"] = name
    fmtr["min"] = np.min(array)
    fmtr["max"] = np.max(array)
    fmtr["zeros"] = np.sum(array == np.zeros(array.shape))
    fmtr["zper"] = float(fmtr["zeros"]) / float(fmtr["elements"]) * 100
    fmtr["nans"] = np.sum(np.isnan(array))
    fmtr["nper"] = float(fmtr["nans"]) / float(fmtr["elements"]) * 100
    fmtr["type"] = array.dtype
    fmtr["range"] = "[%(min)5.5g,%(max)5.5g]" % fmtr
    return MSG % fmtr

class AbstractError(Exception):
    """An error which arose due to bad abstraction implemetnation"""
    pass

class HDUFrameTypeError(Exception):
    """docstring for HDUFrameTypeError"""
    pass
        
