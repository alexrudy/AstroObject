#!/usr/bin/env python
# 
#  test.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 

execfile("__init__.py")
import logging,os,sys
import Utilities
from AstroImage import plt,np
import AstroImage, AstroSpectra
import matplotlib as mpl
from pyraf import iraf

LOG = logging.getLogger("AstroObject Tests")

ImageResult = True

if __name__ != '__main__':
    LOG.critical(__name__+" is not a module, do not run it as one!")
    sys.exit(1)

LOG.info("== Image Tests Starting ==")
LOG.info("Allocating Image Object")
FileName = "Tests/Hong-Kong.jpg"
TestImage = AstroImage.FITSImage()

LOG.info("Loading Image from File "+FileName+"...")
TestImage.loadFromFile(FileName)

LOG.info("Plotting Image "+TestImage.statename+"...")
plt.figure(1)
TestImage.show()
plt.title("Image: "+TestImage.statename)

LOG.info("Image Manipulation: GrayScale...")
TestImage.save(TestImage.data()[:,:,1],"GrayScale")
ImageResult = ImageResult and len(TestImage.object().shape) == 2

LOG.info("Plotting Image: "+TestImage.statename+"...")
plt.figure(2)
TestImage.show()
plt.title("Image"+TestImage.statename)

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
plt.title("Image"+TestImage.statename)

ImageResult = ImageResult and np.abs(TestImage.data()-TestImage.data("GrayScale")).max() < 1e-20

if os.access("HongKong.fit",os.F_OK):
    LOG.debug("Removing HongKong.fit file")
    os.remove("HongKong.fit")

LOG.info("== Image Tests Complete ==")

LOG.info("Result = %s" % ("Passed" if ImageResult else "Failed"))

LOG.info("== Spectra Tests Starting ==")

TestSpectra = AstroSpectra.FITSSpectra()

LOG.info("Generating a Blackbody Spectrum at 5000K...")
x = np.linspace(0.1e-6,2e-6,1000)[1:]
TestSpectra.save(np.array([x,Utilities.BlackBody(x,5000)]),"BlackBody")
LOG.info("Displaying a Spectrum")
plt.figure(4)

TestSpectra.showSpectrum()
plt.xlabel("Wavelength")
plt.ylabel("Flux (Joules)")

plt.show()

LOG.info("== IRAF Interaction Tests Starting ==")

iraf.imarith(TestImage.inFITS(),"/",2,TestImage.outFITS(statename="Half"))
TestImage.reloadFITS()
plt.figure(4)
TestImage.show()


# LOG.info("Result = %s" % ("Passed" if result else "Failed"))