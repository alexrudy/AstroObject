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

def update(d, u):
    """A deep update command for dictionaries.
    This is because the normal dictionary.update() command does not handle nested dictionaries."""
    if len(u)==0:
        return d
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

class LogManager(logging.getLoggerClass()):
    
    def initialize(self):
        """Initializes this logger to buffer"""
        self.buffer = handlers.MemoryHandler(1e6)
        self.buffer.setLevel(logging.NOTSET)
        logging.captureWarnings(True)
        self.addHandler(self.buffer)
        
        self.level = logging.INFO
    
    def _configure(self):
        """Configure this logging object"""
        self.config = {
            'logging' : {
                'file' : {
                    'enable' : True,
                    'format' : "%(asctime)s : %(levelname)-8s : %(funcName)-20s : %(message)s",
                    'filename' : "SED",
                },
                'console': {
                    'enable' : False,
                    'format' : "...%(message)s"
                },
            },
        }
        
        try:
            with open(self.configFileName,'r') as stream:
                loaded = yaml.load(stream)
                self.config = update(self.config,loaded)
        except IOError as e:
            self.log.warning("Couldn't load Configuration File %s" % self.configFileName)
    
    def start(self):
        """Starts this logger outputing"""
        
        # Setup the Console Log Handler
        self.console = logging.StreamHandler()    
        consoleFormatter = logging.Formatter(self.config["logging"]["console"]["format"])
        self.console.setFormatter(consoleFormatter)
        
        if self.config["logging"]["console"]["level"]:
            self.console.setLevel(self.config["logging"]["console"]["level"])
        elif self.level:
            self.console.setLevel(self.level)

        if self.config["System"]["logging"]["console"]["enable"]:
            self.log.addHandler(self.console)
            self.consolebuffer.setTarget(self.console)
        
        self.consolebuffer.close()
        self.log.removeHandler(self.consolebuffer)

        self.logfile = None
        # Only set up the file log handler if we can actually access the folder
        if os.access(self.config["System"]["Dirs"]["Logs"],os.F_OK) and self.config["System"]["logging"]["file"]["enable"]:
            filename = self.config["System"]["Dirs"]["Logs"] + self.config["System"]["logging"]["file"]["filename"]+".log"
            self.logfile = logging.handlers.TimedRotatingFileHandler(filename=filename,when='midnight')
            self.logfile.setLevel(logging.DEBUG)
            fileformatter = logging.Formatter(self.config["System"]["logging"]["file"]["format"],datefmt="%Y-%m-%d-%H:%M:%S")
            self.logfile.setFormatter(fileformatter)
            self.log.addHandler(self.logfile)
            # Finally, we should flush the old buffers
            self.filebuffer.setTarget(self.logfile)

        self.filebuffer.close()
        self.log.removeHandler(self.filebuffer)
        self.log.debug("Configured Logging")
