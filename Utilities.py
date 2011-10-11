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
import pyfits
import logging,time,sys


LOG = logging.getLogger(__name__)

def set_axis_padding(xytup,*otherxy):
    """docstring for set_axis_padding"""
    xs,ys = xytup
    
    if otherxy != ():
        for xad,yad in otherxy:
            xs = tuple(xs) + tuple(xad)
            ys = tuple(ys) + tuple(yad)
    
        x = np.concatenate(xs)
        y = np.concatenate(ys)
    else:
        x = xs
        y = ys
    
    plt.axis([min(x)-(max(x)-min(x))*0.05, max(x)+(max(x)-min(x))*0.05, min(y)-(max(y)-min(y))*0.05, max(y)+(max(y)-min(y))*0.05])
    



def validate_filename(string,extension=".fit"):
    """Validates a string as an acceptable filename, stripping path components,etc."""
    return string.replace("/","").rstrip(extension).replace(".","") + extension
    

