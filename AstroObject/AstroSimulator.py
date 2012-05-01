# -*- coding: utf-8 -*-
# 
#  AstroSimulator.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-12-14.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.5.1
# 
"""
:mod:`AstroSimulator` — Complex Task Management 
===============================================

The Simulator is designed to provide a high level, command-line useful interface to large computational tasks. As the name suggests, Simulators often do a lot of programming work, and do so across many distinct "stages", whcih can be configured in any way the user desires. All of the abilities in this program are simply object abstraction techniques to provide a complex program with a command line interface and better control and reporting on the activities carreid out to successfully complete the program. It allows for the configuration of simple test cases and "macros" from within the program, eliminating the need to provide small wrapper scripts and test handlers.

An example (simple) program using the simulator can be found in :ref:`SimulatorExample`

.. _Simulator_CLI:

:program:`Simulator` Command Line Interface
-------------------------------------------

The master simulator program is a command-line interface to the :meth:`AstroObject.AstroSimulator.Simulator.run` method. Below are the major command line components.

Usage Statement ::
	
	Simulator [ options ][ configuration ] {stages}
	
The program is actually agnostic to the order of arguments. Any argument may come in any position. As such, all arguments must be unique.

.. program:: Simulator

.. option:: {stages}
	
	The stages option specifies individual stages for the program to run. You must specify at least one stage to run in the simulator. By default, two basic stages are provided, ``*all`` and ``*none``. The default simulation is performed by ``*all``. To test the simulator without running any stages (for example, to test :meth:`AstroObject.AstroSimulator.Simulator.registerFunction` functionality), use the ``*none`` stage to opertate without using any stages.
	
	Stages are called with either a ``*``, ``+`` or ``-`` character at the beginning. Their resepctive actions are shown below. All commands must include at least one macro. If you don't want any particular macro, use the ``*none`` macro.
	
	To run a simulation using the ``*all`` macro, the command would be::
		
		$ Simulator *all
		
	
	
	========= ============ ================================
	Character  Action      Description
	========= ============ ================================
	``*``     Include      To include a stage, use ``*stage``. This will also run the dependents for that stage.
	``-``     Exclude      To exclude a stage, use ``-stage``. This stage (and it's dependents) will be skipped.
	``+``     Include-only To include a stage, but not the dependents of that stage, use ``+stage``.
	========= ============ ================================
	
	.. Note ::
		Including an argument and excluding it simultaneously will have the effect of including it overall. So the following three commands are equivalent::
			
			$ Simulator +stage -stage *none
			$ Simulator -stage +stage *none
			$ Simulator +stage *none
			
		Also, excluding a stage that is included as a macro will exclude that stage and not call it's dependents, so the following calls are equivalent ::
			
			$ Simulator -stage *stage
			$ Simulator *none

	
	The commonly used stages in :program:`Simulator` are
	
	=====================  ========================================
	  Stage                Description                             
	=====================  ========================================
	  ``*all``              Run all default stages                 
	  ``*none``             Run no stages                          
	=====================  ========================================
	
	Stages are registered by the :meth:`AstroObject.AstroSimulator.Simulator.registerStage` method.
	
.. option:: [configurations]
	
	Configuration options override defaults set up in :class:`AstroObject.AstroSimulator.Simulator`. As such, they are useful quick changes to a configuration.
	
	 ===================== ============================================
	   Options               Description
	 ===================== ============================================
	   ``-d``                enable debugging messages and plots
	 ===================== ============================================
	
	.. Note::
		This means if you dump the configuration file (see :option:`--dump`) and use that directly as your new configuration file, these options will have no effect. Therefore, it is advisable that your configuration file contain the minimum amount of detail to override the default values set in the program. However, if you wish to use these options, but always disable debug, for example, you could disable debug in your configuration file. This will make none of these flags enable debugging.
		
	
.. option:: -h, --help
	
	Get help about the :program:`Simulator` command. Help will list commonly used stages, optional arguments, and configuration items.
	
	.. Note ::
		To get a full list of stages available, use :option:`--stages`
		
.. option:: --version
	
	Print the program version.
	
.. option:: --cf file.yaml
	
	Set the name of the configuration file to use. By default, the configuation file is called `SED.main.config.yaml`. This will be the filename used for dumping configurations with the :option:`--dump` command (Dump will append the extension ``-dump.yaml`` onto the filename to prevent overwriting exisitng configurations)
	
.. option:: -n,--dry-run
	
	Traverse all of the stages to be run, printing them as the program goes, but do not run any stages.
	
.. option:: --list-stages
	
	Print all stages registered in the simulator. Any stage listed in the output of this function can be run.
	
.. option:: --dump
	
	Dump the configuration to a file. Filenames are the configuration file name with ``-dump.yaml`` appended.

.. option:: --p,--profile
    
    Show a timing profile of the simulation, including status of stages, at the end of the simulation.

.. _Configuration:

:program:`Simulator` Configuration Files
----------------------------------------

:program:`Simulator` configuration files are YAML files which contain a dictionary structure. All values in the YAML files are basic yaml, and contain no python-specific directives. To find out what the default or current configuration is, use the :option:`--dump` command. The file produced from this will contain a YAML structure for the configuration in use when the system started up. The various directives in the configuration file are described below. Configuration options are described using the dotted-syntax described in :mod:`AstroObject.AstroConfig`

- ``Configurations``: contains a list of potential configuration files.
- ``Configurations.Main``: The name of the primary configuration file. This default is produced by the program. Overriding it in the configuration file has essentially no effect.
- ``Dirs``: Directories that this simulator will use for output.
- ``Dirs.Caches``: Location of cache files.
- ``Dirs.Logs``: Location of log files.
- ``Dirs.Partials``: Location of partial output, including a dump of the configuration.
- ``Logging``: Configuration of the :mod:`AstroObject.AstroObjectLogging` module

A simple configuration file can be found in the :ref:`SimulatorExample`.

.. _Simulator_API:

API Methods
-----------
    
The following methods handle the external-API for the simulator. Normally, when you write a simulator, you will subclass the :class:`Simulator`, and then use the methods here to control the behavior of the simulator. At a minimum, a simulator must register stages, probably using :meth:`Simulator.collect` or :meth:`Simulator.registerStage`, and then call the :meth:`Simulator.run` function to process the command line interface and start the simulator.
    
.. autoclass::
    AstroObject.AstroSimulator.Simulator
    
    .. automethod:: collect
    
    .. automethod:: registerStage
    
    .. automethod:: registerConfigOpts
    
    .. automethod:: registerFunction
    
    .. automethod:: run
    
    .. automethod:: startup
    
    .. automethod:: do
    
    .. automethod:: exit
    
    .. automethod:: map

.. _Simulator_Decorators:
    
Decorators
----------
The following decorators can be used (in conjuction with :meth:`AstroObject.AstroSimulator.Simulator.collect`) to register and configure simulator stages:

.. autofunction:: collect

.. autofunction:: ignore

.. autofunction:: include

.. autofunction:: help

.. autofunction:: description

.. autofunction:: depends

.. autofunction:: replaces

.. autofunction:: optional

.. autofunction:: excepts

.. autofunction:: on_collection

.. autofunction:: on_instance_collection
    
Private Methods and Classes
---------------------------
    
These methods are used to implment the public-facing API. They are documented here to explain their use in development.

.. inheritance-diagram::
    AstroObject.AstroSimulator.Simulator
    AstroObject.AstroSimulator.Stage
    :parts: 1

.. automethod:: 
    AstroObject.AstroSimulator.Simulator._initOptions

.. automethod:: 
    AstroObject.AstroSimulator.Simulator._default_macros
    
.. automethod:: 
    AstroObject.AstroSimulator.Simulator._parseArguments
    
.. automethod:: 
    AstroObject.AstroSimulator.Simulator._preConfiguration
    
.. automethod:: 
    AstroObject.AstroSimulator.Simulator._configure
    
.. automethod:: 
    AstroObject.AstroSimulator.Simulator._postConfiguration

.. automethod:: 
    AstroObject.AstroSimulator.Simulator.execute
    
.. autoclass::
    AstroObject.AstroSimulator.Stage


"""


