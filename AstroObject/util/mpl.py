# -*- coding: utf-8 -*-
# 
#  mpl_utilities.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-04-17.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.5.2
# 
u"""
:mod:`mpl` – Matplotlib helpers
-------------------------------

This module provides helpers which are dependent on :mod:`matplotlib`.

.. autoclass::
    AstroObject.util.mpl.LogFormatterTeXExponent
    :members:
    :special-members:
    
.. automethod::
    AstroObject.util.mpl.expandLim
    
.. automethod::
    AstroObject.util.mpl.get_padding

"""

import re
from matplotlib.ticker import LogFormatter

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
