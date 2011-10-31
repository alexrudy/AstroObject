#!/usr/bin/env python
# 
#  test.py
#  ObjectModel
#  
#  Created by Alexander Rudy on 2011-10-07.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.2.0
# 

execfile("__init__.py")
import logging,os,sys,unittest
import Utilities
from AstroImage import plt,np
import AstroImage, AstroSpectra, AnalyticSpectra, AstroObjectBase
import matplotlib as mpl
import matplotlib.image as mpimage
from pyraf import iraf

LOG = logging.getLogger("AstroObject Tests")




LOG.info("Starting Test Suite: %s" % __file__)

class TestsObject(unittest.TestCase):
    """A class for testing the AstroObject objects"""
    def setUp(self):
        """Sets up the Object Tests"""
        self.EmptyFileName = "Tests/Empty.fits"
        self.EmptyFileNameEx = "Tests/Empty-Ex.fits"
        # Generate Object
        self.Object = AstroObjectBase.FITSObject(filename=self.EmptyFileName)
        # Generate Empty Frame
        self.EmptyFrame = AstroObjectBase.FITSFrame("Test Empty Frame")
        
        if os.access(self.EmptyFileName,os.F_OK):
            os.remove(self.EmptyFileName)
        
    
    def test_save(self):
        """FITSObject.save will reject poorly typed objects and objects with identical labels"""
        LOG.info("TEST: "+self.test_save.__doc__)
        self.Object.save(self.EmptyFrame)
        self.assertRaises(TypeError,self.Object.save,[1,3])
        self.assertRaises(KeyError,self.Object.save,self.EmptyFrame)
        
    
    def test_show(self):
        """FITSFrame will raise an AbstractError on FITSObject.show"""
        LOG.info("TEST: "+self.test_show.__doc__)
        self.Object.save(self.EmptyFrame)
        self.assertRaises(Utilities.AbstractError,self.Object.show)
        
    
    def test_write(self):
        """Existance of written empty FITS File after calling FITSObject.write"""
        LOG.info("TEST: "+self.test_write.__doc__)
        self.Object.save(self.EmptyFrame)
        self.Object.write()
        self.assertTrue(os.access,(self.EmptyFileName,os.F_OK))
        
    
    def test_read(self):
        """Code Reads Empty FITS File error-free"""
        LOG.info("TEST: "+self.test_read.__doc__)
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
        self.TestReadWriteFileName = "Tests/Hong-Kong-Test.fits"
        # Generate Object
        self.EmptyObject = AstroImage.ImageObject()
        self.GrayScaleImage = np.int32(np.sum(mpimage.imread(self.HongKongImage),axis=2))
        plt.clf()
        
    
    def test_loadfromfile(self):
        """ImageObject.loadFromFile method runs"""
        LOG.info("TEST: "+self.test_loadfromfile.__doc__)
        self.EmptyObject.loadFromFile(self.HongKongImage)
        
    
    def test_manipulation(self):
        """ImageObject.save and ImageObject.data methods correctly handle two forms of data"""
        LOG.info("TEST: "+self.test_manipulation.__doc__)
        self.EmptyObject.loadFromFile(self.HongKongImage)
        self.EmptyObject.save(np.flipud(np.sum(self.EmptyObject.data(),axis=2)),"GrayScale Hong Kong Image")
        self.assertTrue(self.EmptyObject.data().ndim == 2)
        self.EmptyObject.show()
        plt.title("Grayscale Image of Hong Kong")
        plt.gca().set_xticks([])
        plt.gca().set_yticks([])
        plt.colorbar()
        plt.savefig("Tests/Grayscale-Hong-Kong")
        
    
    def test_frame(self):
        """AstroImage.ImageFrame saves Image Data"""
        LOG.info("TEST: "+self.test_frame.__doc__)
        frame = AstroImage.ImageFrame(self.GrayScaleImage,"GrayScale Hong Kong Image")
        self.EmptyObject.save(frame)
        LOG.debug("Generated Frame %s" % frame)
        
    
    def test_write(self):
        """ImageFrame produces a FITS File"""
        LOG.info("TEST: "+self.test_write.__doc__)
        frame = AstroImage.ImageFrame(self.GrayScaleImage,"GrayScale Hong Kong Image")
        self.EmptyObject.save(frame)
        if os.access(self.HongKongFileName,os.F_OK):
            os.remove(self.HongKongFileName)
        self.EmptyObject.write(self.HongKongFileName)
        self.assertTrue(os.access,(self.HongKongFileName,os.F_OK))
        
    
    def test_read(self):
        """ImageObject reads Image Files, but not Empty Files"""
        LOG.info("TEST: "+self.test_read.__doc__)
        self.EmptyObject.read(self.HongKongExFileName)
        self.assertRaises(ValueError,self.EmptyObject.read,self.EmptyFileName)
        
    
    def test_readwrite(self):
        """Image Data is preserved through read and write"""
        LOG.info("TEST: "+self.test_readwrite.__doc__)
        self.EmptyObject.save(self.GrayScaleImage,"GrayScale Hong Kong Image")
        self.EmptyObject.write(self.TestReadWriteFileName)
        self.EmptyObject.read(self.TestReadWriteFileName,"Imported Hong Kong Image")
        self.assertAlmostEqual(np.abs(self.EmptyObject.data()-self.EmptyObject.data("GrayScale Hong Kong Image")).max(),0)
        
    
    def tearDown(self):
        """docstring for tearDown"""
        self.EmptyObject = None
        self.GrayScaleImage = None
        if os.access(self.TestReadWriteFileName,os.F_OK):
            os.remove(self.TestReadWriteFileName)
        
    

