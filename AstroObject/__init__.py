# -*- coding: utf-8 -*-
# 
#  __init__.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.5.3-p1
#  
 
import time,sys,os

from AstroObjectLogging import *

from version import version as versionstr

__version__ = versionstr

__all__ = ['AnalyticSpectra','AstroImage','AstroObjectBase','AstroSpectra','AstroObjectLogging','Utilities']


LOG = logging.getLogger(__name__)


