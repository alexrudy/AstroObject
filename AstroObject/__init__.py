# 
#  __init__.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.2.5
#  
 
import time,sys,os

from AstroObjectLogging import *

__version__ = '0.2.5'

__all__ = ['AnalyticSpectra','AstroImage','AstroObjectBase','AstroSpectra','AstroObjectLogging','Utilities']

__config__ = "logging.yaml"

LOG = logging.getLogger(__name__)
LOG.configure(configFile = __config__ )
LOG.start()
