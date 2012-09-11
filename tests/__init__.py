# -*- coding: utf-8 -*-
# 
#  __init__.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-03-17.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.5.3-p1
# 

from AstroObject.AstroObjectLogging import *

__config__ = "logging.yaml"


LOG = logging.getLogger("AstroObject")
LOG.configure_from_file(filename = __config__ )
LOG.start()
