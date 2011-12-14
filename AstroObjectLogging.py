# 
#  AstroObjectLogging.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-12-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.2.4
#

import logging
import logging.handlers as handlers

import math, copy, sys, time, os

from Utilities import *

logging.captureWarnings(True)

levels = {"LIBDEBUG":2,"LIBINFO":5,"LIBWARN":8}
for name,lvl in levels.iteritems():
    logging.addLevelName(lvl,name)



class LogManager(logging.getLoggerClass()):
    
    def __init__(self,name):
        super(LogManager,self).__init__(name)
        self.configured = False
        self.running = False
        self.handling = False
        self.level = False
        self.initCustomLevels()
        self.initialize()
    
    def initCustomLevels(self):
        """Initializes the module level custom level functions as shortcuts"""
        for name,lvl in levels.iteritems():
            def log(*args):
                self.log(lvl,*args)
            setattr(self,name.lower(),log)
    
    def initialize(self):
        """Initializes this logger to buffer"""
        if self.handling:
            raise ConfigurationError("Logger appears to be already handling messages")
        if self.running:
            raise ConfigurationError("Logger seems to already have started")
        if self.configured:
            raise ConfigurationError("Logger appears to be already configured")
        
        self.buffer = handlers.MemoryHandler(1e6)
        self.addHandler(self.buffer)

        self.libdebug("Logging Started")
        self.running = True
    
    config = {
                'logging' : {
                    'file' : {
                        'enable' : True,
                        'format' : "%(asctime)s : %(levelname)-8s : %(funcName)-20s : %(message)s",
                        'dateformat' : "%Y-%m-%d-%H:%M:%S",
                        'filename' : "AstroObject",
                        'level' : None,
                    },
                    'console': {
                        'enable' : True,
                        'format' : "...%(message)s",
                        'level' : None,
                    },
                },
                'System' : {
                    'Dirs': {
                        'Logs' : "Logs/"
                    },
                },
            }
    
    def configure(self,configFile=None,configuration=None):
        """Configure this logging object"""
        if self.configured:
            raise ConfigurationError("Logger appears to be already configured")
        if self.handling:
            raise ConfigurationError("Logger appears to be already handling")
        # Configure from Variable
        if configuration != None:
            self.config = update(self.config,configuration)
            self.debug("Updated Configuration from variable")            
            self.configured |= True
        # Configure from File
        if configFile != None:
            try:
                with open(configFile,'r') as stream:
                    loaded = yaml.load(stream)
                    self.config = update(self.config,loaded)
            except IOError as e:
                self.warning("Couldn't load Configuration File %s" % self.configFileName)
            else:
                self.configured |= True
        
        if not self.configured:
            self.libwarn("No configuration provided or accessed. Using defaults.")
    
    def start(self):
        """Starts this logger outputing"""
        if self.handling:
            raise ConfigurationError("Logger appears to be already handling messages")
        if not self.running:
            raise ConfigurationError("Logger appears to not be running. This should never happen")
        if not self.configured:
            self.libwarn("Logger appears not to be configured")
        
        # Setup the Console Log Handler
        self.console = logging.StreamHandler()    
        consoleFormatter = logging.Formatter(self.config["logging"]["console"]["format"])
        self.console.setFormatter(consoleFormatter)
        
        if self.config["logging"]["console"]["level"]:
            self.console.setLevel(self.config["logging"]["console"]["level"])
        elif self.level:
            self.console.setLevel(self.level)

        if self.config["logging"]["console"]["enable"]:
            self.addHandler(self.console)
            self.handling |= True
        
        self.logfile = None
        self.logfolder = self.config["System"]["Dirs"]["Logs"]
        
        # Only set up the file log handler if we can actually access the folder
        if os.access(self.logfolder,os.F_OK):
            
            filename = self.config["System"]["Dirs"]["Logs"] + self.config["logging"]["file"]["filename"]+".log"
            
            self.logfile = logging.handlers.TimedRotatingFileHandler(filename=filename,when='midnight')
            fileformatter = logging.Formatter(self.config["logging"]["file"]["format"],datefmt=self.config["logging"]["file"]["dateformat"])
            self.logfile.setFormatter(fileformatter)
            
            if self.config["logging"]["file"]["level"]:
                self.console.setLevel(self.config["logging"]["file"]["level"])
            elif self.level:
                self.console.setLevel(self.level)
                        
            if self.config["logging"]["file"]["enable"]:
            
                self.addHandler(self.logfile)
                # Finally, we should flush the old buffers
                self.buffer.setTarget(self.logfile)
                self.handling |= True
        
        self.removeHandler(self.buffer)
        self.buffer.close()
        if self.handling:
            self.libdebug("Configured Logging")

logging.setLoggerClass(LogManager)