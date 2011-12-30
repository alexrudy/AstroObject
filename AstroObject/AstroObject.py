# 
#  AstroObject.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-19.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.2.9
# 

# This file maintains compatability with the 0.2 API for base classes

from AstroObjectBase import *
import logging

LOG = logging.getLogger(__name__)

LOG.warning("Using Depreciated Module: AstroObject, use AstroObjectBase instead!")