class SpectraTests(unittest.TestCase):
    """docstring for SpectraTests"""
    
    BlackBody = {}
    T = 5000.
    BlackBody["WL"]   = np.linspace(0.37e-6,2e-6,1e5)
    BlackBody["Flux"] = Utilities.BlackBody(BlackBody["WL"],T)
    ImageData = np.array([[3.,2.,4.],[3.,4.,2],[4.,1.,9.]])
    
    def setUp(self):
        """Set up the Spectra Tests"""
        self.BlackBodyFile = "BlackBody.fits"
        self.BlackBodyImage = "BlackBody.png"
        self.SpectrumObject = AstroSpectra.SpectraObject()
        self.SpectrumData = np.array([self.BlackBody["WL"],self.BlackBody["Flux"]])
        plt.clf()
        
    
    def test_save(self):
        """Saves a simple BlackBody Spectrum"""
        LOG.info("Test: " + self.test_save.__doc__)
        self.SpectrumObject.save(self.SpectrumData,"BlackBody Data")
        Frame = AstroSpectra.SpectraFrame(self.SpectrumData,"BlackBody Frame")
        self.SpectrumObject.save(Frame)
        self.assertRaises(KeyError,self.SpectrumObject.save,Frame)
        
    
    def test_validate(self):
        """Verifies that a spectrum is 1-D etc."""
        LOG.info("Test: " + self.test_validate.__doc__)
        Frame = AstroSpectra.SpectraFrame(self.SpectrumData,"BlackBody Frame")
        Frame.validate()
        ImFrame = AstroSpectra.SpectraFrame(self.ImageData,"Image Data")
        self.assertRaises(AssertionError,ImFrame.validate)
        
    
    def test_show(self):
        """Produces an Example Figure"""
        LOG.info("Test: " + self.test_show.__doc__)
        plt.figure()
        self.SpectrumObject.save(self.SpectrumData,"BlackBody")
        self.SpectrumObject.show()
        plt.xlabel("Wavelength (m)")
        plt.ylabel("Flux (J/s)")
        plt.title("Blackbody Spectrum at %dK" % self.T)
        plt.savefig("Tests/"+ self.BlackBodyImage)
        
    
    def test_read_write(self):
        """Reads and Writes a Spectrum Image"""
        LOG.info("Test: " + self.test_read_write.__doc__)
        self.SpectrumObject.save(self.SpectrumData,"BlackBody")
        if os.access("Tests/"+ self.BlackBodyFile,os.F_OK):
            os.remove("Tests/"+ self.BlackBodyFile)
        self.SpectrumObject.write("Tests/" + self.BlackBodyFile)
        self.SpectrumObject.read( "Tests/" + self.BlackBodyFile)
        self.assertAlmostEqual(np.abs(self.SpectrumObject.data()-self.SpectrumObject.data("BlackBody")).max(),0)
    


class AnalayticSpectraTests(unittest.TestCase):
    """Tests on the AnalyticSpectra model"""
    
    
    wavelength = np.linspace(0.37e-6,2e-6,1e5)
    
    
    def setUp(self):
        """Initial variables for Analytic Spectra Tests"""
        self.SpectrumObject = AstroSpectra.SpectraObject()
        self.RenderedFilename = "AnalyticRender.png"
        plt.clf()
    
    def test_render(self):
        """Rendering a blackbody and a gaussain spectrum"""
        LOG.info("Test: "+self.test_render.__doc__)
        BlackbodyS = AnalyticSpectra.BlackBodySpectrum(5000)
        GaussianS = AnalyticSpectra.GaussianSpectrum(0.5e-6,0.5e-7,1e12)
        self.SpectrumObject.save(BlackbodyS(self.wavelength),BlackbodyS.label)
        self.SpectrumObject.save(GaussianS(self.wavelength),GaussianS.label)
        
    def test_compose(self):
        """Test composition spectra rendering and saving"""
        LOG.info("Test: "+self.test_compose.__doc__)
        BlackbodyS = AnalyticSpectra.BlackBodySpectrum(5000)
        GaussianS = AnalyticSpectra.GaussianSpectrum(1.0e-6,0.5e-7,5e12)
        CompositeS = BlackbodyS + GaussianS
        self.SpectrumObject.save(CompositeS(self.wavelength),CompositeS.label)
        self.SpectrumObject.show()
        plt.savefig("Tests/"+self.RenderedFilename)

if __name__ != '__main__':
    LOG.critical(__name__+" is not a module, do not run it as one!")
else:
    LOG.debug("Removing Console Handler...")
    print "\n" + "-"*70
    logging.getLogger('').removeHandler(console)
    
    objectSuite = unittest.TestLoader().loadTestsFromTestCase(ObjectTests)
    imageSuite = unittest.TestLoader().loadTestsFromTestCase(ImageTests)
    spectraSuite = unittest.TestLoader().loadTestsFromTestCase(SpectraTests)
    analyticSuite = unittest.TestLoader().loadTestsFromTestCase(AnalayticSpectraTests)
    
    alltests = unittest.TestSuite([objectSuite, imageSuite, spectraSuite, analyticSuite])
    
    result = unittest.TextTestRunner(verbosity=2).run(alltests)
    
    logging.getLogger('').addHandler(console)
    LOG.debug("Re-applying Console Handler...")
    LOG.info("Tests were %s" % "passed" if result.wasSuccessful() else "FAILED")
    
