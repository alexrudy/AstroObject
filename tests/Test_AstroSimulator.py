# -*- coding: utf-8 -*-
# 
#  Test_AstroSimulator.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-01-11.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.5.2
# 


from tests.AstroTest import *
import AstroObject.AstroSimulator as AS
from AstroObject.AstroCache import *
import nose.tools as nt
from nose.plugins.skip import Skip,SkipTest
import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import logging


class test_Simulator(API_Base):
    """AstroObject.AstroSimulator"""
    attributes = ["SIMULATOR"]
    
    def setup(self):
        """Set up the simulator"""
        self.SIMULATOR = AS.Simulator("Tester")
        super(test_Simulator, self).setup()
        
    
    def test_registerStage(self):
        """registerStage()"""
        self.SIMULATOR.registerStage(abs,"abs")
        assert "abs" in self.SIMULATOR.stages
        
        
class test_SimulatorFunctional(object):
    """Functional tests for AstroSimulator"""
    
    def test_BasicSimulation(self):
        """A very simple simulation with caching"""
        SIM = AS.Simulator(name="Loggy",commandLine=False)
    
        class SimpleStage(object):
            def __init__(self,SIM):
                super(SimpleStage, self).__init__()
                self.name = "SimpleStage"
                self.sim = SIM
    
            def run(self):
                print "Hello from %s Object" % self.name
                img = self.sim.Caches["Random Image"]
                self.A = img[0,0]
        
            def other(self):
                """Other Stage Function"""
                print "Hello from %s Stage" % "other"
                img = self.sim.Caches["Random NPY"]
                self.B = img[1,1]
    
            def last(self):
                """Last Stage Function"""
                print "Last Stage"
                img = self.sim.Caches["Random Image"]
                self.C = img[0,0]
    
            def save(self,data):
                """Saves some cache data"""
                np.save("Caches/Test.npy",data)
    
            def cache(self):
                """Cache this image"""
                return np.random.normal(10,2,(1000,1000))
        
            def load(self):
                """Load the image"""
                return np.load("Caches/Test.npy")
        
        stage = SimpleStage(SIM)
        log = logging.getLogger("Loggy")
        log.useConsole(False)
        
        SIM.registerStage(stage.run,name="examp",description="Example Stage",include=True)
        SIM.registerStage(stage.other,name="other",description="Other Stage",include=True)
        SIM.registerStage(stage.last,name="last",description="Last Stage",include=True)
        SIM.registerStage(None,"ex",dependencies=["examp","other"],help="example Macro")
        SIM.Caches["Random Image"] = Cache(stage.cache,stage.load,stage.save)
        SIM.Caches["Random NPY"] = NumpyCache(stage.cache,"Caches/Random.npy")
        SIM.Caches.clear()
        SIM.startup()
        SIM.do("all")
        log.useConsole(True)
        
        assert stage.A == stage.C
        assert stage.A != stage.B
        assert stage.B != stage.C
    
        
