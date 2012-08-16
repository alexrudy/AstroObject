# -*- coding: utf-8 -*-
# 
#  __init__.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-05-08.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 
u"""
:mod:`util` — Utility functions
===============================

Provides utilities useful in various places in the module.

.. automethod::
    AstroObject.util.getVersion
    
.. automethod::
    AstroObject.util.validate_filename
    
.. automethod::
    AstroObject.util.update
    
.. automethod::
    AstroObject.util.func_lineno
    
.. automethod::
    AstroObject.util.make_decorator
    
.. automethod::
    AstroObject.util.npArrayInfo
    
.. automodule::
    AstroObject.util.functions
    
.. automodule::
    AstroObject.util.images

.. automodule::
    AstroObject.util.mpl

.. automodule::
    AstroObject.util.pbar

"""
from __future__ import division
import os
import collections

import numpy as np

from ..version import version as versionstr

__all__ = [ "getVersion", "validate_filename", "update", "func_lineno", "make_decorator", "npArrayInfo", "ConfigurationError"]

__version__ = versionstr


def getVersion():
    """Returns the version number as either a string or tuple. The version number is retrieved from the "VERSION" file, which should contain just the text for the version and nothing else. When the version is returned as a tuple, each component (level) of the version number is a seperate, integer element of the tuple."""
    return versionstr

def validate_filename(resourcename,extension=".fits"):
    """Validates a string as an acceptable filename, stripping path components,etc.
    
    ..warning:: This function isn't very good. I wouldn't use it in its current state."""
    dirname,filename = os.path.split(resourcename)
    if not filename.endswith(extension):
        filename += extension
    return os.path.join(dirname,filename)

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

def func_lineno(func):
    """Get the line number of a function. First looks for
    compat_co_firstlineno, then func_code.co_first_lineno.
    """
    try:
        return func.compat_co_firstlineno
    except AttributeError:
        try:
            return func.func_code.co_firstlineno
        except AttributeError:
            return -1

def make_decorator(func):
    """
    Wraps a test decorator so as to properly replicate metadata
    of the decorated function, including nose's additional stuff
    (namely, setup and teardown).
    """
    def decorate(newfunc):
        if hasattr(func, 'compat_func_name'):
            name = func.compat_func_name
        else:
            name = func.__name__
        newfunc.__dict__ = func.__dict__
        newfunc.__doc__ = func.__doc__
        newfunc.__module__ = func.__module__
        if not hasattr(newfunc, 'compat_co_firstlineno'):
            newfunc.compat_co_firstlineno = func.func_code.co_firstlineno
        try:
            newfunc.__name__ = name
        except TypeError:
            # can't set func name in 2.3
            newfunc.compat_func_name = name
        return newfunc
    return decorate

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


class HDUFrameTypeError(Exception):
    """An error caused because an HDUFrame is of the wrong type for interpretation."""
    pass
    
class ConfigurationError(Exception):
    """Denotes an error caused by a bad configuration"""
    pass    


