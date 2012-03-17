# 
#  __init__.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-03-17.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 

from AstroObject.AstroObjectLogging import *

__config__ = "logging.yaml"


LOG = logging.getLogger("AstroObject")
LOG.configure(configFile = __config__ )
LOG.start()
