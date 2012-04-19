# -*- coding: utf-8 -*-
# 
#  AstroObjectLogging.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-12-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.5-a1
#
"""
Easy Logging :mod:`AstroObjectLogging`
======================================

This module provides basic access to logging functions. It elimiates much of the variablity in logging, replacing it with the simple logging configuration options that AstroObject is constantly using. It is, however, built on the normal logging module, and so shouldn't break any other logging schemes. <http://docs.python.org/library/logging.html>

Other than a simpler set of possible configuration options, this object has the advantage that it allows for dynamic configurations which vary from run to run. As is common in complex programs, a lot happens before reading a configuration file. However, without the configuration file, the system can't start logging. This logger holds all the messages it recieves pre-configuration for use once the logger starts, preserving these messages for later debugging.

To use the logging::
	
	LOG = logging.getLogger(__name__)
	LOG.info("Buffered Message Saved for later output")
	LOG.configure(configFile="some.yaml")
	LOG.info("Buffered Message, saved for later output")
	LOG.start()
	LOG.info("Normal Message")
	LOG.useConsole(False)
	LOG.info("Not on the console")
	LOG.useConsole(True)
	LOG.info("Back to the console!")
	

.. autoclass::
    AstroObject.AstroObjectLogging.LogManager
    :members:

"""
import logging
import logging.handlers as handlers

import math, copy, sys, time, os
import yaml

from Utilities import *

__version__ = getVersion()

logging.captureWarnings(True)

levels = {"LIBDEBUG":2,"LIBINFO":5,"LIBWARN":8}
for name,lvl in levels.iteritems():
    logging.addLevelName(lvl,name)

class GrowlHandler(logging.Handler):
    """Handler that emits growl notifications"""
    def __init__(self,name=None):
        super(GrowlHandler, self).__init__()
        self.name = name
        if self.name == None:
            self.name = "AstroObject"
        try:
            import gntp.notifier
            self.gntp = gntp
        except ImportError as e:
            self.disable = True
            self.notifier = None
        else:
            self.disable = False
            self.notifier = self.gntp.notifier.GrowlNotifier(
                applicationName=self.name,
                notifications=["Info Message","Warning Message","Critical Message","Error Message","Debug Message"],
                defaultNotifications=["Info Message","Warning Message","Critical Message","Error Message"],
            )
            self.notifier.register()
        self.titles = {
            logging.DEBUG:"%s Debug" % self.name,
            logging.INFO:"%s Info" % self.name,
            logging.WARNING:"%s Warning" % self.name,
            logging.CRITICAL:"%s Critical" % self.name,
            logging.ERROR:"%s Error" % self.name}
        
    
    mapping = {logging.DEBUG:"Debug Message",logging.INFO:"Info Message",logging.WARNING:"Warning Message",logging.CRITICAL:"Critical Message",logging.ERROR:"Error Message"}

    
    
    def emit(self,record):
        """Emits a growl notification"""
        if self.disable:
            return
        try:
            msg = self.format(record)
            self.notifier.notify(
                noteType = self.mapping[record.levelno],
                title = self.titles[record.levelno],
                description = msg,
                sticky = False,
                priority = 1,
            )
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

        

