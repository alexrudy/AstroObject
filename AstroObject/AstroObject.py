# -*- coding: utf-8 -*-
# 
#  AstroObject.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-19.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.5.3
# 
"""This file maintains module level compatibility with the 0.2 API for base classes. It has been depreciated."""
# This file maintains compatability with the 0.2 API for base classes

import AstroObject.AstroObjectBase
from AstroObject.AstroObjectBase import *
import logging

__all__ = AstroObject.AstroObjectBase.__all__

LOG = logging.getLogger(__name__)

LOG.warning("Using Depreciated Module: AstroObject, use AstroObjectBase instead!")
