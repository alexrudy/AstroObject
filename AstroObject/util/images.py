# -*- coding: utf-8 -*-
# 
#  images.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-05-08.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 
u"""
:mod:`util.images` – Functions for image manipulation
-----------------------------------------------------

.. automethod:: 
    AstroObject.util.images.bin

"""
import numpy as np

def bin(array,factor):
    """Bins an array by the given factor in each axis."""
    Aout = np.zeros(tuple((np.array(array.shape) / factor).astype(np.int)), dtype=array.dtype)
    [ Aout += array[i::factor,i::factor] for i in range(factor) ]
    return Aout
