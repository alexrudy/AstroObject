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
from AstroImage import plt,np
import AstroImage, AstroSpectra


LOG = logging.getLogger("TESTING")
result = True

FileName = "Tests/Hong-Kong.jpg"
TestImage = AstroImage.FITSImage()
LOG.info("== Image Tests Starting ==")
LOG.info("Image Loading Procedure for File "+FileName+"...")
TestImage.loadFromFile(FileName)
LOG.info("Image Display:"+FileName+"...")
plt.figure(1)
TestImage.show()
LOG.info("Image Manipulation: GrayScale...")
TestImage.save(TestImage.data()[:,:,1],"GrayScale")
result = result and len(TestImage.object().shape) == 2
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

plt.draw()

result = result and np.abs(TestImage.data()-TestImage.data("GrayScale")).max() < 1e-20

if os.access("HongKong.fit",os.F_OK):
    LOG.debug("Removing HongKong.fit file")
    os.remove("HongKong.fit")

LOG.info("== Image Tests Complete ==")

LOG.info("Result = %s" % ("Passed" if result else "Failed"))

LOG.info("== Spectra Tests Starting ==")

TestSpectra = AstroSpectra.FITSSpectra()

LOG.info("Generating a Blackbody Spectrum at 5000K...")
x = np.linspace(0.1e-6,2e-6,1000)[1:]
TestSpectra.save(np.array([x,Utilities.BlackBody(x,5000)]),"BlackBody")
LOG.info("Displaying a Spectrum")
plt.figure(4)
TestSpectra.showSpectrum()

plt.show()
