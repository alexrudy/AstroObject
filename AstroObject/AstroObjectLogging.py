# 
#  AstroObjectLogging.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-12-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.3.0a2
#

import logging
import logging.handlers as handlers

import math, copy, sys, time, os

from Utilities import *

__version__ = getVersion()

logging.captureWarnings(True)

levels = {"LIBDEBUG":2,"LIBINFO":5,"LIBWARN":8}
for name,lvl in levels.iteritems():
    logging.addLevelName(lvl,name)



class LogManager(logging.getLoggerClass()):
    """The logging class which handles the log messages. It handles its own limited configuration, and buffers messages before it starts, so that early messages are still written to a file."""
    def __init__(self,name):
        super(LogManager,self).__init__(name)
        self.name = name
        self.configured = False
        self.running = False
        self.handling = False
        self.doConsole = False
        self.level = False
        self.setLevel(1)
        self.initialize()
    
    def initialize(self):
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
                    'file' : {
                        'enable' : True,
                        'format' : "%(asctime)s : %(levelname)-8s : %(module)-40s : %(funcName)-10s : %(message)s",
                        'dateformat' : "%Y-%m-%d-%H:%M:%S",
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
        """Configure this logging object. The configuration happens from a file (`configFile`) and then from an object `configuration`. As such, values in the object will override values from the file, and both will override the defaults. The default settings place messages in a file called AstroObject.log in the Logs/ folder."""
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
                self.warning("Couldn't load Configuration File %s" % configFile)
            else:
                self.configured |= True
        
        if not self.configured:
            self.log(8,"No configuration provided or accessed. Using defaults.")
    
    def start(self):
        """Starts this logger outputing, based on the configuration. It is recommended that you call :meth:`configure` first."""
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
        self.logfolder = self.config["Dirs"]["Logs"]
        
        # Only set up the file log handler if we can actually access the folder
        if os.access(self.logfolder,os.F_OK):
            filename = self.config["Dirs"]["Logs"] + self.config["logging"]["file"]["filename"]+".log"
            
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