# Standard Python Modules
import math, copy, sys, time, logging, os, json, datetime
import re
import argparse
import yaml
from ast import literal_eval

from pkg_resources import resource_filename

import multiprocessing

# Dependent Modules
from progressbar import *

# Submodules from this system
from AstroCache import *
from AstroConfig import StructuredConfiguration, DottedConfiguration
from Utilities import *

__all__ = ["Simulator","on_collection","help","replaces","excepts","depends","include","optional","description","collect","ignore","on_instance_collection"]

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
    def __init__(self,stage,name="a Stage",description=None,exceptions=None,dependencies=None,replaces=None,optional=False):
        super(Stage, self).__init__()
        self._name = name
        self.macro = False
        if callable(stage):
            self.do = stage
        else:
            self.do = lambda: None
            self.macro = True
            if description == None:
                description = name
        if exceptions == None:
            self.exceptions = tuple()
        elif exceptions == True:
            self.exceptions = Exception
        else:
            self.exceptions = exceptions
        self.description = description
        self.deps = dependencies
        self.reps = replaces
        self.optional = optional
        self.startTime = None
        self.endTime = None
        self.ran = False
        self.complete = False
    
    @property
    def name(self):
        return self._name
    
    @staticmethod
    def table_head():
        """Table head for profiling."""
        text  = u""
        text += terminal.render(u"|%(BLUE)s-----------------------%(NORMAL)s|%(BLUE)s--------%(NORMAL)s|%(BLUE)s---------------%(NORMAL)s|\n")
        text += u"|         Stage         | Passed |     Time      |\n"
        text += terminal.render(u"|%(BLUE)s-----------------------%(NORMAL)s|%(BLUE)s--------%(NORMAL)s|%(BLUE)s---------------%(NORMAL)s|")
        return text
      
    @staticmethod 
    def table_foot(total):
        """Table footer for profiling."""
        text  = terminal.render(u"|%(BLUE)s-----------------------%(NORMAL)s Total Time: ")+u"%(time)-9s"+terminal.render(u"%(BLUE)s---%(NORMAL)s|")
        text = text % {"time":datetime.timedelta(seconds=int(total))}
        return text
        
    def table_row(self,total=None):
        """Return a profiling string table row.
        ::
            
            >>> stage.table_row()
            |                 other |   True |  0:00:00   0% |
            
        
        """
        assert self.ran, "Stage %s didn't run" % self.name
        string =  u"| %(stage)21s | %(color)s%(result)6s%(normal)s | %(timestr) 12s |"
        keys = {
                "stage": self.name,
                "color": terminal.GREEN if self.complete else terminal.RED,
                "normal": terminal.NORMAL,
                "result": str(self.complete),
                "time": datetime.timedelta(seconds=int(self.durTime)),
            }
        if total == None or total == 0:
            keys["timestr"] = u"% 12s" % keys["time"]            
        else:
            keys["per"] = ( self.durTime / total ) * 100.0
            if keys["per"] > 50:
                string += terminal.RED
            elif keys["per"] > 20:
                string += terminal.BLUE
            elif keys["per"] > 10:
                string += terminal.GREEN
            blen = int(keys["per"] * (terminal.COLUMNS - 50) / 75)
            if blen > terminal.COLUMNS - 50:
                blen = terminal.COLUMNS - 50
            string += u"█" * blen
            string += terminal.NORMAL
            keys["timestr"] = u"%(time)8s %(per)3d%%" % keys
        return string % keys
        
    def profile(self):
        """Return a string stage profile for this stage."""
        assert self.ran, u"Stage %s didn't run" % self.name
        return u"Stage %(stage)s %(result)s in %(time).2fe" % {
            "stage": self.name,
            "result": u"completed" if self.complete else u"failed",
            "time": datetime.timedelta(seconds=self.durTime),
        }
        
    def run(self):
        """Run the stage"""
        self.startTime = time.clock()
        try:
            self.ran = True
            self.do()
        except:
            raise
        else:
            self.complete = True
        finally:
            self.endTime = time.clock()
            self.durTime = self.endTime - self.startTime
        

