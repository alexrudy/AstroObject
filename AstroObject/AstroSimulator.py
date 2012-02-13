# 
#  AstroSimulator.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-12-14.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.3.0a1
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
    """A stage object for maintaing data structure"""
    def __init__(self,stage,name="a Stage",description="A description",order=0,exceptions=None,dependencies=None):
        super(Stage, self).__init__()
        self.do = stage
        if exceptions == None:
            self.exceptions = tuple()
        else:
            self.exceptions = exceptions
        self.name = name
        self.description = description
        self.order = order
        self.deps = dependencies

class Simulator(object):
    """A Simulator, used for running large segements of code with detailed logging and progress checking. Simulators have a name, the `name` parameter can be left as is to use the name of the simulator's class (mostly useful if you subclassed it!). The `commandLine` parameter can be set to False to prevent the simulator collecting arguments from `sys.argv` for use. This allows you to programatically call the simulator with the :meth:`do` method."""
    
    name = "Simulator"
    
    config = {
        "Dirs" : {
            "Caches" : "Caches",
            "Logs" : "Logs/",
            "Partials" : "Partials",
            "Images" : "Images",
        },
        "Configs" : {
            "Main" : "Simulator.yaml",
            "This" : "Simulator.yaml",
        },
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
        self.log = logging.getLogger(self.name)
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
        self.Caches = CacheManager(self.name)
        self.initOptions()
        
    def initOptions(self):
        """Initializes the command line options for this script. This function is automatically called on construction, and provides the following default command options which are already supported by the simulator
        
        Command line options are:
        
        ================ =====================
        CLI Option       Description
        ================ =====================
        `--version`      Display version information about this module
        `--do-plot`      Show debugging plots which will be stored in the Partials directory
        `--no-cache`     Disable all caching mechanisms
        `--debug`,`-d`   Turn on debugging messages
        `--config`       Specify a configuration file
        `--dump-config`  Write the current configuration to file
        `--print-stages` Print the stages that the command will execute, do not do anything
        ================ =====================
        
        Macros defined at this level are:
        
        ======== ==================================================
        Macro    Result
        ======== ==================================================
        `*all`   Includes every stage
        `*none`  Doesn't include any stages (technically redundant)
        ======== ==================================================
        
        """
        self.USAGE = "%(command)s %(basicOpts)s %(subcommand)s"
        self.USAGEFMT = { 'command' : "%(prog)s", 'basicOpts': "[ configuartion options ]", 'subcommand' : "{macro}" }
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
        self.parser.add_argument('--print-stages',action='store_true',dest='print_stages',help="Print the stages that the simulator intends to run")

        self.macro_parser = self.parser.add_argument_group('Macros')
        self.macro_parser.add_argument("*all",action='append_const',dest='macros',const="all",help="All Stages")
        self.macro_parser.add_argument("*none",action='append_const',dest='macros',const='none',help=argparse.SUPPRESS)
        self.pos_stage_parser = self.parser.add_argument_group('Stages')
        self.neg_stage_parser = self.parser.add_argument_group('Remove Stages')
        self.config_parser = self.parser.add_argument_group("Configuration")
        
        self.macros["all"] = []
        self.macros["none"] = []
        
        
    def registerStage(self,stage,name=None,description=None,position=None,exceptions=None,include=True,help=False):
        """Register a stage for operation with the simulator. The stage will then be available as a command line option, and will be operated with the simulator.
        
        Registered stages can be explicity run from the command line by including::
            
            $ Simulator +stage
            
        And can be explicity excluded from the command line::
            
            $ Simulator -stage
            
        Where `+stage` will override `-stage` so::
            
            $ Simulator +test -test
            $ Simulator -test +test
            
        will both run the `test` stage.
        
        =================== ==============
        keyword             Description
        =================== ==============
        stage               The function to run for this stage. Should not take any arguments
        name                The command-line name of this stage (no spaces, `+`, `-`, or `*`)
        description         A short description, which will be used by the logger when displaying information about the stage
        position            A number, describing the position in the ordering for this stage. If None, stages are appended to the end of the stage list.
        exceptions          A tuple of exceptions which are acceptable results for this stage. These exceptions will be caught and logged, but will allow the simulator to continue
        include             A boolean, Whether to include this stage in the `*all` macro or not.
        help                Help text for the command line argument. A value of False excludes the help, None includes generic help.
        =================== ==============
        """
        if self.running or self.starting:
            raise ConfigurationError("Cannot add a new stage to the simulator, the simulation has already started!")
        if position == None:
            if len(self.orders.keys()) == 0:
                position = 0
            else:
                position = max(self.orders.keys()) + 1
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
            inhelp = help
            exhelp = help
        elif help == None:
            help = "stage %s" % name
            inhelp = "Include " + help
            exhelp = "Exclude " + help
        else:
            inhelp = "Include " + help
            exhelp = "Exclude " + help
            
        
        stageObject = Stage(stage,name=name,description=description,order=position,exceptions=exceptions)
        self.stages[name] = stageObject
        self.orders[position] = name
        self.pos_stage_parser.add_argument("+"+name,action='append_const',dest='include',const=name,help=inhelp)
        self.neg_stage_parser.add_argument("-"+name,action='append_const',dest='exclude',const=name,help=exhelp)
        if include:
            self.macros["all"] += [name]
        
    def registerMacro(self,name,*stages,**kwargs):
        """Add a new macro to the simulation. Macros are groups of stages (and other macros) which can be called fromthe command line using the `*` parameter. Macros are registered with the command name (without the `*`) and the remaining arguments are the stage/macro names to be included. Kewyord argumetns can be included, and will be passed to argparse.add_argument
        """
        if self.running or self.starting:
            raise ConfigureError("Cannot add macro after simulator has started!")
            
        if "help" not in kwargs:
            help = argparse.SUPPRESS
        else:
            help = kwargs["help"]
            del kwargs["help"]
        self.mparse[name] = self.macro_parser.add_argument("*"+name,action='append_const',dest='macros',const=name,help=help,**kwargs)
        self.macros[name] = list(stages)
        
    def registerConfigOpts(self,argument,configuration,**kwargs):
        """Registers a bulk configuration option which will be provided with the USAGE statement"""
        if self.running or self.starting:
            raise ConfigureError("Cannot add macro after simulator has started!")
        
        if "help" not in kwargs:
            help = argparse.SUPPRESS
        else:
            help = kwargs["help"]
            del kwargs["help"]
        
        self.config_parser.add_argument("-"+argument,action='append_const',dest='preconfig',const=configuration,help=help,**kwargs)
        
        
    def configure(self,configFile=None,configuration=None):
        """Configure this object. Configuration happens first from passed dictionaries (`configuration` variable) and then from files. The result is that configuration will use the values from files in place of values from passed in dictionaries. Running this function twice requires re-setting the `self.configured`."""
        if self.running:
            return ConfigurationError("Cannot configure the simulator, the simulation has already started!")
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
        
        # Start Logging
        self.log.configure(configuration=self.config)
        self.log.start()
        if os.path.isdir(self.config["Dirs"]["Partials"]):
            with open(self.config["Dirs"]["Partials"]+"/config-%s.yaml" % (self.name),"w") as stream:
                stream.write("# Configuration from %s\n" % self.name)
                yaml.dump(self.config,stream,default_flow_style=False) 
        
        # Write Configuration to Partials Directory
        if os.path.isdir(self.config["Dirs"]["Partials"]):
            with open("%s/config-%s.yaml" % (self.config["Dirs"]["Partials"],self.name),"w") as stream:
                stream.write("# Configuration from %s\n" % self.name)
                yaml.dump(self.config,stream,default_flow_style=False) 
        
    def parseArguments(self,*args):
        """Parse arguments. Argumetns can be passed into this function like they would be passed to the command line. These arguments will only be parsed when the system is not in `commandLine` mode."""
        if args != None and not self.commandLine:
            Namespace = self.parser.parse_args(list(args))
            self.options = vars(Namespace)
        elif self.commandLine:
            Namespace = self.parser.parse_args()
            self.options = vars(Namespace)
        else:
            self.log.debug("Skipping argument parsing")
    
    def pre_applyArguments(self):
        """Applies arguments before configuration. Only argument applied is the name of the configuration file, allowing the command line to change the configuration file name."""
        if "config" in self.options and self.options["config"] != None:
            self.config["Configs"]["This"] = self.options["config"]
        if "preconfig" in self.options and self.options["preconfig"] != None:
            for config in self.options["preconfig"]:
                self.config = update(self.config,config)
        

        
    
    
    def post_applyArguments(self):
        """Apply arguments after configuration. The arguments applied here flesh out macros, and copy data from the configuration system into the operations system."""
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
        """Recursively traverse macros and turn them into lists of stages, rather than lists of stages and macros."""
        expanded = {}
        for macro in self.macros.keys():
            expanded[macro] = self._expandMacros(macro)
        self.macros = expanded

    def _expandMacros(self,macro,*expanded):
        """Recursive macro expansion function"""
        if macro in expanded:
            raise ConfigurationError("I seem to be in a recursive macro")
        newMacro = []
        for stage in self.macros[macro]:
            if stage in self.macros.keys():
                newMacro += self._expandMacros(stage,macro,*expanded)
            else:
                newMacro += [stage]
        return newMacro
        
    def startup(self):
        """Start up the simulation. """
        self.starting = True
        self.expandMacros()
        self.parseArguments()
        self.pre_applyArguments()
        self.configure(configFile=self.config["Configs"]["This"])
        if self.caching:
            self.Caches.load()
        self.starting = False
        
    def next(self):
        """Return the name of the next stage for the simulator."""
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
        """Run the simulator. Parses arguments (*args) passed in to take control of the system"""
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
                if self.options['print_stages']:
                    if use:
                        completed.append(stage)    
                elif not use:
                    self.log.log(2,"Skipping stage %s" % stage)
                    if stage in self.macros["all"]:
                        self.inorder = False
                elif use:
                    if not self.inorder:
                        self.log.warning("Stages have run out of order... mileage may vary.")
                    self.execute(stage)
                    completed.append(stage)
            else:
                self.running = False
        
        if self.options['print_stages']:
            print completed
        return completed
    
    def execute(self,stage):
        """Actually exectue a particular stage"""
        s = self.stages[stage]
        self.log.debug("Starting %s" % s.name)
        self.log.info("%s" % s.description)
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
        
