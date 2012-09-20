# -*- coding: utf-8 -*-
# 
#  __init__.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.6.0
#  
 
import time,sys,os

from .loggers import *

from version import version as versionstr

__version__ = versionstr

__all__ = ['anaspec','image','base','spectra','logging','util']


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


