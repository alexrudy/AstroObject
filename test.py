#!/usr/bin/env python
# 
#  test.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 

execfile("__init__.py")
import logging,os
import Utilities
from AstroImage import plt
import AstroImage


LOG = logging.getLogger("TESTING")

FileName = "Tests/Hong-Kong.jpg"
TestImage = AstroImage.FITSImage()

LOG.info("Image Loading Procedure for File "+FileName+"...")
TestImage.loadFromFile(FileName)
LOG.info("Image Display:"+FileName+"...")
plt.figure(1)
TestImage.show()
LOG.info("Image Manipulation: GrayScale...")
TestImage.save(TestImage.data()[:,:,1],"GrayScale")
LOG.info("Image Display: GrayScale...")
plt.figure(2)
TestImage.show()

if os.access("HongKong.fit",os.F_OK):
    LOG.debug("Removing old HongKong.fit file")
    os.remove("HongKong.fit")

LOG.info("FITS File Writing...")
TestImage.FITS("HongKong.fit")
LOG.info("FITS File Reading...")
TestImage.loadFromFITS("HongKong.fit")
LOG.info("Image Display: Loaded from FITS")
plt.figure(3)
TestImage.show()
plt.show()

if os.access("HongKong.fit",os.F_OK):
    LOG.debug("Removing HongKong.fit file")
    os.remove("HongKong.fit")

LOG.info("TESTS PASSED")
