# -*- coding: utf-8 -*-
# 
#  __init__.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-03-17.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.6.0
# 

from AstroObject.loggers import *

__config__ = "tests/logging.yaml"


LOG = logging.getLogger("AstroObject")
LOG.configure_from_file(filename = __config__ )
LOG.start()