class Simulator(object):
    """A Simulator, used for running large segements of code with detailed logging and progress checking. Simulators have a name, the `name` parameter can be left as is to use the name of the simulator's class (mostly useful if you subclassed it!). The `commandLine` parameter can be set to False to prevent the simulator collecting arguments from `sys.argv` for use. This allows you to programatically call the simulator with the :meth:`do` method.
    
    :param string name: Simulator name
    :param bool commandLine: Whether the simulator is run from the command line, or programatically.
    
    By default simulators are named for their class."""
    
    name = "Simulator"
    
    def __init__(self,name="__class__.__name__",commandLine=True,version=None):
        super(Simulator, self).__init__()
        self.stages = {}
        self.macros = {}
        self.functions = {}
        self.exclude = []
        self.include = []
        self.orders = []

        self.attempt = [] # Stages and dependents which have been attempted.        
        self.complete = [] # Stages and dependents which have been walked
        self.done = [] # Stages and dependents which have been checked
        self.ran = [] # Stages and dependents which have been executed
        self.aran = []
        self.name = name
        self.order = None
        self.config = StructuredConfiguration({})
        self.config.dn = DottedConfiguration
        self.config.load(resource_filename(__name__,"Defaults.yaml"))
        
        if name == "__class__.__name__":
            self.name = self.__class__.__name__
        if isinstance(name,str):
            self.name = self.name.encode('utf-8')
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
        self.progressbar = False
        self.commandLine = commandLine
        self.Caches = CacheManager()
        self._depTree = []
        
        if version==None:
            self.version = [u"AstroObject: " + __version__]
        else:
            self.version = [self.name + u": " + version,u"AstroObject: " + __version__]
        
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
        self.USAGE = u"%(command)s %(basicOpts)s %(subcommand)s"
        self.USAGEFMT = { 'command' : u"%(prog)s", 'basicOpts': u"[ options ][ configuration ]", 'subcommand' : u"{stages}" }
        
        HelpDict = { 'command': u"%(prog)s",'name': self.name }
        ShortHelp = u"""
        Command Line Interface for %(name)s.
        The simulator is set up in stages, which are listed below. 
        By default, the *all stage should run the important parts of the simulator.
        
        (*) Include      : To include a stage, use *stage. This will also run the dependents for that stage.
        (-) Exclude      : To exclude a stage, use -stage. 
        (+) Include-only : To include a stage, but not the dependents of that stage, use +stage.
        
        To run the simulater, use 
        $ %(command)s *all""" % HelpDict
        LongHelp = u"""This is a multi-function dynamic command line interface to a complex program. 
The base unit, stages, are individual functions which should be able to run independtly of each other. 
Stages can declare dependencies if they are not independent of each other. The command line interface
can be customized using the 'Default' configuration variable in the configuration file.
        """ % HelpDict
        
        self.parser = argparse.ArgumentParser(description=ShortHelp,
            formatter_class=argparse.RawDescriptionHelpFormatter,usage=self.USAGE % self.USAGEFMT,prefix_chars="-+*",epilog=LongHelp)
        
        # Parsers
        self.config_parser = self.parser.add_argument_group("configuration presets")
        self.pos_stage_parser = self.parser.add_argument_group('Single Use Stages')
        self.neg_stage_parser = self.parser.add_argument_group('Remove Stages')
        self.inc_stage_parser = self.parser.add_argument_group('action stages')
        
        # Add the basic controls for the script
        self.parser.add_argument('--version',action='version',version="\n".join(self.version))
        
        # Operational Controls
        self.registerConfigOpts('d',{'Debug':True},help="enable debugging messages and plots")
        
        # Config Commands
        self.parser.add_argument('--configure',action='append',metavar="Option.Key='literal value'",help="add configuration items in the form of dotted names and value pairs: Option.Key='literal value' will set config[\"Option.Key\"] = 'literal value'",dest='literalconfig')
        self.parser.add_argument('-c','--config-file',action='store',dest='config',type=str,help="use the specified configuration file",metavar="file.yaml")
        self.registerFunction('-p','--profile',self._show_profile,run='end',help="show a simulation profile")
        self.registerFunction('-n','--dry-run', self._dry_run, run='post',help="run the simulation, but do not execute stages.")
        self.registerFunction('--show-tree', self._show_dep_tree, run='end',help="show a dependcy tree of all stages run.")
        self.registerFunction('--show-stages',self._show_done_stages,run='end',help="show a flat list of all stages run.")
        self.registerFunction('--dump-config', self._dump_config,help="dump the configuration to a file, with extension .dump.yaml")
        self.registerFunction('--dump-full-raw', self._dump_full_config)
        self.registerFunction('--list-stages', self._list_stages, help="list all of the stages initialized in the simulator.")
        
        # Default Macro
        self.registerStage(None,"all",description="Run all stages",help="Run all stages",include=False)
        self.registerStage(None,"none",description="Run no stages",help="Run no stages",include=False)
        
        
    def _default_macros(self):
        """Sets up the ``*all`` macro for this system, specifically, triggers the ``*all`` macro to run last."""
        self.orders.remove("all")
        self.orders += ["all"]

        
    #########################
    ### REGISTRATION APIs ###
    #########################    
        
    def registerStage(self,stage,name=None,description=None,exceptions=None,include=None,help=False,dependencies=None,replaces=None,optional=False):
        """Register a stage for operation with the simulator. The stage will then be available as a command line option, and will be operated with the simulator. Stages should be registered early in the operation of the simulator (preferably in the initialization, after the simulator class itself has initialized) so that the program is aware of the stages for running. 
        
        :keyword function stage: The function to run for this stage. Should not take any arguments
        :keyword string name:  The command-line name of this stage (no spaces, `+`, `-`, or `*`)
        :keyword string description: A short description, which will be used by the logger when displaying information about the stage
        :keyword tuple exceptions: A tuple of exceptions which are acceptable results for this stage. These exceptions will be caught and logged, but will allow the simulator to continue. These exceptions will still raise errors in Debug mode.
        :keyword bool include: A boolean, Whether to include this stage in the `*all` macro or not.
        :keyword string help: Help text for the command line argument. A value of False excludes the help, None includes generic help.
        :keyword list dependencies: An ordered list of the stages which must run before this stage can run. Dependencies will be deep-searched.
        :keyword list replaces: A list of stages which can be replaced by this stage. This stage will now satisfy those dependencies.
        :keyword bool optional: A boolean about wheather this stage can be skipped. If so, warnings will not be raised when this stage is explicitly skipped (like ``-stage`` would do)
        
        
    	Stages are called with either a ``*``, ``+`` or ``-`` character at the beginning. Their resepctive actions are shown below.
	
    	========= ============ ================================
    	Character  Action      Description
    	========= ============ ================================
    	``*``     Include      To include a stage, use ``*stage``. This will also run the dependents for that stage.
    	``-``     Exclude      To exclude a stage, use ``-stage``. This stage (and it's dependents) will be skipped.
    	``+``     Include-only To include a stage, but not the dependents of that stage, use ``+stage``.
    	========= ============ ================================
        
        Stages cannot be added dynamically. Once the simulator starts running (i.e. processing stages) the order and settings are fixed. Attempting to adjsut the stages at this point will raise an error.
        """
        if self.running or self.starting:
            raise ConfigurationError("Cannot add a new stage to the simulator, the simulation has already started!")
        if name == None:
            name = stage.__name__
        name = name.replace("_","-")
            
        if name in self.stages:
            raise ValueError("Cannot have duplicate stage named %s" % name)
        
        if exceptions == None and hasattr(stage,'exceptions'):
            exceptions = stage.exceptions
        elif exceptions == None:
            exceptions = tuple()
        if exceptions == True:
            exceptions = Exception
        
        if dependencies == None and hasattr(stage,'dependencies'):
            dependencies = stage.dependencies
        elif dependencies == None:
            dependencies = []
        if not isinstance(dependencies,list):
            raise ValueError("Invalid type for dependencies: %s" % type(dependencies))
            
        if replaces == None and hasattr(stage,'replaces'):
            replaces = stage.replaces  
        elif replaces == None:
            replaces = []
        if not isinstance(replaces,list):
            raise ValueError("Invalid type for dependencies: %s" % type(replaces))
        
        if description == None and hasattr(stage,'description'):
            description = stage.description
        elif description == None and callable(stage):
            description = stage.__doc__
        elif not description:
            description = "Running %s" % name

        if (not help) and hasattr(stage,'help'):
            help = stage.help
        elif help == False:
            help = argparse.SUPPRESS
        elif help == None:
            help = "stage %s" % name

        if include == None and hasattr(stage,'include'):
            include = stage.include
        elif include == None:
            include = False    
        
        stageObject = Stage(stage,name=name,description=description,exceptions=exceptions,dependencies=dependencies,replaces=replaces,optional=optional)
        self.stages[name] = stageObject
        self.orders += [name]
        self.pos_stage_parser.add_argument("+"+name,action='append_const',dest='include',const=name,help=argparse.SUPPRESS)
        self.neg_stage_parser.add_argument("-"+name,action='append_const',dest='exclude',const=name,help=argparse.SUPPRESS)
        self.inc_stage_parser.add_argument("*"+name,action='append_const',dest='macro',const=name,help=help)
        if include:
            self.stages["all"].deps += [name]
        
    def registerFunction(self,*arguments,**kwargs):
        """Register a function to run using a flag.
        
        :param string argument: The calling argument, e.g. ``--hello-world``. Multiple arguments can be provided.
        :param function function: The function to be run. This should be the last comma separated argument.
        :keyword str help: Command line help for this function.
        :keyword str run: ('pre'|'post'|'end') Whether to run the function before or after configuration of the simulator, or at the end of the simulation.
        :keyword str name: An explicit function name.
        
        Functions registered with ``post=False`` will be run before the simulator is configured from a file. As such, changes they make can be easily re-adjusted by the user. Functions registered with ``post=True`` (the default) will run after configuration, but before any stages run. They can be used to inspect or adjust configuration variables or other globals.
        
        Other keyword arguments are passed to :meth:`ArgumentParser.add_argument`
        """
        if self.running or self.starting:
            raise ConfigureError("Cannot add macro after simulator has started!")

        help = kwargs.pop("help",argparse.SUPPRESS)
            
        run = kwargs.pop('run','post')
        runOpts = { 'post' : 'afterFunction' , 'pre' : 'beforeFunction', 'end' : 'endFunction'}
        if run not in runOpts:
            raise KeyError("Run option not supported: %s, %r" % (run,runOpts.keys()))
        
        arguments = list(arguments)
        function = arguments.pop()
        
        name = kwargs.pop('name',function.__name__)
        
        self.functions[name] = function
        
        self.parser.add_argument(*arguments,action='append_const',dest=runOpts[run],const=name,help=help,**kwargs)
        
        
    def registerConfigOpts(self,argument,configuration,preconfig=True,**kwargs):
        """Registers a bulk configuration option which will be provided with the USAGE statement. This configuration option can easily override normal configuration settings. Configuration provided here will override programmatically specified configuration options. It will not override configuration provided by the configuration file. These configuration options are meant to provide alterantive *defaults*, not alternative configurations.
        
        :param string argument: The command line argument (e.g. ``-D``)
        :param dict configuration: The configuration dictionary to be merged with the master configuration.
        :keyword bool preconfig: Applies these adjustments before loading the configuration file.
        
        Other keyword arguments are passed to :meth:`ArgumentParser.add_argument`
        """
        if self.running or self.starting:
            raise ConfigureError("Cannot add macro after simulator has started!")
        
        if "help" not in kwargs:
            help = argparse.SUPPRESS
        else:
            help = kwargs["help"]
            del kwargs["help"]
        if preconfig:
            dest = 'beforeConfigure'
        else:
            dest = 'afterConfigure'
        self.config_parser.add_argument("-"+argument,action='append_const',dest=dest,const=configuration,help=help,**kwargs)
        
    
    def setLongHelp(self,string):
        """Set the long epilogue help for the simulator. The long help will be printed at the end of the help documentation."""
        assert not self.starting, "Parsing has started, can't set long help!"
        assert not self.running, "Simulator is running, can't set long help!"
        self.parser.epilog = string
        
    def dir_filename(self,directory,filename):
        """Return a directory filename."""
        return "%(directory)s/%(filename)s" % { "directory" : self.config["Dirs"][directory] , "filename" : filename }
    
    #############################
    ### PUBLIC OPERATION APIs ###
    #############################
    
    def collect(self,matching=r'^(?!\_)',**kwargs):
        """Collect class methods for inclusion as simulator stages. Instance methods are collected if they do not belong to the parent :class:`Simulator` class (i.e. this method, and others like :meth:`registerStage` will not be collected.). Registered stages will default to having no dependents, to be named similar to thier own methods (``collected_stage`` becomes ``*collected-stage`` on the command line) and will use thier doc-string as the stage description. The way in which these stages are collected can be adjusted using the decorators provided in this module.
        
        To define a method as a stage with a dependent, help string, and by default inclusion, use::
            
            @collect
            @include
            @description("Doing something")
            @help("Do something")
            @depends("other-stage")
            @replaces("missing-stage")
            def stagename(self):
                pass
        
        This method does not do any logging. It should be called before the :meth:`run` method for the simulator is called.
        
        Private methods are not included using the default matching string ``r'^(?!\_)'``. This string excludes any method beginning with an underscore. Alternative method name matching strings can be provided by the user.
        
        :param string matching: Regular expression used for matching method names.
        :param kwargs: Keyword arguments passed to the :meth:`registerStage` function.
        
        """
        genericList = dir(Simulator)
        currentList = dir(self)
        stageList = []
        for methodname in currentList:
            if methodname not in genericList:
                method = getattr(self,methodname)
                if callable(method) and ( re.search(matching,methodname) or getattr(method,'collect',False) ) and ( not getattr(method,'ignore',False) ):
                    stageList.append(method)
                    
        stageList.sort(key=func_lineno)
        [ self.registerStage(stage,**kwargs) for stage in stageList ]
    
    
    def run(self):
        """Run the actual simulator. This command handles simulators which can be run from the command line. Calling :meth:`run` will run all of the stages specified on the command line. If you do not want this effect, use :meth:`startup` to prepare the simulator, and :meth:`do` to run the actual simulator. Calling :meth:`exit` at the end will allow the simulator to close out and perform any output tasks, but will also end the current python session."""
        self.startup()
        try:
            self.do()
        except Exception:
            raise
        finally:
            self.exit()
    
    def startup(self):
        """Start up the simulation. This function handles the configuration of the system, and prepares for any calls made to :meth:`do`."""
        self._default_macros()
        self.starting = True
        self._parseArguments()
        self._preConfiguration()
        self._configure()
        self._postConfiguration()
        for vstr in self.version:
            self.log.info(vstr)
        self.starting = False
                
    def do(self,*stages):
        """Run the simulator.
        
        :argument stages: Stages to be run as macros.
        
        This command can be used to run specific stages and their dependents. The control is far less flow control than the command-line interface (there is currently no argument interface to inclusion and exclusion lists, ``+`` and ``-``.), but can be used to call single macros in simulators froms scripts. In these cases, it is often beneficial to set up your own macro (calling :func:`registerStage` with ``None`` as the stage action) to wrap the actions you want taken in each phase.
        
        It is possible to stop execution in the middle of this function. Simply set the simulator's ``paused`` variable to ``True`` and the simulator will remain in a state where you are free to call :meth:`do` again."""
        if self.running and not self.paused:
            raise ConfigurationError(u"Simulator is already running!")
        elif self.paused:
            self.pasued = False
            self.config["Options.macro"] += list(stages)
        else:
            self.running = True
            self.config["Options.macro"] += list(stages)
            if self.config["Options.macro"] == []:
                if self.config["Default"]:
                    self.config["Options.macro"] = self.config["Default"]
                else:
                    self.parser.error(u"No stages triggered to run!")
            if self.attempt == []:
                self.inorder = True
                self.complete = []
        
        for stage in self.orders:
            if stage in self.config["Options.macro"]:
                self.execute(stage)
            elif stage in self.config["Options.include"]:
                self.execute(stage,deps=False)
        self.running = False
    
    
    def execute(self,stage,deps=True,level=0):
        """Actually exectue a particular stage. This function can be called to execute individual stages, either with or without dependencies. As such, it gives finer granularity than :func:`do`.
        
        :param string stage: The stage name to be exectued.
        :param bool deps: Whether to run all dependencies.
        
        This method handles exceptions from the called stages, including keyboard interrupts.
        """
        if self.paused or not self.running:
            return False
            
        if stage not in self.stages:
            self.log.critical("Stage %s does not exist." % stage)
            self.exit(1)
        use = True
        if stage in self.config["Options.exclude"]:
            use = False
        if stage in self.config["Options.include"]:
            use = True
        if stage in self.attempt:
            return use
        if not use:
            return use
        
        self.attempt += [stage] + self.stages[stage].reps
         
        if deps:
            
            for dependent in self.orders:
                if dependent in self.stages[stage].deps:
                    if dependent not in self.attempt:
                        self.execute(dependent,level=level+1)
                    else:
                        self._depTree += ["%-30s : (done already)" % (u"  " * (level+1) + u"└ %s" % dependent)]
                    if dependent not in self.complete:
                        if self.stages[dependent].optional:
                            self.log.debug(u"Stage '%s' requested by '%s' but skipped" % (dependent,stage))
                        else:
                            self.log.warning(u"Stage '%s' required by '%s' but failed to complete." % (dependent,stage))
        else:
            self.log.warning(u"Explicity skipping dependents")
        
        s = self.stages[stage]
        indicator = u"└>%s" if level else u"=>%s"
        self._depTree += ["%-30s : %s" % (u"  " * level + indicator % stage,s.description)]
        if s.macro or self.config["Options.DryRun"]:
            self.complete += [stage] + s.reps
            self.done += [stage]
            return use
        
        self.log.debug("Starting \'%s\'" % s.name)
        self.log.info(u"%s" % s.description)
        
        try:
            s.run()
        except KeyboardInterrupt as e:
            self.log.useConsole(True)
            self.log.critical("Keyboard Interrupt during %(stage)s... ending simulator." % {'stage':s.name})
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
            self.log.critical(u"Error %(name)s in stage %(stage)s:'%(desc)s'!" % { 'name' : e.__class__.__name__, 'desc' : s.description, 'stage' : s.name } )
            self.log.critical(u"Error: %(msg)s" % { 'msg' : e } )
            raise
        else:
            self.log.debug(u"Completed '%s' and %r" % (s.name,s.reps))
            self.complete += [stage] + s.reps
            self.ran += [stage]
            self.done += [stage]
        finally:
            self.aran += [stage]
            self.log.debug(u"Finished '%s'" % s.name)
        
        return use
        
    def exit(self,code=0,msg=None):
        """This function exist the current python instance with the requested code. Before exiting, a message is printed.
        
        :param int code: exit code
        :param string msg: exit message
        
        """
        for fk in self.config.get("Options.endFunction",[]):
            self.functions[fk]()
        if msg:
            self.log.info(msg)
        self.log.info(u"Simulator %s Finished" % self.name)
        if code != 0:
            sys.exit(code)
        

    
    def map(self,function,collection=[],idfun=str,exceptions=True,color="green"):
        """Map a function over a given collection."""
        if exceptions == True:
            exceptions = Exception
        
        self.errors = []
        
        if not self.progressbar and color:
            self._start_progress_bar(len(collection),color)
            showBar = True
        else:
            showBar = False
        
        try:
            map(lambda i:self._collection_map(i,function,exceptions,idfun,showBar),collection)
        except:
            raise
        finally:       
            if showBar:
                self._end_progress_bar()
            ferr = float(len(self.errors)) / float(len(collection))
            if ferr > 0.1:
                self.log.warning(u"%d%% of iterations had errors." % (ferr * 100.0))
                self.log.warning(u"See the log for Errors.")
            if len(self.errors) > 0:
                self.log.warning(u"Trapped %d errors" % len(self.errors))
                for error in self.errors:
                    self.log.debug(u"Error %s caught" % error)
    
    def map_over_collection(self,function,idfun=str,collection=[],exceptions=True,color="green"):
        """docstring for map_over_collection"""
        self.map(function,collection,idfun,exceptions,color)
    
    
    ##################################
    ### INTERNAL OPERATING METHODS ###
    ##################################
    
    def _parseArguments(self):
        """Parse arguments. Argumetns can be passed into this function like they would be passed to the command line. These arguments will only be parsed when the system is not in `commandLine` mode."""
        if self.commandLine:
            Namespace = self.parser.parse_args()
            self.config["Options"].merge(vars(Namespace))
            self.config["Options.Parsed"] = True
            self.log.log(2,"Parsed command line arguments")
        elif not self.config["Options.Parsed"]:
            Namespace = self.parser.parse_args("")
            self.config["Options"].merge(vars(Namespace))
            self.config["Options.Parsed"] = True
            self.log.log(2,"Parsed default line arguments")
        else:
            self.log.debug("Skipping argument parsing")
        
        for key in self.config["Options"].keys():
            if self.config["Options"][key] == None:
                del self.config["Options"][key]
        
    
    def _preConfiguration(self):
        """Applies arguments before configuration. Only argument applied is the name of the configuration file, allowing the command line to change the configuration file name."""
        if self.config.get("Options.config",False):
            self.config.setFile(self.config["Options.config"],"Options")
        for fk in self.config.get("Options.beforeFunction",[]):
            self.functions[fk]()
        for cfg in self.config.get("Options.beforeConfigure",[]):
            self.config.merge(cfg)
        
    
    def _configure(self):
        """Loads the default configuration file, and writes the configuration to a partial file."""
        if self.running:
            return ConfigurationError("Cannot configure the simulator, the simulation has already started!")
        if self.configured:
            raise ConfigurationError("%s appears to be already configured" % (self.name))

        self.configured |= self.config.load()
        self.log.debug("Updated Configuration from default file %s" % self.config["Configurations.This"])            
                
        if not self.configured:
            self.log.log(8,"No configuration provided or accessed. Using defaults.")
        
        # Start Logging
        self.log.configure(configuration=self.config)
        self.log.start()
        
        # Write Configuration to Partials Directory
        if os.path.isdir(self.config["Dirs.Partials"]):
            filename = self.dir_filename("Partials","%s.config.yaml" % self.name)
            self.config.save(filename)
    
            
    def _postConfiguration(self):
        """Apply arguments after configuration. The arguments applied here flesh out macros, and copy data from the configuration system into the operations system."""
        if not isinstance(self.config.get("Options.exclude",False),list):
            self.config["Options.exclude"] = []
        if not isinstance(self.config.get("Options.include",False),list):
            self.config["Options.include"] = []
        if not isinstance(self.config.get("Options.macro",False),list):
            self.config["Options.macro"] = []
        for item in self.config.get("Options.literalconfig",[]):    
            key,value = item.split("=")
            try:
                self.config[key] = literal_eval(value)
            except:
                self.config[key] = value
        for cfg in self.config.get("Options.afterConfigure",[]):
            self.config.merge(cfg)
        for fk in self.config.get("Options.afterFunction",[]):
            self.functions[fk]()

    ############################################
    ### INTERNAL FUNCTION INTROSPECTION APIs ###
    ############################################    
        
    def _list_stages(self):
        """List stages and exit"""
        text = "Stages:\n"
        for stage in self.orders:
            s = self.stages[stage]
            text += "%(command)-20s : %(desc)s" % {'command':s.name,'desc':s.description}
            text += "\n"
        self.exit(msg=text)
    
    def _dump_full_config(self):
        """docstring for _dump_full_config"""
        filename = self.config["Configurations.This"].rstrip(".yaml")+".fdump.yaml"
        self.config.save(filename)        
        
    def _dump_config(self):
        """Dump the configuration to a file"""
        filename = self.config["Configurations.This"].rstrip(".yaml")+".dump.yaml"
        config = self.config.store
        del config["Options"]
        config.save(filename) 
        
    def _dry_run(self):
        """Trigger a dry run"""
        self.config["Options.DryRun"] = True
        
    def _show_done_stages(self):
        """Dry Run"""
        text = [u"Stages done, in order:"]
        order = 1
        for stage in self.done:
            s = self.stages[stage]
            text += [u"%(order)3d. %(command)-20s : %(desc)s" % {'order':order,'command':s.name,'desc':s.description}]
            order += 1
        self.log.info(u"\n".join(text))

    def _show_dep_tree(self):
        """Dependency Tree"""
        self._depTree.reverse()
        text = u"Dependency Tree, request order:\n"
        text += "\n".join(self._depTree)
        self.log.info(text)
        
    def _show_profile(self):
        """Show the profile of the simulation"""
        
        total = sum([ self.stages[stage].durTime for stage in self.aran])
        
        text = [u"Simulation profile:"]
        text += [Stage.table_head()]
        
        for stage in self.aran:
            text += [self.stages[stage].table_row(total)]
            
        text += [Stage.table_foot(total)]
            
        self.log.info(u"\n".join(text))
            
    
    #################################
    ### INTERNAL HELPER FUNCTIONS ###
    #################################
    
    def _start_progress_bar(self,length,color):
        """Return a progress bar object of a specified color in the standard format."""
        widgets = [Percentage(),' ',ColorBar(color=color),' ',ETA()]
        self.progressbar = ProgressBar(widgets=widgets,maxval=length).start()
        self.progress = 0
        self.log.useConsole(False)
        return self.progressbar
        
    def _end_progress_bar(self):
        """End the progressbar object's operation"""
        self.progressbar.finish()
        self.log.useConsole(True)
        self.progressbar = False
        self.progress = 0
    
    def _collection_map(self,i,function,exceptions,idfun,showBar):
        """Maps something over a bunch of lenslets"""
        identity = idfun(i)
        if showBar:
            self.progressbar.update(self.progress)
        try:
            function(i)
        except exceptions as e:
            self.log.error(u"Caught %s in %r" % (e.__class__.__name__,identity))
            self.log.error(u"%s" % e)
            self.errors += [e]
            if self.config["Debug"]:
                raise
        finally:
            if showBar:
                self.progress += 1.0
                self.progressbar.update(self.progress)


