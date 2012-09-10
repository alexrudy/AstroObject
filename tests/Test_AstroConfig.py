# -*- coding: utf-8 -*-
# 
#  Test_AstroConfig.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2012-03-17.
#  Copyright 2012 Alexander Rudy. All rights reserved.
#  Version 0.5.3-p2
# 

# Python Imports
import math, copy, sys, time, logging, os

# Testing Imports
import nose.tools as nt
from nose.plugins.skip import Skip,SkipTest

# AstroObject Import
from AstroObject.AstroConfig import *

class Test_Configuration(object):
    """AstroObject.AstroConfig.Configuration"""
    
    def setUp(self):
        """docstring for setUp"""
        self.cfgA = {"Hi":{"A":1,"B":2,},}
        self.cfgB = {"Hi":{"A":3,"C":4,},}
        self.cfgC = {"Hi":{"A":3,"B":2,"C":4,},} #Should be a merge of A and B
        self.Class = Configuration
        
    def tearDown(self):
        """Remove junky files if they showed up"""
        self.remove("Test.yaml")
        self.remove("Test.dat")
    
    def remove(self,filename):
        """docstring for remove"""
        try:
            os.remove(filename)
        except:
            pass
    
    
    def test_init(self):
        """__init__"""
        cfg = self.Class(self.cfgC)
    
    def test_update(self):
        """update() deep updates"""
        cfg = self.Class(self.cfgA)
        cfg.update(self.cfgB)
        assert cfg == self.cfgC
    
        
    def test_merge(self):
        """merge() deep updates"""
        cfg = self.Class(self.cfgA)
        cfg.merge(self.cfgB)
        print self.cfgC
        assert cfg == self.cfgC
        
    def test_save(self):
        """save() writes yaml file or dat file"""
        cfg = self.Class(self.cfgC)
        cfg.save("Test.yaml")
        loaded = self.Class()
        loaded.load("Test.yaml")
        print self.cfgC, loaded
        assert self.cfgC == loaded.extract()
        cfg.save("Test.dat")
        
        
    def test_read(self):
        """load() reads a yaml file."""
        cfg = self.Class(self.cfgC)
        cfg.save("Test.yaml")
        cfg = self.Class()
        cfg.load("Test.yaml")
        print cfg, self.cfgC
        assert cfg == self.cfgC

class Test_DottedConfiguration(Test_Configuration):
    """AstroObject.AstroConfig.DottedConfiguration"""
    def setUp(self):
        """docstring for setUp"""
        self.cfgA = {"Hi":{"A":1,"B":2,"D":{"A":1},},}
        self.cfgB = {"Hi":{"A":3,"C":4,},}
        self.cfgC = {"Hi":{"A":3,"B":2,"C":4,"D":{"A":1},},} #Should be a merge of A and B
        self.Class = DottedConfiguration
    
    
    def test_dottedread(self):
        """access dotted configuration items"""
        cfg = self.Class(self.cfgA)
        assert 2 == cfg["Hi.B"]
        assert 1 == cfg["Hi.A"]
        assert 1 == cfg["Hi.D.A"]
        assert 1 == cfg["Hi"]["D"]["A"]
    
    @nt.raises(KeyError)
    def test_dottedread_nested(self):
        """access fails for nested dotted reads"""
        cfg = self.Class(self.cfgA)
        assert 1 == cfg["Hi.D.A"]
        assert 1 == cfg["Hi"]["D.A"]
        
    def test_dottedread_fixnest(self):
        """access succeeds for nested dotted reads after changing nesting mode."""
        cfg = self.Class(self.cfgA)
        assert 1 == cfg["Hi.D.A"]
        cfg.dn = DottedConfiguration
        assert cfg["Hi"]["D.A"] == 1
        

class Test_StructuredConfiguration(Test_DottedConfiguration):
    """AstroObject.AstroConfig.StructuredConfiguration"""
    def setUp(self):
        """docstring for setUp"""
        self.cfgA = {"Hi":{"A":1,"B":2,"D":{"A":1},},}
        self.cfgB = {"Hi":{"A":3,"C":4,},}
        self.cfgC = {"Hi":{"A":3,"B":2,"C":4,"D":{"A":1},},"Configurations":{"This":"AO.config.yaml"},} #Should be a merge of A and B
        self.Class = StructuredConfiguration
    
    def test_setFile(self):
        """setFile()"""
        cfg = self.Class(self.cfgC)
        cfg.setFile("Test.yaml")
        
    
    def test_save_included(self):
        """save() writes yaml file or dat file"""
        cfg = self.Class(self.cfgC)
        cfg.setFile("Test.yaml")
        cfg.save()
        loaded = self.Class()
        loaded.load("Test.yaml")
        assert self.cfgC == loaded.extract()
        cfg.save("Test.dat")
        assert os.access("Test.dat",os.F_OK)
        
        
    def test_read(self):
        """load() reads a yaml file."""
        cfg = self.Class(self.cfgC)
        cfg.save("Test.yaml")
        cfg = self.Class()
        cfg.load("Test.yaml")
        assert cfg == self.cfgC
    
                
