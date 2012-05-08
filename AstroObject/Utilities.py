# -*- coding: utf-8 -*-
# 
#  Utilities.py
#  Astronomy ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.5.2
#
"""
AstroObject :mod:`Utilities`
============================

These are mostly internal module utility functions, documented here in case you find them useful. They are not guaranteed to function in any way.

.. autofunction:: AstroObject.Utilities.getVersion

.. autofunction:: AstroObject.Utilities.npArrayInfo

.. autofunction:: AstroObject.Utilities.expandLim

.. autofunction:: AstroObject.Utilities.bin

.. autofunction:: AstroObject.Utilities.BlackBody

.. autofunction:: AstroObject.Utilities.Gaussian

"""
from __future__ import division
import numpy as np
import scipy as sp
import scipy.constants as spconst
import math
import logging,time,sys,collections,os
from pkg_resources import resource_string


import terminal as terminal
from version import version as versionstr


LOG = logging.getLogger(__name__)



def disable_Console():
    """Disables console Logging"""
    logging.getLogger('').removeHandler(console)

def enable_Console():
    """docstring for enable_Console"""
    logging.getLogger('').addHandler(console)
    

                
