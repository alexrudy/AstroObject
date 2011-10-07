#!/usr/bin/env python
# 
#  test.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 

import logging
import Utilities
from AstroImage import plt
import AstroImage


LOG = logging.getLogger("test.py")

FileName = "./Tests/Hong-Kong.jpg"
TestImage = AstroImage.FITSImage()

TestImage.loadFromFile(FileName)
LOG.info("Loaded Image "+FileName)
TestImage.show()
LOG.info("Showing Image")
plt.show()