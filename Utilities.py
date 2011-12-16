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
import logging,time,sys,collections,os


LOG = logging.getLogger(__name__)

def disable_Console():
    """Disables console Logging"""
    logging.getLogger('').removeHandler(console)

def enable_Console():
    """docstring for enable_Console"""
    logging.getLogger('').addHandler(console)
    
def getVersion(rel=__file__,filename="VERSION",getTuple=False):
    """docstring for getVersion"""
    with open(os.path.abspath(os.path.join(os.path.dirname(rel),filename)),'r') as stream:
        string = stream.read()
    if getTuple:
        stuple = string.split(".")
        stuple = [ int(val) for val in stuple ]
        return tuple(stuple)
    else:
        return string

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
    

def npArrayInfo(array,name):
    """Message describing this array"""
    fmtr = {}
    fmtr["name"] = name
    fmtr["type"] = str(type(array))
    if isinstance(array,np.ndarray):
        MSG = "%(name)s has %(elements)d elements with shape %(shape)s."
        fmtr["elements"] = array.size
        fmtr["shape"] = str(array.shape)
        try:
            fmtr["min"] = np.min(array)
            fmtr["max"] = np.max(array)
            fmtr["range"] = "[%(min)5.5g,%(max)5.5g]" % fmtr

        except ValueError:
            MSG += " Array does not appear to be numerical!"
        else:
            MSG += " Range %(range)s"
        fmtr["zeros"] = np.sum(array == np.zeros(array.shape))
        fmtr["zper"] = float(fmtr["zeros"]) / float(fmtr["elements"]) * 100
        if fmtr["zeros"] > 0:
            MSG += " Zeros %(zeros)d (%(zper)3d%%)."
        try:
            fmtr["nans"] = np.sum(np.isnan(array))
            fmtr["nper"] = float(fmtr["nans"]) / float(fmtr["elements"]) * 100
            if fmtr["nans"] > 0:
                MSG += " NaNs %(nans)d (%(nper)3d%%)."
        except TypeError:
            MSG += " Could not measure NaNs."    
        fmtr["dtype"] = array.dtype
        if fmtr["dtype"] != np.float64:
            MSG += " Data Type %(dtype)s."
    else:
        MSG = "%(name)s doesn't appear to be a Numpy Array! Type: %(type)s"
    return MSG % fmtr

class AbstractError(Exception):
    """An error which arose due to bad abstraction implemetnation"""
    pass

class HDUFrameTypeError(Exception):
    """docstring for HDUFrameTypeError"""
    pass
        
