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

# Scipy Extras
from scipy import ndimage
from scipy.spatial.distance import cdist
from scipy.linalg import norm

# Standard Python Modules
import math, copy, sys, time, logging, os
import argparse
import yaml

# Submodules from this system
from AstroCache import *
from Utilities import *

__all__ = ["Simulator"]

__version__ = getVersion()

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
                'format' : "%(asctime)s : %(levelname)-8s : %(module)-15s : %(funcName)-10s : %(message)s",
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
                "Main" : "Simulator.yaml",
            },
        },
    }
    
    def __init__(self,name="__class__.__name__",commandLine=True):
        super(Simulator, self).__init__()
        self.stages = {}
        self.orders = {}
        self.macros = {}
        self.mparse = {}
        self.exclude = []
        self.name = name
        self.order = None
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
        self.paused = False
        self.commandLine = commandLine
        self.Caches = CacheManager()
        self.initOptions()
        
    def initOptions(self):
        """Initializes the command line options for this script"""
        self.USAGE = "%(command)s %(basicOpts)s %(subcommand)s"
        self.USAGEFMT = { 'command' : os.path.basename(sys.argv[0]), 'basicOpts': "[ -E | -D | -T ]", 'subcommand' : "{macro}" }
        ShortHelp = "Command Line Interface for %(name)s" % { 'name': self.name }
        self.parser = argparse.ArgumentParser(description=ShortHelp,
            formatter_class=argparse.RawDescriptionHelpFormatter,usage=self.USAGE % self.USAGEFMT,prefix_chars="-+*")
        
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
        self.macro_parser = self.parser.add_argument_group('Macros')
        self.macro_parser.add_argument("*all",action='append_const',dest='macros',const="all",help="All Stages")
        self.pos_stage_parser = self.parser.add_argument_group('Stages')
        self.neg_stage_parser = self.parser.add_argument_group('Remove Stages')
        
    def registerStage(self,stage,name=None,description=None,position=None,exceptions=None,help=None,include_all=True):
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
        if help == False:
            help = argparse.SUPPRESS
        elif help == None:
            help = "stage %s" % name
        
        stageObject = Stage(stage,name=name,description=description,order=position,exceptions=exceptions)
        self.stages[name] = stageObject
        self.orders[position] = name
        self.pos_stage_parser.add_argument("+"+name,action='append_const',dest='include',const=name,help="Include "+help)
        self.neg_stage_parser.add_argument("-"+name,action='append_const',dest='exclude',const=name,help="Exclude "+help)
        
    def registerMacro(self,name,*stages,**kwargs):
        """Adds a new macro to the simulation"""
        if self.running or self.starting:
            raise ConfigureError("Cannot add macro after simulator has started!")
            
        if "help" not in kwargs:
            help = argparse.SUPPRESS
        else:
            help = kwargs["help"]
            del kwargs["help"]
        self.mparse[name] = self.macro_parser.add_argument("*"+name,action='append_const',dest='macros',const=name,help=help,**kwargs)
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
    
    def parseArguments(self,*args):
        """Parse arguments, and pre-apply appropriate values to configuration"""
        if args != None and not self.commandLine:
            Namespace = self.parser.parse_args(*args)
        elif self.commandLine:
            Namespace = self.parser.parse_args()
        else:
            raise ConfigurationError("No Operational Arguments Provided...")
        self.options = vars(Namespace)
    
    def pre_applyArguments(self):
        """Apply arguments before configure"""
        if "config" in self.options and self.options["config"] != None:
            self.config["System"]["Configs"]["Main"] = self.options["config"]

        
    
    
    def post_applyArguments(self):
        """Apply post-arguments"""
        if "exclude" not in self.options or not isinstance(self.options["exclude"],list):
            self.options["exclude"] = []
        if "include" not in self.options or not isinstance(self.options["include"],list):
            self.options["include"] = []
        self.macro = []
        if "macros" in self.options and self.options["macros"] != None:
            for m in self.options["macros"]:
                self.macro += self.macros[m]
        if self.macro == [] and self.options["include"] == []:
            self.parser.error("No stages specified for operation")
        self.log.log(2,"Macro Stages %s" % (self.macro))
    
    def expandMacros(self):
        """Expand the macros to expand internal macros"""
        for macro in self.macros:
            self._expandMacros(macro)
        self.macros["all"] = [s for s in self.stages.keys() if s not in self.exclude]
        self.macros["none"] = []
        

    def _expandMacros(self,macro,*expanded):
        """Expand Macros on a certain macro"""
        if macro in expanded:
            raise ConfigurationError("I seem to be in a recursive macro")
        newMacro = []
        for stage in macro:
            if stage in self.macros:
                newMacro += self._expandMacros(self.macros[macro],macro,*expanded)
            else:
                newMacro += stage
        return newMacro
        
    
    def startup(self):
        """Basic actions for simulator startup"""
        self.starting = True
        self.expandMacros()
        self.parseArguments()
        self.pre_applyArguments()
        self.configure(configFile=self.config["System"]["Configs"]["Main"])
        if self.caching:
            self.Caches.load()
        self.starting = False
        
    def next(self):
        """Return the name of the next stage"""
        if self.starting:
            raise ConfigurationError("Simulator hasn't finished starting")
        if self.order == None:
            self.order = min(self.orders.keys())
            return self.orders[self.order]
        next = self.order
        while next <= max(self.orders.keys()):
            next += 1
            if next in self.orders:
                self.order = next
                return self.orders[next]
        return False
        
        
        
    def run(self):
        """Run the actual simulator"""
        self.startup()
        self.do()
        self.exit()
    
    def do(self,*args):
        """Pass a series of modules etc. to this command, to run the system."""
        if self.running:
            raise ConfigurationError("Simulator is already running!")
        
        self.parseArguments(*args)
        self.post_applyArguments()
        self.running = True
        self.inorder = True
        completed = []
        
        while self.running and not self.paused:
            stage = self.next()
            if stage:
                use = False
                if stage in self.macro:
                    use = True
                if stage in self.options["exclude"]:
                    use = False
                if stage in self.options["include"]:
                    use = True
                if not use:
                    self.log.log(2,"Skipping stage %s" % stage)
                    self.inorder = False
                if use:
                    if not self.inorder:
                        self.log.warning("Stages have run out of order... mileage may vary.")
                    self.execute(stage)
                    completed.append(stage)
            else:
                self.running = False
        
        return completed
    
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
        pass
        
