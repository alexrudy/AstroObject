#!/usr/bin/env python
# 
#  test.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
# 

execfile("__init__.py")
import logging,os,sys,unittest
import Utilities
from AstroImage import plt,np
import AstroImage, AstroSpectra, AnalyticSpectra, AstroObject
import matplotlib as mpl
from pyraf import iraf

LOG = logging.getLogger("AstroObject Tests")




LOG.info("Starting Test Suite: %s" % __file__)

class ObjectTests(unittest.TestCase):
    """A class for testing the AstroObject objects"""
    def setUp(self):
        """Sets up the Object Tests"""
        LOG.info("--Object Tests--")
        # Generate Object
        self.Object = AstroObject.FITSObject()
        # Generate Empty Frame
        self.Frame = AstroObject.FITSFrame("Test Empty Frame")
        
        self.Object.save(self.Frame)
    
    def test_save(self):
        """Tests save"""
        self.assertRaises(TypeError,self.Object.save,[1,3])
        self.assertRaises(KeyError,self.Object.save,self.Frame)
    
    def test_show(self):
        """Tests the plotting functions"""
        self.assertEqual(type(plt.plot([1])),type(self.Object.show()))
    
    def tearDown(self):
        """Tears down UnitTests"""
        LOG.info("--Completed Object Tests--")
        plt.show()
    
        
def ObjectTest():
    """docstring for ObjectTests"""
    Passed = True
    
    Object.save(Frame)
    Object.show()
    LOG.info("Returned List Correctly: ")

if __name__ != '__main__':
    LOG.critical(__name__+" is not a module, do not run it as one!")
    sys.exit(1)
else:
    LOG.info("Removing Console Handler...")
    logging.getLogger('').removeHandler(console)
    suite = unittest.TestLoader().loadTestsFromTestCase(ObjectTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
    logging.getLogger('').addHandler(console)
    LOG.info("Re-applying Console Handler...")
    
    
def ImageTests():
    """Performs basic Image Tests"""
    ImageResult = True
    LOG.info("== Image Tests Starting ==")
    LOG.info("Allocating Image Object")
    FileName = "Tests/Hong-Kong.jpg"
    TestImage = AstroImage.ImageObject()

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
    return ImageResult


def SpectraTests():
    """Tests the facilities for raw spectra"""
    LOG.info("== Spectra Tests Starting ==")

    TestSpectra = AstroSpectra.SpectraObject()

    LOG.info("Generating a Blackbody Spectrum at 5000K...")
    x = np.linspace(0.1e-6,2e-6,1000)[1:]
    TestSpectra.save(np.array([x,Utilities.BlackBody(x,5000)]),"BlackBody")
    LOG.info("Displaying a Spectrum")
    plt.figure(4)

    TestSpectra.showSpectrum()
    plt.xlabel("Wavelength")
    plt.ylabel("Flux (Joules)")

def AnalyticSpectraTests():
    """docstring for AnalyticSpectraTests"""
    LOG.info("== Analytic Spectra Testing ==")
    TestSpectra = AstroSpectra.SpectraObject()
    
    LOG.info("Generating Spectrum Components")
    BlackBody = AnalyticSpectra.BlackBodySpectrum(5000)
    Gaussian = AnalyticSpectra.GaussianSpectrum(0.5e-6,0.5e-8,4e12)
    Composed = Gaussian + BlackBody
    x = np.linspace(0.1e-6,2e-6,1000)[1:]
    LOG.info("Saving Generated Spectrum (and rendering...)")
    TestSpectra.save(np.array([x,Composed(x)]),"Composed Spectrum")

    LOG.info("Plotting Generated Spectrum")
    plt.figure(5)
    TestSpectra.showSpectrum()


def IRAFTests():
    """Testing IRAF Interaction"""
    LOG.info("== IRAF Interaction Tests Starting ==")
    FileName = "Tests/Hong-Kong.jpg"
    TestImage = AstroImage.ImageObject()

    LOG.info("Loading Image from File "+FileName+"...")
    TestImage.loadFromFile(FileName)
    
    LOG.info("Image Manipulation: GrayScale...")
    TestImage.save(TestImage.data()[:,:,1],"GrayScale")
    
    iraf.imarith(TestImage.inFITS(),"/",2,TestImage.outFITS(statename="Half"))
    TestImage.reloadFITS()
    plt.figure(6)
    TestImage.show()




# LOG.info("Result = %s" % ("Passed" if result else "Failed"))