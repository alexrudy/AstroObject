# -*- coding: utf-8 -*-
# 
#  Test_AstroConfig.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-03-17.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.5.2
# 

# Python Imports
import math, copy, sys, time, logging, os

# Testing Imports
import nose.tools as nt
from nose.plugins.skip import Skip,SkipTest

# AstroObject Import
from AstroObject.AstroCache import *
from AstroObject.AstroConfig import *



class Test_Cache(object):
    """AstroObject.AstroCache.Cache"""
    def setUp(self):
        """Fixtures for this test"""
        self.cache = Cache(self.generate,self.load,self.save)
        self.filename = "Caches/Time.dat"
        
    def generate(self):
        """Generate data for this item"""
        return "Some string for now %s" % time.clock()
        
    def save(self,data):
        """Save the data"""
        with open(self.filename,"w") as stream:
            stream.write(data)
    
    def load(self):
        """docstring for load"""
        with open(self.filename,"r") as stream:
            for line in stream:
                return line
    
    def test_call(self):
        """__call__() cache"""
        first = self.cache()
        second = self.cache()
        self.cache.reset()
        third = self.cache()
        self.cache.reset()
        os.remove(self.filename)
        fourth = self.cache()
        assert first == second and second == third
        assert first != fourth
        os.remove(self.filename)
        
    
class Test_YAMLCache(Test_Cache):
    """AstroObject.AstroCache.YAMLCache"""
    def setUp(self):
        """Fixtures for this test"""
        self.filename = "Caches/Time.yaml"
        self.cache = YAMLCache(self.generate,self.filename)
        
    def generate(self):
        """Generate data for this item"""
        return {"Key":"Some string for now %s" % time.clock()}

class Test_ConfigCache(Test_Cache):
    """AstroObject.AstroCache.ConfigCache"""
    def setUp(self):
        """Fixtures for this test"""
        self.filename = "Caches/TCFG.yaml"
        self.config = Configuration({"Key":"Some string for now %s" % time.clock()})
        self.cache = ConfigCache(self.config,self.filename)    
        
    def test_call(self):
        """__call__() cache"""
        first = self.cache()
        second = self.cache()
        self.cache.reset()
        third = self.cache()
        assert first == second and second == third
        os.remove(self.filename)
        fourth = ConfigCache(Configuration({"Key":"Some string for now %s" % time.clock()}),self.filename)()
        assert first != fourth
        os.remove(self.filename)
        
    
    
    
        
