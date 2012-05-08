# -*- coding: utf-8 -*-
# 
#  images.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-05-08.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 

import numpy as np

def bin(array,factor):
    """Bins an array by the given factor"""
    
    finalShape = tuple((np.array(array.shape) / factor).astype(np.int))
    Aout = np.zeros(finalShape)
    
    for i in range(factor):
        Ai = array[i::factor,i::factor]
        Aout += Ai
    
    return Aout
