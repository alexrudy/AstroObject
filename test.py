#!/usr/bin/env python
# 
#  test.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 

execfile("__init__.py")
import logging
import Utilities
from AstroImage import plt
import AstroImage


LOG = logging.getLogger("test.py")

FileName = "Tests/Hong-Kong.jpg"
TestImage = AstroImage.FITSImage()

TestImage.loadFromFile(FileName)
LOG.info("Loaded Image:"+FileName)
plt.figure(1)
TestImage.show()
LOG.info("Showing Image:"+FileName)
TestImage.save(TestImage.data()[:,:,1],"GrayScale")
LOG.info("Grayscaled Image: GrayScale")
plt.figure(2)
TestImage.show()
LOG.info("Showing Image: GrayScale")
plt.show()