# 
#  AstroSimulator.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-12-14.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.3.0a1
# 

# Standard Python Modules
import math, copy, sys, time, logging, os
import argparse
import yaml

# Submodules from this system
from AstroCache import *
from AstroConfig import *
from Utilities import *

__all__ = ["Simulator"]

__version__ = getVersion()

class Stage(object):
    """A stage object for maintaing data structure"""
    def __init__(self,stage,name="a Stage",description="A description",exceptions=None,dependencies=None,replaces=None,optional=False):
        super(Stage, self).__init__()
        self.macro = False
        if callable(stage):
            self.do = stage
        else:
            self.do = lambda: None
            self.macro = True
        if exceptions == None:
            self.exceptions = tuple()
        else:
            self.exceptions = exceptions
        self.name = name
        self.description = description
        self.deps = dependencies
        self.reps = replaces
        self.optional = optional

class Simulator(object):
    """A Simulator, used for running large segements of code with detailed logging and progress checking. Simulators have a name, the `name` parameter can be left as is to use the name of the simulator's class (mostly useful if you subclassed it!). The `commandLine` parameter can be set to False to prevent the simulator collecting arguments from `sys.argv` for use. This allows you to programatically call the simulator with the :meth:`do` method."""
    
    name = "Simulator"
    
    def __init__(self,name="__class__.__name__",commandLine=True):
        super(Simulator, self).__init__()
        self.stages = {}
        self.macros = {}
        self.exclude = []
        self.include = []
        self.attempt = []
        self.orders = []
        self.complete = []
        self.name = name
        self.order = None
        self.config = StructuredConfiguration({
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
          'growl' : {
              'enable' : True,
              'level'  : None,
              'name' : "AstroSimulator",
          }
        },
       })
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
        self.options = None
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
        LongHelp = """The command line interface to %(name)s normally takes a stage or stages as arguments. Each stage is specified on the command line prefixed by the *,+, or - characters. The * will run the stage and all dependents. The + will run solely that stage. The - will specifically exclude that stage (and so skip it's dependents)."""
        
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
        self.parser.add_argument('--clear-cache',action='store_true',dest='clear_cache')
        self.parser.add_argument('-d','--debug',action='store_true',dest='debug',help="enable debugging messages and plots")
        
        # Config Commands
        self.parser.add_argument('--config',action='store',dest='config',type=str,help="use the specified configuration file",metavar="file.yaml")
        self.parser.add_argument('--dump-config',action='store_true',dest='dump',help=argparse.SUPPRESS)
        self.parser.add_argument('--print-stages',action='store_true',dest='print_stages',help="Print the stages that the simulator intends to run")

        # Parsers
        self.config_parser = self.parser.add_argument_group("Configuration")
        self.pos_stage_parser = self.parser.add_argument_group('Single Use Stages')
        self.neg_stage_parser = self.parser.add_argument_group('Remove Stages')
        self.inc_stage_parser = self.parser.add_argument_group('Stages')
        
        # Default Macro
        self.registerStage(None,"all",description="Run all stages",help="Run all stages",include=False)
        self.registerStage(None,"none",description="Run no stages",help="Run no stages",include=False)
        
        
        
    def registerStage(self,stage,name,description=None,position=None,exceptions=None,include=True,help=False,dependencies=None,replaces=None,optional=False):
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
        if name == None:
            raise ValueError("Stage must have a name")
        if name in self.stages:
            raise ValueError("Cannot have duplicate stage named %s" % name)
        if description == None:
            description = name
        if exceptions == None:
            exceptions = tuple()
        if dependencies == None:
            dependencies = []
        if not isinstance(dependencies,list):
            raise ValueError("Invalid type for dependencies: %s" % type(dependencies))
            
        if replaces == None:
            replaces = []
        if not isinstance(replaces,list):
            raise ValueError("Invalid type for dependencies: %s" % type(replaces))
            
        if help == False:
            help = argparse.SUPPRESS
        elif help == None:
            help = "stage %s" % name

            
        
        stageObject = Stage(stage,name=name,description=description,exceptions=exceptions,dependencies=dependencies,replaces=replaces,optional=optional)
        self.stages[name] = stageObject
        self.orders += [name]
        if not stageObject.macro:
            self.pos_stage_parser.add_argument("+"+name,action='append_const',dest='include',const=name,help=argparse.SUPPRESS)
            self.neg_stage_parser.add_argument("-"+name,action='append_const',dest='exclude',const=name,help=argparse.SUPPRESS)
        self.inc_stage_parser.add_argument("*"+name,action='append_const',dest='macro',const=name,help=help)
        if include:
            self.stages["all"].deps += [name]
        
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
            self.config.merge(configuration)
            self.log.debug("Updated Configuration from variable")            
            self.configured |= True
        # Configure from File
        if configFile != None:
            self.configured |= self.config.load(configFile)
        self.configured |= self.config.load()
        
        if not self.configured:
            self.log.log(8,"No configuration provided or accessed. Using defaults.")
        
        # Start Logging
        self.log.configure(configuration=self.config)
        self.log.start()
        
        # Write Configuration to Partials Directory
        if os.path.isdir(self.config["Dirs"]["Partials"]):
            with open(self.config["Dirs"]["Partials"]+"/config-%s.yaml" % (self.name),"w") as stream:
                stream.write("# Configuration from %s\n" % self.name)
                yaml.dump(self.config,stream,default_flow_style=False) 
        
    def parseArguments(self):
        """Parse arguments. Argumetns can be passed into this function like they would be passed to the command line. These arguments will only be parsed when the system is not in `commandLine` mode."""
        if self.commandLine:
            Namespace = self.parser.parse_args()
            self.options = vars(Namespace)
            self.log.log(2,"Parsed command line arguments")
        elif self.options == None:
            Namespace = self.parser.parse_args("")
            self.options = vars(Namespace)
            self.log.log(2,"Parsed default line arguments")
        else:
            self.log.debug("Skipping argument parsing")
    
    def preConfiguration(self):
        """Applies arguments before configuration. Only argument applied is the name of the configuration file, allowing the command line to change the configuration file name."""
        if "config" in self.options and self.options["config"] != None:
            self.config["Configs"]["This"] = self.options["config"]
        if "preconfig" in self.options and self.options["preconfig"] != None:
            for preconfig in self.options["preconfig"]:
                self.config.merge(preconfig)
            
    def postConfiguration(self):
        """Apply arguments after configuration. The arguments applied here flesh out macros, and copy data from the configuration system into the operations system."""
        if "exclude" not in self.options or not isinstance(self.options["exclude"],list):
            self.options["exclude"] = []
        if "include" not in self.options or not isinstance(self.options["include"],list):
            self.options["include"] = []
        if "macro" not in self.options or not isinstance(self.options["macro"],list):
            self.options["macro"] = []
        if self.options["debug"]:
            self.config["Debug"] = self.options["debug"]
        
    def startup(self):
        """Start up the simulation. """
        self.starting = True
        self.parseArguments()
        self.preConfiguration()
        self.configure(configFile=self.config["Configs"]["This"])
        if self.caching:
            self.Caches.load()
        self.postConfiguration()
        self.starting = False
        
        
        
    def run(self):
        """Run the actual simulator"""
        self.startup()
        self.do()
        self.exit()
    
    def do(self,*stages):
        """Run the simulator. Macro runs stages passed in."""
        if self.running:
            raise ConfigurationError("Simulator is already running!")
        self.running = True
        self.options["macro"] += list(stages)
        if self.options["macro"] == []:
            self.parser.error("No stages triggered to run!")
        if self.attempt == []:
            self.inorder = True
            self.complete = []
        
        while self.running and not self.paused:
            for stage in self.orders:
                if stage in self.options["macro"]:
                    self.execute(stage)
                elif stage in self.options["include"]:
                    self.execute(stage,deps=False)
            self.running = False
        
        if self.options['print_stages']:
            print self.completed
    
    def execute(self,stage,deps=True):
        """Actually exectue a particular stage"""
        if self.paused or not self.running:
            return False
        use = True
        if stage in self.options["exclude"]:
            use = False
        if stage in self.options["include"]:
            use = True
        if stage in self.attempt:
            return use
        if not use:
            return use
        
        self.attempt += [stage] + self.stages[stage].reps
         
        if deps:
            
            for dependent in self.stages[stage].deps:
                if dependent not in self.attempt:
                    self.execute(dependent)
                if dependent not in self.complete:
                    if self.stages[dependent].optional:
                        self.log.debug("Stage \'%s\' requested by \'%s\' but skipped" % (dependent,stage))
                    else:
                        self.log.warning("Stage \'%s\' required by \'%s\' but failed to complete." % (dependent,stage))
        else:
            self.log.warning("Explicity skipping dependents")
        
        s = self.stages[stage]
        if s.macro:
            self.complete += [stage] + s.reps
            return use
        
        self.log.debug("Starting \'%s\'" % s.name)
        self.log.info("%s" % s.description)
        
        try:
            s.do()
        except s.exceptions as e:
            self.log.error("Error %(name)s in stage %(desc)s. Stage indicated that this error was not critical" % {'name': e.__class__.__name__, 'desc': s.description})
            self.log.error("Error: %(msg)s" % {'msg':e})
            if self.config["Debug"]:
                raise
        except Exception as e:
            self.log.critical("Error %(name)s in stage %(desc)s!" % {'name': e.__class__.__name__, 'desc': s.description})
            self.log.critical("Error: %(msg)s" % {'msg':e})
            raise
        else:
            self.log.debug("Completed \'%s\'" % s.name)
            self.complete += [stage] + s.reps
        finally:
            self.log.debug("Finished \'%s\'" % s.name)
        
        return use
        
    def exit(self):
        """Cleanup function for when we are all done"""
        pass
        
