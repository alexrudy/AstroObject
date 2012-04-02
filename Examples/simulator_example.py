#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
#  simulator_example.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-03-18.
#  Copyright 2012 Alexander Rudy. All rights reserved.
# 

# Standard Scipy Toolkits
import numpy as np

# Standard Python imports 
import math, copy, sys, time, logging, os, argparse

# AstroObject Imports
from AstroObject.AstroSimulator import *
from AstroObject.AstroCache import *


    
class SimpleStage(Simulator):
    """An example simulator designed to show the power of simulations and for use while testing."""
    def __init__(self,*args,**kwargs):
        super(SimpleStage, self).__init__(*args,**kwargs)
        self.registerStage(self.main,include=True)
        self.registerStage(self.other,include=True)
        self.registerStage(self.last,include=True)
        self.registerStage(None,"ex",description="Example Macro",dependencies=["main","other"],help="example Macro")
        self.Caches["Random Image"] = Cache(self.cache,self.load,self.save)
        self.Caches["Random NPY"] = NumpyCache(self.cache,filename="%s/Random.npy" % self.config["Dirs"]["Caches"])
        
    def main(self):
        """Main Stage"""
        print "Hello from %s Object" % self.name
        img = self.Caches["Random Image"]
        print img[0,0]
        
    def other(self):
        """Other Stage"""
        print "Hello from %s Stage" % "other"
        img = self.Caches["Random NPY"]
        print img[1,1]
    
    def last(self):
        """Last Stage"""
        print "Last Stage"
        img = self.Caches["Random Image"]
        print img[0,0]
    
    def save(self,data):
        """Saves some cache data"""
        np.save("%s/Random.npy" % self.config["Dirs"]["Caches"],data)
        
    def cache(self):
        """Cache this image"""
        return np.random.normal(10,2,(1000,1000))
        
    def load(self):
        """Load the image"""
        return np.load("%s/Random.npy" % self.config["Dirs"]["Caches"])
        

if __name__ == '__main__':
    Sim = SimpleStage(commandLine=True)
    Sim.run()
