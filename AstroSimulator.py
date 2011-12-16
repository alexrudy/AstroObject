# 
#  AstroSimulator.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-12-14.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.3.0
# 

# Standard Scipy Toolkits
import numpy as np
import pyfits as pf
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt

# Matplolib Extras
import matplotlib.image as mpimage
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter

# Scipy Extras
from scipy import ndimage
from scipy.spatial.distance import cdist
from scipy.linalg import norm

# Standard Python Modules
import math, copy, sys, time, logging, os
import argparse

# Submodules from this system
from Utilities import *

__all__ = ["Simulator"]

__version__ = getVersion(__file__)

class Stage(object):
    """docstring for Stage"""
    def __init__(self,stage):
        super(Stage, self).__init__()
        self.do = stage

class Simulator(object):
    """A Simulator, used for running large segements of code with detailed logging and progress checking"""
    
    name = "Simulator"
    
    config = {
        "logging" : {
          "console" : {
              "enable" : True,
              "message" : "...%(message)s",
              "level" : None,
          },
          "file" : {
                'enable' : True,
                'format' : "%(asctime)s : %(levelname)-8s : %(module)-40s : %(funcName)-10s : %(message)s",
                'dateformat' : "%Y-%m-%d-%H:%M:%S",
                'filename' : "AstroObjectSim",
                'level' : None,
          },
        },
        "System" : {
            "Dirs" : {
                "Caches" : "Caches",
                "Logs" : "Logs/",
                "Partials" : "Partials",
                "Images" : "Images",
            },
            "Configs" : {
                "Main" : "Simulator.yaml"
            },
        },
    }
    
    def __init__(self,name="__class__.__name__",commandLine=True):
        super(Simulator, self).__init__()
        self.stages = {}
        self.orders = {}
        self.macros = {}
        self.name = name
        if name == "__class__.__name__":
            self.name = self.__class__.__name__
        self.log = logging.getLogger(__name__)
        # The following are boolean state values for the simulator
        self.configured = False
        self.logging = False
        self.running = False
        self.plotting = False
        self.debugging = False
        self.caching = True
        self.commandLine = commandLine
        
        if commandLine:
            self.initOptions()
        
    def initOptions(self):
        """Initializes the command line options for this script"""
        self.USAGE = "%(command)s %(basicOpts)s %(subcommand)s"
        self.USAGEFMT = { 'command' : os.path.basename(sys.argv[0]), 'basicOpts': "[ -E | -D | -T ]", 'subcommand' : "{macro}" }
        ShortHelp = "Command Line Interface for %(name)s" % { 'name': self.name }
        self.parser = argparse.ArgumentParser(description=ShortHelp,
            formatter_class=argparse.RawDescriptionHelpFormatter,usage=self.USAGE % self.USAGEFMT,prefix_chars="-+")
        
        self.parser.add_argument('-f',metavar='filename',type=str,dest='filename',
            help="filename for output image (without .fits)")
        # Add the basic controls for the script
        self.parser.add_argument('--version',action='version',version=__version__)
        
        # Operational Controls
        self.parser.add_argument('--do-plot',action='store_true',dest='plot',help="Enable debugging plots")
        self.parser.add_argument('--no-cache',action='store_false',dest='cache',
            help="ignore cached data from the simulator")
        self.parser.add_argument('-d','--debug',action='store_true',dest='debug',help="enable debugging messages and plots")
        
        # Config Commands
        self.parser.add_argument('--config',action='store',dest='config',type=str,help="use the specified configuration file",metavar="file.yaml")
        self.parser.add_argument('--dump-config',action='store_true',dest='dump',help=argparse.SUPPRESS)
                
        self.subparsers = self.parser.add_subparsers(title="macros",dest="command")
        
        self.subparsers.add_parser("all",help="Run all stages")
        
    def register(self,stage,name=None,description=None,position=None):
        """Adds a stage object to this simulator"""
        if self.running:
            return ConfigurationError("Cannot add a new stage to the simulator, the simulation has already started!")
        if position != None:
            position = len(self.stages)
        if name == None:
            raise ValueError("Stage must have a name")
        
        
        stageObject = Stage(stage)
        stageObject.name = name
        stageObject.description = description
        stageObject.order = position
        self.stages[name] = stageObject
        self.parser.add_argument("+"+name,action='append_const',dest='include',const=name,help=argparse.SUPPRESS)
        self.parser.add_argument("-"+name,action='append_const',dest='exclude',const=name,help=argparse.SUPPRESS)
        
    def addMacro(self,name,*stages,**kwargs):
        """Adds a new macro to the simulation"""
        self.subparsers.add_parser(name,**kwargs)
        self.macros[name] = list(*stages)
        
    def configure(self,configFile=None,configuration=None):
        """Configure this logging object"""
        if self.running:
            return ConfigurationError("Cannot add a new stage to the simulator, the simulation has already started!")
        if self.configured:
            raise ConfigurationError("%s appears to be already configured" % (self.name))
        # Configure from Variable
        if configuration != None:
            self.config = update(self.config,configuration)
            self.log.debug("Updated Configuration from variable")            
            self.configured |= True
        # Configure from File
        if configFile != None:
            try:
                with open(configFile,'r') as stream:
                    loaded = yaml.load(stream)
                    self.config = update(self.config,loaded)
            except IOError as e:
                self.log.warning("Couldn't load Configuration File %s" % configFile)
            else:
                self.configured |= True
        
        if not self.configured:
            self.log.log(8,"No configuration provided or accessed. Using defaults.")
        self.log.configure(configuration=self.config)
        self.log.start()
    
    def parseArguments(self):
        """Parse arguments, and pre-apply appropriate values to configuration"""
        Namespace = self.parser.parse_args()
        self.options = vars(Namespace)
    
    def pre_applyArguments(self):
        """Apply arguments before configure"""
        if "config" in self.options and self.options["config"] != None:
            self.config["System"]["Configs"]["Main"] = self.options["config"]
    
    def post_applyArguments(self):
        """Apply post-arguments"""
        pass
    
    def startup(self):
        """Basic actions for simulator startup"""
        if self.commandLine:
            self.parseArguments()
            self.pre_applyArguments
        self.configure(configFile=self.config["System"]["Configs"]["Main"])
        if self.commandLine:
            self.post_applyArguments()
        
    def run(self):
        """Run the actual simulator"""
        self.startup()
        self.running = True
        
        
        