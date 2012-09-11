# -*- coding: utf-8 -*-
# 
#  Test_AstroObjectLogging.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-12-29.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.5.3-p1
# 


import AstroObject.AstroObjectLogging as AOLogging
import logging,logging.handlers
import nose.tools as nt
from nose.plugins.skip import Skip,SkipTest
import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
import os

class test_Logger(object):
    """AstroObjectLogging.LogManager"""
    
    def test_LoggerInit(self):
        """logging.getLogger(__name__)"""
        log = logging.getLogger(__name__+".init")
        assert isinstance(log,AOLogging.AstroLogger)
        assert not log.configured
        assert log.getEffectiveLevel() == 0
        assert not log.config["logging"]["file"]["enable"]
    
    def test_configure(self):
        """configure() success"""
        log = logging.getLogger(__name__+".configure")
        log.configure()
        assert not log.configured
        log.configure(configuration={'logging':{'file':{'level':20}}})
        assert log.config["logging"]["file"]["level"] == 20
        assert log.configured
        
    def test_configure_twice(self):
        """configure() twice"""
        log = logging.getLogger(__name__+".configure+failure")
        log.configure()
        assert not log.configured
        log.configure(configuration={'logging':{'file':{'level':20}}})
        assert log.configured
        log.configure(configuration={'logging':{'file':{'level':20}}})
        
    def test_start(self):
        """start() success"""
        log = logging.getLogger(__name__+".start")
        log.configure(configuration={'logging':{'file':{'level':10}}})
        log.start()
    
    def test_start_failure(self):
        """start() failure"""
        log = logging.getLogger(__name__+".start+failure")
        log.configure(configuration={'logging':{'file':{'level':10}}})
        log.start()
        log.start()
        
        
        
        
