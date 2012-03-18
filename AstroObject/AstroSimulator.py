# -*- coding: utf-8 -*-
# 
#  AstroSimulator.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-12-14.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.3.0
# 

# Standard Python Modules
import math, copy, sys, time, logging, os, json
import argparse
import yaml

# Submodules from this system
from AstroCache import *
from AstroConfig import *
from Utilities import *

__all__ = ["Simulator"]

__version__ = getVersion()

class Stage(object):
    """A stage object for maintaing data structure. This object is only created internally by the :class:`Simulator` class. The attributes of this class are directly called. The class does not provide accessor or setter methods, and should never be called externally.
    
    .. attribute:: Stage.do
        
        The stage function to be called during operation.
    
    .. attribute:: macro
        
        Boolean flag. Set to ``False`` if this stage has a callable ``do`` attribute.
        
    .. attribute:: exceptions
        
        A tuple of exceptions which should not cause this stage to fail.
    
    .. attribute:: name
        
        The calling, hashable name of this stage, stored here for return as a string value in messages.
        
    .. attribute:: description
        
        A human readable description of what this stage is doing, represeneted in the active voice and shown during operation.
        
    .. attribute:: deps
    
        List of all of the stages that this stage depends on.
        
    .. attribute:: reps
        
        List of all the stages that this stage could replace
        
    .. attribute:: optional
        
        A boolean flag. If it is set to true, the simulator will not raise a warning when this stage is skipped.
        
    """
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
            "Partials": "Partials",
        },
        "Configurations" : {
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
        self.Caches = CacheManager()
        self.options = None
        self._initOptions()
        
    def _initOptions(self):
        """Initializes the command line options for this script. This function is automatically called on construction, and provides the following default command options which are already supported by the simulator:
        
        Command line options are:
        
        ================== =====================
        CLI Option         Description
        ================== =====================
        ``--version``      Display version information about this module
        ``--cf file.yaml`` Specify a configuration file
        ``--dry-run``      Print the stages this command would have run.
        ``--dump``         Write the current configuration to file
        ``--stages``       Print the stages that the command will execute, do not do anything
        ================== =====================
        
        Macros defined at this level are:
        
        ========= ==================================================
        Macro     Result
        ========= ==================================================
        ``*all``   Includes every stage
        ``*none``  Doesn't include any stages (technically redundant)
        ========= ==================================================
        
        """
        self.USAGE = "%(command)s %(basicOpts)s %(subcommand)s"
        self.USAGEFMT = { 'command' : "%(prog)s", 'basicOpts': "[ options ][ configuration ]", 'subcommand' : "{stages}" }
        
        
        ShortHelp = """
        Command Line Interface for %(name)s.
        The simulator is set up in stages, which are listed below. 
        By default, the *all stage should run the important parts of the simulator.
        
        (*) Include      : To include a stage, use *stage. This will also run the dependents for that stage.
        (-) Exclude      : To exclude a stage, use -stage. 
        (+) Include-only : To include a stage, but not the dependents of that stage, use +stage.
        
        To run the simulater, use 
        $ %(command)s *all""" % { 'command': "%(prog)s",'name': self.name }
        LongHelp = """The command line interface to %(name)s normally takes a stage or stages as arguments. Each stage is specified on the command line prefixed by the *,+, or - characters. The * will run the stage and all dependents. The + will run solely that stage. The - will specifically exclude that stage (and so skip it's dependents)."""
        
        self.parser = argparse.ArgumentParser(description=ShortHelp,
            formatter_class=argparse.RawDescriptionHelpFormatter,usage=self.USAGE % self.USAGEFMT,prefix_chars="-+*")
        
        # Parsers
        self.config_parser = self.parser.add_argument_group("Configuration")
        self.pos_stage_parser = self.parser.add_argument_group('Single Use Stages')
        self.neg_stage_parser = self.parser.add_argument_group('Remove Stages')
        self.inc_stage_parser = self.parser.add_argument_group('Stages')
        
        # Add the basic controls for the script
        self.parser.add_argument('--version',action='version',version=__version__)
        
        # Operational Controls
        self.registerConfigOpts('d',{'Debug':True},help="enable debugging messages and plots")
        
        # Config Commands
        self.parser.add_argument('--pre-configure',action='append',help=argparse.SUPPRESS,metavar="{'config':'value'}",dest='preconfigure')
        self.parser.add_argument('--configure',action='append',metavar="{'config':'value'}",help="Add configuration items in the form of python dictionaries",dest='postconfig')
        self.parser.add_argument('--cf',action='store',dest='config',type=str,help="use the specified configuration file",metavar="file.yaml")
        self.parser.add_argument('--dry-run',action='store_true',dest='dry_run',help="Print the stages that the simulator wishes to run, without executing.")
        self.registerFunction('--dump',self._dump_config)
        self.registerFunction('--stages',self._list_stages,help="List all of the stages initialized")
        

        
        # Default Macro
        self.registerStage(None,"all",description="Run all stages",help="Run all stages",include=False)
        self.registerStage(None,"none",description="Run no stages",help="Run no stages",include=False)
        
        
    def _default_macros(self):
        """Sets up the ``*all`` macro for this system, specifically, triggers the ``*all`` macro to run last."""
        self.orders.remove("all")
        self.orders += ["all"]

        
        
        
    def registerStage(self,stage,name,description=None,exceptions=None,include=True,help=False,dependencies=None,replaces=None,optional=False):
        """Register a stage for operation with the simulator. The stage will then be available as a command line option, and will be operated with the simulator. Stages should be registered early in the operation of the simulator (preferably in the initialization, after the simulator class itself has initialized) so that the program is aware of the stages for running. 
        
    	Stages are called with either a ``*``, ``+`` or ``-`` character at the beginning. Their resepctive actions are shown below.
	
    	========= ============ ================================
    	Character  Action      Description
    	========= ============ ================================
    	``*``     Include      To include a stage, use ``*stage``. This will also run the dependents for that stage.
    	``-``     Exclude      To exclude a stage, use ``-stage``. This stage (and it's dependents) will be skipped.
    	``+``     Include-only To include a stage, but not the dependents of that stage, use ``+stage``.
    	========= ============ ================================
        
        To use a registered stage, and call all of its dependents, call ::
            
            $ Simulator *stage
            
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
        exceptions          A tuple of exceptions which are acceptable results for this stage. These exceptions will be caught and logged, but will allow the simulator to continue. These exceptions will still raise errors in Debug mode.
        include             A boolean, Whether to include this stage in the `*all` macro or not.
        help                Help text for the command line argument. A value of False excludes the help, None includes generic help.
        dependencies        An ordered list of the stages which must run before this stage can run. Dependencies will be deep-searched.
        replaces            A list of stages which can be replaced by this stage. This stage will now satisfy those dependencies.
        optional            A boolean about wheather this stage can be skipped. If so, warnings will not be raised when this stage is explicitly skipped (like ``-stage`` would do)
        =================== ==============
        
        Stages cannot be added dynamically. Once the simulator starts running (i.e. processing stages) the order and settings are fixed. Attempting to adjsut the stages at this point will raise an error.
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
        self.pos_stage_parser.add_argument("+"+name,action='append_const',dest='include',const=name,help=argparse.SUPPRESS)
        self.neg_stage_parser.add_argument("-"+name,action='append_const',dest='exclude',const=name,help=argparse.SUPPRESS)
        self.inc_stage_parser.add_argument("*"+name,action='append_const',dest='macro',const=name,help=help)
        if include:
            self.stages["all"].deps += [name]
        
    def registerFunction(self,argument,function,post=True,**kwargs):
        """Register a function to run using a flag"""
        if self.running or self.starting:
            raise ConfigureError("Cannot add macro after simulator has started!")
        
        if "help" not in kwargs:
            help = argparse.SUPPRESS
        else:
            help = kwargs["help"]
            del kwargs["help"]
        if post:
            dest='postfunc'
        else:
            dest='prefunc'
        
        self.parser.add_argument(argument,action='append_const',dest='postfunc',const=function,help=help,**kwargs)
        
        
    def registerConfigOpts(self,argument,configuration,preconfig=True,**kwargs):
        """Registers a bulk configuration option which will be provided with the USAGE statement. This configuration option can easily override normal configuration settings. Configuration provided here will override programmatically specified configuration options. It will not override configuration provided by the configuration file. These configuration options are meant to provide alterantive *defaults*, not alternative configurations."""
        if self.running or self.starting:
            raise ConfigureError("Cannot add macro after simulator has started!")
        
        if "help" not in kwargs:
            help = argparse.SUPPRESS
        else:
            help = kwargs["help"]
            del kwargs["help"]
        if preconfig:
            dest = 'preconfig'
        else:
            dest = 'postconifg'
        self.config_parser.add_argument("-"+argument,action='append_const',dest=dest,const=configuration,help=help,**kwargs)
        
        
    def _configure(self,configFile=None,configuration=None):
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
            with open("%s/config-%s.yaml" % (self.config["Dirs"]["Partials"],self.name),"w") as stream:
                stream.write("# Configuration from %s\n" % self.name)
                yaml.dump(self.config,stream,default_flow_style=False) 
        
    def _parseArguments(self):
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
    
    def _preConfiguration(self):
        """Applies arguments before configuration. Only argument applied is the name of the configuration file, allowing the command line to change the configuration file name."""
        if "config" in self.options and self.options["config"] != None:
            self.config["Configurations"]["This"] = self.options["config"]
        if "preconfig" in self.options and self.options["preconfig"] != None:
            for preconfig in self.options["preconfig"]:
                if isinstance(preconfig,str):
                    preconfig = json.loads(unicode(preconfig))
                self.config.merge(preconfig)
        if "prefunc" in self.options and self.options["prefunc"] != None:
            for f in self.options["prefunc"]:
                f()
        
            
    def _postConfiguration(self):
        """Apply arguments after configuration. The arguments applied here flesh out macros, and copy data from the configuration system into the operations system."""
        if "exclude" not in self.options or not isinstance(self.options["exclude"],list):
            self.options["exclude"] = []
        if "include" not in self.options or not isinstance(self.options["include"],list):
            self.options["include"] = []
        if "macro" not in self.options or not isinstance(self.options["macro"],list):
            self.options["macro"] = []
        if "postconfig" in self.options and self.options["postconfig"] != None:
            for preconfig in self.options["postconfig"]:
                if isinstance(preconfig,str):
                    preconfig = json.loads(unicode(preconfig))
                self.config.merge(preconfig)
        
        if "postfunc" in self.options and self.options["postfunc"] != None:
            for f in self.options["postfunc"]:
                f()
        
        
    def _list_stages(self):
        """List stages and exit"""
        text = "Stages:\n"
        for stage in self.orders:
            s = self.stages[stage]
            text += "%(command)-20s : %(desc)s" % {'command':s.name,'desc':s.description}
            text += "\n"
        self.parser.exit(message=text)
        
    def _dump_config(self):
        """Dump the configuration to a file"""
        with open(self.config["Configurations"]["This"]+"-dump.yaml","w") as stream:
            stream.write("# Configuration from %s\n" % self.name)
            yaml.dump(self.config.extract(),stream,default_flow_style=False) 
        
                
    def startup(self):
        """Start up the simulation. """
        self._default_macros()
        self.starting = True
        self._parseArguments()
        self._preConfiguration()
        self._configure(configFile=self.config["Configurations"]["This"])
        self._postConfiguration()
        self.starting = False
        
        
        
    def run(self):
        """Run the actual simulator. This command handles simulators which can be run from the command line. Calling :meth:`run` will run all of the stages specified on the command line. If you do not want this effect, use :meth:`startup` to prepare the simulator, and :meth:`do` to run the actual simulator. Calling :meth:`exit` at the end will allow the simulator to close out and perform any output tasks, but will also end the current python session."""
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
        
        if self.options['dry_run']:
            text = "Stages completed:\n"
            for stage in self.complete:
                s = self.stages[stage]
                text += "%(command)-20s : %(desc)s" % {'command':s.name,'desc':s.description}
                text += "\n"
            self.exit(msg=text)
            
    def execute(self,stage,deps=True):
        """Actually exectue a particular stage"""
        if self.paused or not self.running:
            return False
            
        if stage not in self.stages:
            self.log.critical("Stage %s does not exist." % stage)
            self.exit(1)
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
        
        if self.options["dry_run"]:
            self.complete += [stage] + s.reps
            return use
        
        self.log.debug("Starting \'%s\'" % s.name)
        self.log.info("%s" % s.description)
        
        try:
            s.do()
        except KeyboardInterrupt as e:
            self.log.useConsole(True)
            self.log.critical("Keyboard Interrupt... ending simulator.")
            self.log.critical("Last completed stage: %(stage)s" % {'stage':self.complete.pop()})
            self.log.debug("Stages completed: %s" % self.complete)
            self.exit()
        except s.exceptions as e:
            if self.config["Debug"]:
                self.log.useConsole(True)
            self.log.error(u"Error %(name)s in stage %(stage)s:%(desc)s. Stage indicated that this error was not critical" % {'name': e.__class__.__name__, 'desc': s.description,'stage':s.name})
            self.log.error(u"Error: %(msg)s" % {'msg':e})
            if self.config["Debug"]:
                raise
        except Exception as e:
            self.log.useConsole(True)
            self.log.critical(u"Error %(name)s in stage %(stage)s:%(desc)s!" % {'name': e.__class__.__name__, 'desc': s.description,'stage':s.name})
            self.log.critical(u"Error: %(msg)s" % {'msg':e})
            raise
        else:
            self.log.debug(u"Completed \'%s\'" % s.name)
            self.complete += [stage] + s.reps
        finally:
            self.log.debug(u"Finished \'%s\'" % s.name)
        
        return use
        
    def exit(self,code=0,msg=None):
        """Cleanup function for when we are all done"""
        if msg:
            self.log.info(msg)
        self.log.info("Simulator %s Finished" % self.name)
        sys.exit(code)
        
