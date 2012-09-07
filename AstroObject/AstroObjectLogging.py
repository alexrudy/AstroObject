# -*- coding: utf-8 -*-
# 
#  AstroObjectLogging.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-12-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.5.2
#
"""
:mod:`AstroObjectLogging` — Structured Configuration Logging 
============================================================

This module provides basic access to logging functions. It elimiates much of the variablity in logging, replacing it with the simple logging configuration options that AstroObject is constantly using. It is, however, built on the normal logging module, and so shouldn't break any other logging schemes. <http://docs.python.org/library/logging.html>

Other than a simpler set of possible configuration options, this object has the advantage that it allows for dynamic configurations which vary from run to run. As is common in complex programs, a lot happens before reading a configuration file. However, without the configuration file, the system can't start logging. This logger holds all the messages it recieves pre-configuration for use once the logger starts, preserving these messages for later debugging.

To use the logging::
	
	LOG = logging.getLogger(__name__)
	LOG.info(u"Buffered Message Saved for later output")
	LOG.configure(configFile="some.yaml")
	LOG.info(u"Buffered Message, saved for later output")
	LOG.start()
	LOG.info(u"Normal Message")
	LOG.useConsole(False)
	LOG.info(u"Not on the console")
	LOG.useConsole(True)
	LOG.info(u"Back to the console!")
	

.. autoclass::
    AstroObject.AstroObjectLogging.LogManager
    :members:
    
.. autoclass::
    AstroObject.AstroObjectLogging.GrowlHandler
    :members:

"""
import logging
import logging.handlers as handlers

import math, copy, sys, time, os
import yaml

from Utilities import *
from .AstroConfig import StructuredConfiguration, DottedConfiguration
from logging import *

__version__ = getVersion()
__libdebug__ = False # Toggles PRINTED debugger messages for this module, for dev purposes only.

logging.captureWarnings(True)

levels = {"LIBDEBUG":2,"LIBINFO":5,"LIBWARN":8}
for name,lvl in levels.iteritems():
    logging.addLevelName(lvl,name)
    
def _ldbprint(msg):
    """Print statements for debugging mode."""
    if __libdebug__:
        print msg
    return

class GrowlHandler(logging.Handler):
    """Handler that emits growl notifications using the gntp module.
    
    Growl notifications are displayed by the growl framework application on desktop computers. They can also be sent over a network to notify a remote host. This logger turns log messages into growl notifications."""
    def __init__(self,name=None):
        super(GrowlHandler, self).__init__()
        self.name = name
        if self.name == None:
            self.name = "AstroObject"
        try:
            import gntp
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
            logging.ERROR:"%s Error" % self.name,
            }
        
    
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

class ConsoleFilter(logging.Filter):
    """A simple filter to control console-based output."""
    def __init__(self, on=True):
        super(ConsoleFilter, self).__init__()
        self.on = on
        self.messages = []
        
    def filter(self,record):
        """Filter this record based on whether the console is on."""
        _ldbprint("-Filtering Console Active?:%s" % self.on)
        if self.on:
            return True
        else:
            self.messages.append(record)
            return False
            
class ManyTargetBuffer(handlers.MemoryHandler):
    """docstring for ManyTargetBuffer"""
    def __init__(self, capacity, flushLevel=logging.ERROR, target=None, targets=None):
        super(ManyTargetBuffer, self).__init__(capacity, flushLevel, target)
        if isinstance(self.target,logging.Handler):
            self._targets = [self.target]
        else:
            self._targets = []
        if isinstance(targets,list):
            self._targets += targets

    def setTarget(self,target):
        """Add another target to the handler"""
        if isinstance(target,logging.Handler):
            self._targets += [target]
                
    def flush(self):
        """Flush out this handler"""
        _ldbprint("Flushing Buffer")
        if len(self._targets) > 0:
            _ldbprint( "Flushing %d to %r" % (len(self.buffer),self._targets))
            for record in self.buffer:
                for target in self._targets:
                    if record.levelno >= target.level:
                        _ldbprint( "Flushing to %s" % target)
                        target.handle(record)
            self.buffer = []
        else:
            _ldbprint( "WARNING: FLUSHING TO NO TARGET")
    
    def close(self):
        """Close the handler"""
        super(ManyTargetBuffer, self).close()
        self._targets = None
        
        