class LogManager(logging.getLoggerClass()):
    """A customized logging class. This class is automatically used whenever you are using an AstroObject module elsewhere in your program. It subsumes other logging classes, regardless of the situation. This logger provides many specialized functions useful for logging, but can be used just like a normal logger. By default, the logger starts in buffering mode, collecting messages until it is configured. The configuration then allows it to write messages to the console and to a log file."""
    def __init__(self,name):
        super(LogManager,self).__init__(name)
        self.name = name
        self.configured = False
        self.running = False
        self.handling = False
        self.doConsole = False
        self.level = False
        self.setLevel(1)
        self._initialize()
    
    def _initialize(self):
        """Initializes this logger to buffer messages it receives before it is configured. This initialization is automatically handled when the :class:`LogManager` is created."""
        if self.handling:
            raise ConfigurationError("Logger appears to be already handling messages")
        if self.running:
            raise ConfigurationError("Logger seems to already have started")
        if self.configured:
            raise ConfigurationError("Logger appears to be already configured")
        
        self.buffer = handlers.MemoryHandler(1e6)
        self.buffer.setLevel(0)
        self.addHandler(self.buffer)
        
        self.null = logging.NullHandler()
        
        self.running = True
    
    config = {
                'logging' : {
                    'growl' : {
                        'enable' : False,
                        'level'  : None,
                        'name' : "AstroObject",
                    },
                    'file' : {
                        'enable' : True,
                        'format' : "%(asctime)s : %(levelname)-8s : %(module)-15s : %(funcName)-10s : %(message)s",
                        'dateformat' : "%H:%M:%S",
                        'filename' : "AstroObject",
                        'level' : None,
                    },
                    'console': {
                        'enable' : False,
                        'format' : "...%(message)s",
                        'level' : None,
                    },
                },
                    'Dirs': {
                        'Logs' : "Logs/"
                    },
            }
    
    def configure(self,configFile=None,configuration=None):
        """Configure this logging object using a configuration dictionary. Configuration dictionaries can be provided by a YAML file or directly to the configuration argument. If both are provided, the YAML file will over-ride the explicit dictionary."""
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
                self.warning("Couldn't load Configuration File %s" % configFile)
                self.configured |= False
            else:
                self.configured |= True
        
        if not self.configured:
            self.log(8,"No configuration provided or accessed. Using defaults.")
    
    def start(self):
        """Starts this logger running, using the configuration set using :meth:`configure`. The configuration can configure a file handler and a console handler. Arbitrary configurations are not possible at this point."""
        if self.handling:
            raise ConfigurationError("Logger appears to be already handling messages")
        if not self.running:
            raise ConfigurationError("Logger appears to not be running. This should never happen")
        if not self.configured:
            self.log(8,"Logger appears not to be configured")
        
        # Setup the Console Log Handler
        self.console = logging.StreamHandler()    
        consoleFormatter = logging.Formatter(self.config["logging"]["console"]["format"])
        self.console.setFormatter(consoleFormatter)
        
        if self.config["logging"]["console"]["level"]:
            self.console.setLevel(self.config["logging"]["console"]["level"])
        elif self.level:
            self.console.setLevel(self.level)

        if self.config["logging"]["console"]["enable"] and not self.doConsole:
            self.addHandler(self.console)
            self.handling |= True
        
        self.logfile = None
        self.logfolder = self.config["Dirs"]["Logs"]+"/"
        
        # Only set up the file log handler if we can actually access the folder
        if os.access(self.logfolder,os.F_OK):
            filename = "%(dir)s/%(name)s.log" % {'dir':self.config["Dirs"]["Logs"],'name':self.config["logging"]["file"]["filename"]}
            
            self.logfile = logging.handlers.TimedRotatingFileHandler(filename=filename,when='midnight')
            fileformatter = logging.Formatter(self.config["logging"]["file"]["format"],datefmt=self.config["logging"]["file"]["dateformat"])
            self.logfile.setFormatter(fileformatter)
            
            if self.config["logging"]["file"]["level"]:
                self.logfile.setLevel(self.config["logging"]["file"]["level"])
            elif self.level:
                self.logfile.setLevel(self.level)
                        
            if self.config["logging"]["file"]["enable"]:
            
                self.addHandler(self.logfile)
                # Finally, we should flush the old buffers
                self.buffer.setTarget(self.logfile)
                self.handling |= True
        
        if self.config["logging"]["growl"]["enable"]:
            self.growlHandler = GrowlHandler(name=self.config["logging"]["growl"]["name"])
            if self.growlHandler.disable:
                self.config["logging"]["growl"]["enable"] = False
            else:
                if self.config["logging"]["file"]["level"]:
                    self.growlHandler.setLevel(self.config["logging"]["file"]["level"])
                elif self.level:
                    self.growlHandler.setLevel(logging.INFO)
                self.addHandler(self.growlHandler)
                self.handling |= True
                
        
        self.removeHandler(self.buffer)
        self.buffer.flush()
        if not self.handling:
            self.addHandler(self.null)
            self.log(8,"Logger not actually handling anything!")
            
    def useConsole(self,use=None):
        """Turn on or off the console logging. Specify the parameter `use` to force console logging into one state or the other. If the `use` parameter is not given, console logging will be toggled."""
        if use != None:
            # THIS SHOULD BE BACKWARDS
            # If we turn the console on now, then this very function will turn it off in a minute!
            self.doConsole = not use
        if not self.handling:
            self.log(8,"Logger appears to not already be handling messages")
        if not self.running:
            raise ConfigurationError("Logger appears to not be running. This should never happen")
        if not self.config["logging"]["console"]["enable"]:
            return
        if self.doConsole:
            self.removeHandler(self.console)
            self.doConsole = False
        else:
            self.addHandler(self.console)
            self.doConsole = True

logging.setLoggerClass(LogManager)
