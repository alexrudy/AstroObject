# -*- coding: utf-8 -*-
# 
#  AstroObjectLogging.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-12-12.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.6.0
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
    AstroObject.AstroObjectLogging.AstroLogger
    :members:
    
.. autoclass::
    AstroObject.AstroObjectLogging.GrowlHandler
    :members:
    
.. autoclass::
    AstroObject.AstroObjectLogging.ConsoleFilter
    :members:
    
.. autoclass::
    AstroObject.AstroObjectLogging.RedirectionHandler
    :members:
    
.. autoclass::
    AstroObject.AstroObjectLogging.ManyTargetHandler
    :members:
    
"""
import logging
import logging.handlers as handlers

import math
import copy
import sys
import time
import os
import yaml
import collections

from .AstroConfig import StructuredConfiguration, DottedConfiguration
from logging import *
from .util import getVersion, ConfigurationError, update

__version__ = getVersion()
__libdebug__ = False # Toggles PRINTED debugger messages for this module, for dev purposes only.


levels = {"LIBDEBUG":2,"LIBINFO":5,"LIBWARN":8}
for name,lvl in levels.iteritems():
    logging.addLevelName(lvl,name)
    
def __dbg_print__(msg):
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
        __dbg_print__("-Filtering Console Active?:%s" % self.on)
        if self.on:
            return True
        else:
            self.messages.append(record)
            return False

class RedirectionHandler(logging.Handler):
    """docstring for ManyTargetHandler"""
    
    def __init__(self, *targets):
        super(RedirectionHandler, self).__init__()
        self._targets = []
        self._targets += list(*targets)

    def setTarget(self,target):
        """Add another target to the handler"""
        self._targets += [target]
                
    def handle(self,record):
        """Handle this record by redirecting"""
        if len(self._targets) > 0:
            for target in self._targets:
                if isinstance(target,(logging.Handler,logging.Logger)):
                    if record.levelno >= target.level:
                        target.handle(record)
                elif isinstance(target,str):
                    tlogger = logging.getLogger(target)
                    tlogger.handler(record)

    def close(self):
        """Close the handler"""
        super(RedirectionHandler, self).close()
        self._targets = []            

class ManyTargetHandler(handlers.MemoryHandler):
    """docstring for ManyTargetHandler"""
    def __init__(self, capacity, flushLevel=logging.ERROR, target=None, targets=None):
        super(ManyTargetHandler, self).__init__(capacity, flushLevel, target)
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
        __dbg_print__("Flushing Buffer")
        if len(self._targets) > 0:
            __dbg_print__( "Flushing %d to %r" % (len(self.buffer),self._targets))
            for record in self.buffer:
                for target in self._targets:
                    if record.levelno >= target.level:
                        __dbg_print__( "Flushing to %s" % target)
                        target.handle(record)
            self.buffer = []
        else:
            __dbg_print__( "WARNING: FLUSHING TO NO TARGET")
    
    def close(self):
        """Close the handler"""
        super(ManyTargetHandler, self).close()
        self._targets = []
        
_ConsoleFilter = ConsoleFilter()

class AstroLogger(logging.getLoggerClass()):
    """A customized logging class. This class is automatically used whenever you are using an AstroObject module elsewhere in your program. It subsumes other logging classes, regardless of the situation. This logger provides many specialized functions useful for logging, but can be used just like a normal logger. By default, the logger starts in buffering mode, collecting messages until it is configured. The configuration then allows it to write messages to the console and to a log file."""
    
    def __init__(self,name):
        super(AstroLogger,self).__init__(name)
        self.name = name
        __dbg_print__("--Starting %s" % self.name)
        self.configured = False
        self.handling = False
        self.buffering = False      
        self._config.dn = DottedConfiguration
        self._handlers = {}
        self._filters = {}
        self._filters["console"] = _ConsoleFilter
        __dbg_print__("Launched %s" % self.name)
    
    handlerClasses = {
        'growl' : GrowlHandler,
        'buffer': ManyTargetHandler,
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
            
    def configure_from_file(self,filename):
        """docstring for configure_from_file"""
        __dbg_print__( "--Configure %s " % self.name)
        
        self.configured |= self._config.load(filename)
                    
        if not self.configured:
            self.log(8,"No configuration provided or accessed. Using defaults.")
        __dbg_print__("--END Configure %s" % self.name)
        
    def configure(self,configuration=None):
        """Configure this logging object using a configuration dictionary. Configuration dictionaries can be provided by a YAML file or directly to the configuration argument. If both are provided, the YAML file will over-ride the explicit dictionary."""
        
        __dbg_print__( "--Configure %s " % self.name)
        
        # Configure from Variable
        if configuration != None:
            self._config.update(configuration)
            self.debug("Updated Configuration from variable")            
            self.configured |= True
        
        if not self.configured:
            self.log(8,"No configuration provided or accessed. Using defaults.")
        __dbg_print__("--END Configure %s" % self.name)
    
    def start(self):
        """Starts this logger running, using the configuration set using :meth:`configure`. The configuration can configure a file handler and a console handler. Arbitrary configurations are not possible at this point."""
        __dbg_print__( "--Starting Handlers in %s" % self.name)
        self.setup_handlers()
        if self.buffering:
            for key in self._handlers:
                if key is not 'buffer':
                    __dbg_print__("-Buffer Targeting %s in %s" % (key,self.name))
                    self._handlers['buffer'].setTarget(self._handlers[key])
            self._config["logging.buffer.enable"] = False
            self.setup_handler('buffer')
            self.buffering = False       
        __dbg_print__("--- LOG LEVEL %s %s" % (self.name, self.getEffectiveLevel()))
    
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
        
        # Short Circuit for options not taken.
        if not enable:
            if handler in self._handlers:
                hobject = self._handlers[handler]
                self.removeHandler(hobject)
                hobject.close()
                del self._handlers[handler]
                self.log(2,"Deactivating Handler %s: Deleted." % handler)
                # Flag that we aren't handling, if there are no handlers left.
                if len(self._handlers.keys()) == 0:
                    self.handling = False
                return
            else:
                self.log(2,"Deactivating Handler %s: Does not exist." % handler)
                return
        elif handler in self._handlers:
            self.log(2,"Activating Handler %s: Already active." % handler)
        else:
            # Create the handler object from the configuration
            if handler in self.handlerClasses:
                self._handlers[handler] = self.handlerClasses[handler](**hconfig)
            else:
                self._handlers[handler] = getattr(logging,handler)(**hconfig)
            self.log(2,"Activating Handler %s: Handler created" % handler)
        
        hobject = self._handlers[handler]
        # Set the level of the handler object
        if level is not None:
            hobject.setLevel(level)
            if level < self.level:
                self.setLevel(level)
        else:
            hobject.setLevel(self.level)
        self.log(2,"Setting Handler %s Level: %d" % (handler,hobject.level))    
        
        # Format the handler object
        if format is not None:
            formatter = logging.Formatter(fmt=format,datefmt=dateformat)
            hobject.setFormatter(formatter)
            self.log(2,"Applying Handler %s Formatter" % handler)
            
        # Apply a console filter if this handler passes to streams
        if isinstance(hobject,logging.StreamHandler) and hobject.stream == sys.stderr:
            hobject.addFilter(self._filters["console"])
            self.log(2,"Applying Handler %s Console Filter" % handler)
            
        # Enable and Activate the Handler
        self.addHandler(self._handlers[handler])
        self.handling = True
            
    def useConsole(self,use=None):
        """Turn on or off the console logging. Specify the parameter `use` to force console logging into one state or the other. If the `use` parameter is not given, console logging will be toggled."""
        if use is None:
            self._filters["console"].on = not self._filters["console"].on
        else:
            self._filters["console"].on = use
        __dbg_print__("Console is now: %s for %s" % (self._filters["console"].on,self.name))
        
    def init_buffer(self):
        """Sets up an initialization buffer"""
        self._config["logging.buffer.enable"] = True
        self.setup_handlers('buffer')
        self.setLevel(1)
        self.buffering = True

logging.setLoggerClass(AstroLogger)
logging.captureWarnings(True)
logging.getLogger('py.warnings').addHandler(RedirectionHandler(__name__))


from logging import *