def optional(optional=True):
    """Makes this object optional"""
    if callable(optional) or optional:
        func = optional
        func.optional = True
        return func
    def decorate(func):
        func.optional = optional
        return func
    return decorate
    
def description(description):
    """Gives this object a description"""
    def decorate(func):
        func.description = description
        return func
    return decorate
    

def include(include=True):
    """Commands this object to be included"""
    if callable(include):
        func = include
        func.include = True
        return func
    def decorate(func):
        func.include = include
        return func
    return decorate

def replaces(*replaces):
    """Registers replacements for this stage"""
    def decorate(func):
        func.replaces = list(replaces)
        return func
    return decorate

def help(help):
    """Registers a help string for this function"""
    def decorate(func):
        func.help = help
        return func
    return decorate

def depends(*dependencies):
    """Registers dependencies for this function"""
    def decorate(func):
        func.dependencies = list(dependencies)
        return func
    return decorate

def excepts(*exceptions):
    """Registers exceptions for this function."""
    def decorate(func):
        func.exceptions = tuple(exceptions)
        return func
    return decorate

def collect(collect=True):
    """Include stage explicitly in collection"""
    if callable(collect):
        func = collect
        func.collect = True
        return func
    def decorate(func):
        func.collect = collect
        return func
    return decorate
    

def ignore(ignore=True):
    """Ignore stage explicitly in collection"""
    if callable(ignore):
        func = ignore
        func.ignore = True
        return func
    def decorate(func):
        func.ignore = ignore
        return func
    return decorate
    

def on_instance_collection(get_collection,idfun=str,exceptions=True,color="green"):
    """Decorator for acting a specific method over a collection"""
    def decorate(func):
        name = func.__name__
        def newfunc(self):
            self.map_over_collection(lambda i: func(self,i),idfun,get_collection(self),exceptions,color)
        newfunc = make_decorator(func)(newfunc)
        return newfunc
    return decorate
    
def on_collection(collection,idfun=str,exceptions=True,color="green"):
    """Decorator for acting a specific method over a collection"""
    def decorate(func):
        name = func.__name__
        def newfunc(self):
            self.map_over_collection(lambda i: func(self,i),idfun,collection,exceptions,color)
        newfunc = make_decorator(func)(newfunc)
        return newfunc
    return decorate
    
