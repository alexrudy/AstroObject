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
import matplotlib.image as mpimage
from pyraf import iraf

LOG = logging.getLogger("AstroObject Tests")




LOG.info("Starting Test Suite: %s" % __file__)

class ObjectTests(unittest.TestCase):
    """A class for testing the AstroObject objects"""
    def setUp(self):
        """Sets up the Object Tests"""
        self.EmptyFileName = "Tests/Empty.fits"
        self.EmptyFileNameEx = "Tests/Empty-Ex.fits"
        # Generate Object
        self.Object = AstroObject.FITSObject(filename=self.EmptyFileName)
        # Generate Empty Frame
        self.EmptyFrame = AstroObject.FITSFrame("Test Empty Frame")
        
        if os.access(self.EmptyFileName,os.F_OK):
            os.remove(self.EmptyFileName)
        
    
    def test_save(self):
        """Testing Save for type consistency and key consistency"""
        LOG.info("Testing Save for type consistency and key consistency")
        self.Object.save(self.EmptyFrame)
        self.assertRaises(TypeError,self.Object.save,[1,3])
        self.assertRaises(KeyError,self.Object.save,self.EmptyFrame)
    
    def test_show(self):
        """Testing the plotting functions for type output consistency"""
        LOG.info("Testing the plotting functions for type output consistency")
        self.Object.save(self.EmptyFrame)
        self.assertRaises(Utilities.AbstractError,self.Object.show)
        plt.savefig("Tests/simple_plot_gen")
        
    def test_write(self):
        """Tests the FITS file writing functions for an empty FITS file"""
        LOG.info("Tests the FITS file writing functions for an empty FITS file")
        self.Object.save(self.EmptyFrame)
        self.Object.write()
        self.assertTrue(os.access,(self.EmptyFileName,os.F_OK))
        
    def test_read(self):
        """Testing the abiltiy to read FITS Files"""
        LOG.info(self.test_read.__doc__)
        self.Object.read(self.EmptyFileNameEx)
        
    
    
    def tearDown(self):
        """Tears down UnitTests"""
        self.Object = None
        self.EmptyFrame = None
    
class ImageTests(unittest.TestCase):
    """A class for testing the AstroImage objects"""
    def setUp(self):
        """Sets up the Object Tests"""
        self.HongKongFileName = "Tests/Hong-Kong.fits"
        self.HongKongExFileName = "Tests/Hong-Kong-Ex.fits"
        self.HongKongImage = "Tests/Hong-Kong.jpg"
        self.EmptyFileName = "Tests/Empty-Ex.fits"
        # Generate Object
        self.EmptyObject = AstroImage.ImageObject()
        self.GrayScaleImage = np.sum(mpimage.imread(self.HongKongImage),axis=2)
        
    def test_loadfromfile(self):
        """Testing the ImageObject.loadFromFile method"""
        LOG.info("Testing the ImageObject.loadFromFile method")
        self.EmptyObject.loadFromFile(self.HongKongImage)
        
    def test_manipulation(self):
        """Testing the ImageObject.save and ImageObject.data methods for manipulation"""
        LOG.info("Testing the ImageObject.save and ImageObject.data methods for manipulation")
        self.EmptyObject.loadFromFile(self.HongKongImage)
        self.EmptyObject.save(np.sum(self.EmptyObject.data(),axis=2),"GrayScale Hong Kong Image")
        self.assertTrue(len(self.EmptyObject.object().shape) == 2)
        self.EmptyObject.show()
        plt.savefig("Tests/grayscale_image_gen")
    
    def test_frame(self):
        """Testing AstroImage.ImageFrame Object"""
        LOG.info("Testing AstroImage.ImageFrame Object")
        frame = AstroImage.ImageFrame(self.GrayScaleImage,"GrayScale Hong Kong Image")
        self.EmptyObject.save(frame)
        LOG.debug("Generated Frame %s" % frame)
        
    def test_write(self):
        """Testing writing image to a FITS File"""
        LOG.info(self.test_write.__doc__)
        frame = AstroImage.ImageFrame(self.GrayScaleImage,"GrayScale Hong Kong Image")
        self.EmptyObject.save(frame)
        if os.access(self.HongKongFileName,os.F_OK):
            os.remove(self.HongKongFileName)
        self.EmptyObject.write(self.HongKongFileName)
        
    def test_read(self):
        """Testing reading a FITS File"""
        LOG.info(self.test_read.__doc__)
        self.EmptyObject.read(self.HongKongExFileName)
        self.assertRaises(TypeError,self.EmptyObject.read,self.EmptyFileName)
        
        
        
    def tearDown(self):
        """docstring for tearDown"""
        self.EmptyObject = None
        self.GrayScaleImage = None


if __name__ != '__main__':
    LOG.critical(__name__+" is not a module, do not run it as one!")
    sys.exit(1)
else:
    LOG.debug("Removing Console Handler...")
    print "\n" + "-"*70
    logging.getLogger('').removeHandler(console)
    objectSuite = unittest.TestLoader().loadTestsFromTestCase(ObjectTests)
    imageSuite = unittest.TestLoader().loadTestsFromTestCase(ImageTests)
    alltests = unittest.TestSuite([objectSuite, imageSuite])
    result = unittest.TextTestRunner(verbosity=2).run(alltests)
    logging.getLogger('').addHandler(console)
    LOG.debug("Re-applying Console Handler...")
    LOG.info("Tests were %s" % "passed" if result.wasSuccessful() else "FAILED")
    
    
    
    
def ImageTests():
    """Performs basic Image Tests"""

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