# -*- coding: utf-8 -*-
# 
#  Test_AstroConfig.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-03-17.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.5.3-p1
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
        self.filename = "Time.dat"
        self.cache = Cache(self.generate,self.load,self.save,self.filename)
        self.manager = CacheManager("Caches","SomeString",expiretime=100)
        self.manager["Cache"] = self.cache
        
    def generate(self):
        """Generate data for this item"""
        return "Some string for now %s" % time.clock()
        
    def save(self,data,filename):
        """Save the data"""
        with open(filename,'w') as stream:
            stream.write(data)
    
    def load(self,filename):
        """docstring for load"""
        with open(filename,'r') as stream:
            for line in stream:
                return line
    
    def test_call(self):
        """__call__() cache"""
        first = self.manager["Cache"]
        second = self.manager["Cache"]
        self.cache.reset()
        third = self.manager["Cache"]
        self.cache.reset()
        self.manager.clear()
        fourth = self.manager["Cache"]
        assert first == second and second == third
        assert first != fourth        
    
class Test_YAMLCache(Test_Cache):
    """AstroObject.AstroCache.YAMLCache"""
    def setUp(self):
        """Fixtures for this test"""
        self.filename = "Time.yaml"
        self.cache = YAMLCache(self.generate,self.filename)
        self.manager = CacheManager("Caches","SomeString",expiretime=100)
        self.manager["Cache"] = self.cache
        
        
    def generate(self):
        """Generate data for this item"""
        return {"Key":"Some string for now %s" % time.clock()}
    
    
    
        
