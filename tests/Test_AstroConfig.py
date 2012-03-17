# -*- coding: utf-8 -*-
# 
#  Test_AstroConfig.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-03-17.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.0.0
# 

# Python Imports
import math, copy, sys, time, logging, os

# Testing Imports
import nose.tools as nt
from nose.plugins.skip import Skip,SkipTest

# AstroObject Import
from AstroObject.AstroConfig import *

class Test_Configuration(object):
    """Configuration"""
    
    def setUp(self):
        """docstring for setUp"""
        self.cfgA = {"Hi":{"A":1,"B":2,},}
        self.cfgB = {"Hi":{"A":3,"C":4,},}
        self.cfgC = {"Hi":{"A":3,"B":2,"C":4,},} #Should be a merge of A and B
        
    
    def test_init(self):
        """__init__"""
        cfg = Configuration(self.cfgC)
    
    def test_update(self):
        """update() deep updates"""
        cfg = Configuration(self.cfgA)
        cfg.update(self.cfgB)
        assert cfg == self.cfgC
    
        
    def test_merge(self):
        """merge() deep updates"""
        cfg = Configuration(self.cfgA)
        cfg.merge(self.cfgB)
        assert cfg == self.cfgC
        
    def test_save(self):
        """save() writes yaml file or dat file"""
        cfg = Configuration(self.cfgC)
        cfg.save("Test.yaml")
        os.remove("Test.yaml")
        cfg.save("Test.dat")
        os.remove("Test.dat")
        
        
    def test_read(self):
        """load() reads a yaml file."""
        cfg = Configuration(self.cfgC)
        cfg.save("Test.yaml")
        cfg = Configuration()
        cfg.load("Test.yaml")
        assert cfg == self.cfgC
        os.remove("Test.yaml")
        