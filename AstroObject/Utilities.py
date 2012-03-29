# 
#  Utilities.py
#  Astronomy ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.3.3
#

import numpy as np
import scipy as sp
import scipy.constants as spconst
import math
import logging,time,sys,collections,os
from pkg_resources import resource_string

from matplotlib.ticker import LogFormatter

__all__ = ["LogFormatterTeXExponent","getVersion","expandLim","BlackBody","Gaussian","validate_filename","update","npArrayInfo","AbstractError","HDUFrameTypeError","ConfigurationError","resource_string"]

LOG = logging.getLogger(__name__)

def disable_Console():
    """Disables console Logging"""
    logging.getLogger('').removeHandler(console)

def enable_Console():
    """docstring for enable_Console"""
    logging.getLogger('').addHandler(console)
    
def getVersion(rel=__name__,filename="VERSION",getTuple=False):
    """Returns the version number as either a string or tuple. The version number is retrieved from the "VERSION" file, which should contain just the text for the version and nothing else. When the version is returned as a tuple, each component (level) of the version number is a seperate, integer element of the tuple."""
    string = resource_string(rel,filename)
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
    """Expands Axis Limits by *scale*, given present axis limits"""
    xmin,xmax,ymin,ymax = axis
    xran = abs(xmax-xmin)
    yran = abs(ymax-ymin)

    xmax += xran*scale
    xmin -= xran*scale
    ymax += yran*scale
    ymin -= yran*scale

    axis = (xmin,xmax,ymin,ymax)
    return axis

def bin(array,factor):
    """Bins an array by the given factor"""
    
    finalShape = tuple((np.array(array.shape) / factor).astype(np.int))
    Aout = np.zeros(finalShape)
    
    for i in range(factor):
        Ai = array[i::factor,i::factor]
        Aout += Ai
    
    return Aout


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

def validate_filename(string,extension=".fits"):
    """Validates a string as an acceptable filename, stripping path components,etc.
    
    ..warning:: This function isn't very good. I wouldn't use it in its current state."""
    dirname,filename = os.path.split(string)
    if len(filename) < len(extension):
        filename = filename
    elif filename[-len(extension):] == extension:
        filename = filename[:-len(extension)]
    return os.path.join(dirname,filename+extension)

def update(d, u):
    """A deep update command for dictionaries.
    This is because the normal dictionary.update() command does not handle nested dictionaries."""
    if len(u)==0:
        return d
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d    

def npArrayInfo(array,name=None):
    """Message describing this array in excruciating detail. Used in debugging arrays where we don't know what they contain. Returns a message string.
    
    ::
        
        >>> arr = np.array([0,1,2,3,4,5,np.nan])
        >>> print npArrayInfo(arr,"Some Array")
        Some Array has 7 elements with shape (7,). Range [  nan,  nan] Zeros 1 ( 14%). NaNs 1 ( 14%). 
        >>> print npArrayInfo(arr[1:-1],"Some Array")
        Some Array has 5 elements with shape (5,). Range [    1,    5]
        
      
    """
    fmtr = {}
    MSG = ""
    if name != None:
        fmtr["name"] = name
        MSG += "%(name)s has "
    else:
        fmtr["name"] = str(array)
    fmtr["type"] = str(type(array))
    
    if isinstance(array,np.ndarray):
        
        MSG += "len %(elements)d shaped %(shape)s. "
        
        fmtr["elements"] = array.size
        fmtr["shape"] = str(array.shape)
        
        try:
            fmtr["min"] = np.min(array)
            fmtr["max"] = np.max(array)
            fmtr["range"] = "[%(min)5.5g,%(max)5.5g]" % fmtr
        except ValueError:
            MSG += "Array does not appear to be numerical! "
        else:
            MSG += "Range %(range)s "
        
        fmtr["zeros"] = np.sum(array == np.zeros(array.shape))
        
        fmtr["zper"] = float(fmtr["zeros"]) / float(fmtr["elements"]) * 100
        
        if fmtr["zeros"] > 0:
            MSG += "Zeros %(zeros)d (%(zper)3d%%). "
        
        try:
            fmtr["nans"] = np.sum(np.isnan(array))
            fmtr["nper"] = float(fmtr["nans"]) / float(fmtr["elements"]) * 100
            if fmtr["nans"] > 0:
                MSG += "NaNs %(nans)d (%(nper)3d%%). "
        except TypeError:
            MSG += "Could not measure NaNs. "
        
        fmtr["dtype"] = array.dtype
        
        if fmtr["dtype"] != np.float64:
            MSG += " Data Type %(dtype)s."
    elif isinstance(array,list):
        
        fmtr["elements"] = len(array)
        MSG += " %(elements)d elements "
        
        try:
            fmtr["min"] = min(array)
            fmtr["max"] = max(array)
            fmtr["range"] = "[%(min)5.5g,%(max)5.5g]" % fmtr
        except ValueError:
            MSG += " List does not appear to contain numerical elements."
        else:
            MSG += "Range %(range)s "
    else:
        MSG = "%(name)s doesn't appear to be a Numpy Array! Type: %(type)s"
    return MSG % fmtr

class AbstractError(Exception):
    """An error which arose due to bad abstraction implemetnation"""
    pass

class HDUFrameTypeError(Exception):
    """An error caused because an HDUFrame is of the wrong type for interpretation."""
    pass
    
class ConfigurationError(Exception):
    """Denotes an error caused by a bad configuration"""
    pass    

import re

class LogFormatterTeXExponent(LogFormatter, object):
    """Extends pylab.LogFormatter to use
    tex notation for tick labels."""

    def __init__(self, *args, **kwargs):
        super(LogFormatterTeXExponent,
              self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """Wrap call to parent class with
        change to tex notation."""
        label = super(LogFormatterTeXExponent,
                      self).__call__(*args, **kwargs)
        label = re.sub(r'e(\S)0?(\d+)',
                       r'\\times 10^{\1\2}',
                       str(label))
        label = "$" + label + "$"
        return label
        
__version__ = getVersion()
