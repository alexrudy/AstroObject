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
    def __init__(self,stage,name="a Stage",description="A description",order=0,exceptions=None):
        super(Stage, self).__init__()
        self.do = stage
        if exceptions == None:
            self.exceptions = tuple()
        else:
            self.exceptions = exceptions
        self.name = name
        self.description = description
        self.order = order

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
        self.mparse = {}
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
        self.starting = False
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
        self.subparsers.add_parser("none",help="Macro to run no stages",description="Explicitly use 'none' and +stage to only run a specific stage")
        
    def register(self,stage,name=None,description=None,position=None,exceptions=None):
        """Adds a stage object to this simulator"""
        if self.running or self.starting:
            raise ConfigurationError("Cannot add a new stage to the simulator, the simulation has already started!")
        if position == None:
            position = len(self.stages)
        if name == None:
            raise ValueError("Stage must have a name")
        if position in self.orders:
            raise ValueError("Cannot dupilcate position ordering")
        if description == None:
            description = name
        if exceptions == None:
            exceptions = tuple()
        
        stageObject = Stage(stage,name=name,description=description,order=position,exceptions=exceptions)
        self.stages[name] = stageObject
        self.orders[position] = name
        self.parser.add_argument("+"+name,action='append_const',dest='include',const=name,help=argparse.SUPPRESS)
        self.parser.add_argument("-"+name,action='append_const',dest='exclude',const=name,help=argparse.SUPPRESS)
        
    def addMacro(self,name,*stages,**kwargs):
        """Adds a new macro to the simulation"""
        if self.running or self.starting:
            raise ConfigureError("Cannot add macro after simulator has started!")
            
        self.mparse[name] = self.subparsers.add_parser(name,**kwargs)
        self.macros[name] = list(stages)
        
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
        if "exclude" not in self.options or not isinstance(self.options["exclude"],list):
            self.options["exclude"] = []
        if "include" not in self.options or not isinstance(self.options["include"],list):
            self.options["include"] = []
        
    
    def post_applyArguments(self):
        """Apply post-arguments"""
        self.macro = self.options["command"]
        self.log.log(2,"Macro '%s' Stages %s" % (self.macro,self.macros[self.macro]))
    
    def startup(self):
        """Basic actions for simulator startup"""
        self.starting = True
        
        self.macros["all"] = self.stages.keys()
        self.macros["none"] = []
        self.order = self.orders.keys()
        self.order.sort()
        
        if self.commandLine:
            self.parseArguments()
            self.pre_applyArguments()
        self.configure(configFile=self.config["System"]["Configs"]["Main"])
        if self.commandLine:
            self.post_applyArguments()
        
        self.starting = False
        
    def run(self):
        """Run the actual simulator"""
        self.startup()
        self.running = True
        
        for position in self.order:
            use = False
            stage = self.orders[position]
            if stage in self.macros[self.macro]:
                use = True
            if stage in self.options["exclude"]:
                use = False
            if stage in self.options["include"]:
                use = True
            if not use:
                self.log.log(2,"Skipping stage %s" % stage)
            if use:
                self.execute(stage)
        
        self.exit()
    
    def execute(self,stage):
        """Actually exectue a particular stage"""
        s = self.stages[stage]
        self.log.debug("Starting %s" % s.name)
        self.log.info("Running %s" % s.description)
        try:
            s.do()
        except s.exceptions as e:
            self.log.error("Error %(name)s in stage %(desc)s. Stage indicated that this error was not critical" % {'name': e.__class__.__name__, 'desc': s.description})
            self.log.error("Error: %(msg)s" % {'msg':e})
        except Exception as e:
            self.log.critical("Error %(name)s in stage %(desc)s!" % {'name': e.__class__.__name__, 'desc': s.description})
            self.log.critical("Error: %(msg)s" % {'msg':e})
            raise
        else:
            self.log.debug("Successfully completed stage %s" % s.name)
        finally:
            self.log.debug("Finished %s" % s.name)
        
    def exit(self):
        """Cleanup function for when we are all done"""
        self.log.debug("Simulation took %2.1f seconds" % (time.clock()-self.times["init"]))
    
        