class LogManager(logging.getLoggerClass()):
    """A customized logging class. This class is automatically used whenever you are using an AstroObject module elsewhere in your program. It subsumes other logging classes, regardless of the situation. This logger provides many specialized functions useful for logging, but can be used just like a normal logger. By default, the logger starts in buffering mode, collecting messages until it is configured. The configuration then allows it to write messages to the console and to a log file."""
    
    def __init__(self,name):
        super(LogManager,self).__init__(name)
        self.name = name
        _ldbprint("--Starting %s" % self.name)
        self.configured = False
        self.running = False
        self.handling = False
        self.doConsole = False        
        self.messages = {}
        self._handlers = {}
        self._filters = {}
        self._filters["console"] = ConsoleFilter()
        self._other_loggers = []
        self.setLevel(1)        
        self._config.dn = DottedConfiguration
        self._config["logging.buffer.enable"] = True
        self.setup_handlers()
        self.running = True
        _ldbprint("Launched %s" % self.name)
    
    handlerClasses = {
        'growl' : GrowlHandler,
        'buffer': ManyTargetBuffer,
        'null'  : logging.NullHandler,
        'file'  : handlers.TimedRotatingFileHandler,
        'console' : logging.StreamHandler,
        'simple-file' : logging.FileHandler,
    }
    _config = StructuredConfiguration({
                'logging' : {
                    'buffer'  : {
                        'capacity': 1.0e6,
                        'enable' : False,
                    },
                    'null' : {
                        'enable' : False,
                    },
                    'growl' : {
                        'enable' : False,
                        'level'  : None,
                        'name' : "AstroObject",
                    },
                    'file' : {
                        'enable' : False,
                        'format' : "%(asctime)s : %(levelname)-8s : %(module)-15s : %(funcName)-10s : %(message)s",
                        'dateformat' : "%H:%M:%S",
                        'filename' : __name__,
                        'level' : None,
                        'when'  : 'midnight'
                    },
                    'console': {
                        'enable' : False,
                        'format' : "...%(message)s",
                        'level' : None,
                    },
                },
                    'Dirs': {
                        'Logs' : "Logs"
                    },
            })
    
    @property
    def config(self):
        """A read only element that is the configuration for this system."""
        return StructuredConfiguration(self._config.store)
            
    def configure(self,configFile=None,configuration=None,filters=None):
        """Configure this logging object using a configuration dictionary. Configuration dictionaries can be provided by a YAML file or directly to the configuration argument. If both are provided, the YAML file will over-ride the explicit dictionary."""
        
        _ldbprint( "--Configure %s " % self.name)
        
        # Configure from Variable
        if configuration != None:
            self._config.update(configuration)
            self.debug("Updated Configuration from variable")            
            self.configured |= True
        
        # Configure from File
        if configFile != None:
            self.debug("Updated Configuration from file")            
            self.configured |= self._config.load(configFile)
        
        # Configure from configuration
        self.debug("Updated Configuration from structure")            
        self.configured |= self._config.load()
        
        if filters is not None:
            self._filters = filters
        
        if not self.configured:
            self.log(8,"No configuration provided or accessed. Using defaults.")
        _ldbprint("--END Configure %s" % self.name)
    
    def start(self):
        """Starts this logger running, using the configuration set using :meth:`configure`. The configuration can configure a file handler and a console handler. Arbitrary configurations are not possible at this point."""
        _ldbprint( "--Starting Handlers in %s" % self.name)
        self.setup_handlers()
        if 'buffer' in self._handlers:
            for key in self._handlers:
                if key is not 'buffer':
                    _ldbprint("-Buffer Targeting %s in %s" % (key,self.name))
                    self._handlers['buffer'].setTarget(self._handlers[key])
        
            self._config["logging.buffer.enable"] = False
            self.setup_handler('buffer')
        if len(self._other_loggers) > 0:
            self.start_others(*self._other_loggers)
            
        _ldbprint("--- LOG LEVEL %s %s" % (self.name, self.getEffectiveLevel()))
    
    def setup_handlers(self,*handlers):
        """Sets up the handlers based on the configuration"""
        if len(handlers) == 0:
            handlers = self._config["logging"]
        for handler in handlers:
            self.setup_handler(handler)
            
            
    def setup_handler(self,handler):
        """docstring for setup_handler"""
        # Extract Handler setup information
        hconfig = DottedConfiguration(copy.deepcopy(self._config["logging"][handler].store))
        # Set up configuration variables
        enable = hconfig.pop('enable',False)
        level = hconfig.pop('level',None)
        format = hconfig.pop('format',None)
        dateformat = hconfig.pop('dateformat',None)
            
        if "filename" in hconfig:
            if not os.path.exists(self._config["Dirs.Logs"]):
                enable = False
            hconfig["filename"] = "%(Logs)s/%(filename)s.log" % dict(filename=hconfig["filename"],**self._config["Dirs"])
            _ldbprint("Set handler filename %s for %s in %s" % (hconfig["filename"],handler,self.name))
                
        # Create the handler object from the configuration
        if not ( handler in self._handlers and self._handlers[handler].enabled ) and enable:
            if handler in self.handlerClasses:
                self._handlers[handler] = self.handlerClasses[handler](**hconfig)
            else:
                self._handlers[handler] = getattr(logging,handler)(**hconfig)
            self._handlers[handler].enabled = False
            _ldbprint("-Created %s in %s"  % (handler,self.name))
        elif (handler not in self._handlers) and (not enable):
            _ldbprint("-Skipping Handler %s in %s"  % (handler,self.name))
            return
            
        # Set the level of the handler object
        if level is not None:
            self._handlers[handler].setLevel(level)
        else:
            self._handlers[handler].setLevel(self.level)
        _ldbprint("Handler %s's level is %s in %s" % (handler,self._handlers[handler].level,self.name))    
        
        # Format the handler object
        if format is not None:
            formatter = logging.Formatter(fmt=format,datefmt=dateformat)
            self._handlers[handler].setFormatter(formatter)
            
        # Apply a console filter if this handler passes to streams
        if isinstance(self._handlers[handler],logging.StreamHandler) and self._handlers[handler].stream == sys.stderr:
            self._handlers[handler].addFilter(self._filters["console"])
            
        # Enable and Activate the Handler
        if enable and not self._handlers[handler].enabled:
            self.addHandler(self._handlers[handler])
            self.handling = True
            _ldbprint("Set up and enabled %s in %s" % (handler,self.name))
            self._handlers[handler].enabled = enable
        elif (not enable) and self._handlers[handler].enabled:
            self.removeHandler(self._handlers[handler])
            self._handlers[handler].flush()
            self._handlers[handler].enabled = enable
            del self._handlers[handler]
            if len(self._handlers) == 0:
                self.handling = False
            _ldbprint("Deleted %s in %s" % (handler,self.name))
        else:
            _ldbprint("No status change to %s in %s" % (handler,self.name))
            self._handlers[handler].enabled = enable
        
    def configure_others(self,*loggers):
        """Configure other loggers"""
        if len(loggers) == 0:
            loggers = ['root']
        for logger in loggers:
            log_object = logging.getLogger(logger)
            log_object.configure(configuration = self.config, filters = self._filters)
        if not self.handling:
            self._other_loggers += loggers
    
    def start_others(self,*loggers):
        """docstring for start_others"""
        if len(loggers) == 0:
            loggers = ['root']
        for logger in loggers:
            log_object = logging.getLogger(logger)
            log_object.configure(configuration = self.config)
            
    def useConsole(self,use=None):
        """Turn on or off the console logging. Specify the parameter `use` to force console logging into one state or the other. If the `use` parameter is not given, console logging will be toggled."""
        if use is None:
            self._filters["console"].on = not self._filters["console"].on
        else:
            self._filters["console"].on = use
        _ldbprint("Console is now: %s for %s" % (self._filters["console"].on,self.name))

logging.setLoggerClass(LogManager)

