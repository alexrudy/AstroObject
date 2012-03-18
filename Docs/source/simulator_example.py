# Standard Scipy Toolkits
import numpy as np
import pyfits as pf
import scipy as sp

import math, copy, sys, time, logging, os, argparse

from AstroObject.AstroSimulator import *
from AstroObject.AstroCache import *

SIM = Simulator(commandLine=True)
    
class SimpleStage(object):
    def __init__(self,SIM):
        super(SimpleStage, self).__init__()
        self.name = "SimpleStage"
        self.sim = SIM
    
    def run(self):
        print "Hello from %s Object" % self.name
        img = self.sim.Caches.get("Random Image")
        print img[0,0]
        
    def other(self):
        """Other Stage Function"""
        print "Hello from %s Stage" % "other"
        img = self.sim.Caches.get("Random NPY")
        print img[1,1]
    
    def last(self):
        """Last Stage Function"""
        print "Last Stage"
        img = self.sim.Caches.get("Random Image")
        print img[0,0]
    
    def save(self,stream,data):
        """Saves some cache data"""
        np.save(stream,data)
        
    
    def cache(self):
        """Cache this image"""
        img = np.random.normal(10,2,(1000,1000))
        return img
        
    def load(self,stream):
        """Load the image"""
        try:
            img = np.load(stream)
        except IOError:
            raise CacheIOError("Couldn't find Cache File")
        return img
        
stage = SimpleStage(SIM)

SIM.registerStage(stage.run,name="examp",description="Example Stage")
SIM.registerStage(stage.other,name="other",description="Other Stage")
SIM.registerStage(stage.last,name="last",description="Last Stage")
SIM.registerStage(None,"ex",dependencies=["examp","other"],help="example Macro")
SIM.Caches.register("Random Image",stage.cache,stage.load,stage.save)
SIM.Caches.registerNPY("Random NPY",stage.cache,directory="Caches/",filename="Random.npy")
SIM.Caches.clear()
SIM.run()
