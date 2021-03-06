# -*- coding: utf-8 -*-
# 
#  simulator.py
#  AstroObject
#  
#  Created by Alexander Rudy on 2011-12-14.
#  Copyright 2011 Alexander Rudy. All rights reserved.
#  Version 0.6.1
# 
"""
:mod:`simulator` — Complex Task Management 
===============================================

The Simulator is designed to provide a high level, command-line useful interface to large computational tasks. As the name suggests, Simulators often do a lot of programming work, and do so across many distinct "stages", whcih can be configured in any way the user desires. All of the abilities in this program are simply object abstraction techniques to provide a complex program with a command line interface and better control and reporting on the activities carreid out to successfully complete the program. It allows for the configuration of simple test cases and "macros" from within the program, eliminating the need to provide small wrapper scripts and test handlers.

An example (simple) program using the simulator can be found in :ref:`SimulatorExample`

.. _Simulator_CLI:

:program:`Simulator` Command Line Interface
-------------------------------------------

The master simulator program is a command-line interface to the :meth:`AstroObject.simulator.Simulator.run` method. Below are the major command line components.

Usage Statement ::
	
	Simulator [ options ][ configuration ] {stages}
	
The program is actually agnostic to the order of arguments. Any argument may come in any position. As such, all arguments must be unique.

.. program:: Simulator

.. option:: {stages}
	
	The stages option specifies individual stages for the program to run. You must specify at least one stage to run in the simulator. By default, two basic stages are provided, ``*all`` and ``*none``. The default simulation is performed by ``*all``. To test the simulator without running any stages (for example, to test :meth:`AstroObject.simulator.Simulator.registerFunction` functionality), use the ``*none`` stage to opertate without using any stages.
	
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
	
	Stages are registered by the :meth:`AstroObject.simulator.Simulator.registerStage` method.
	
.. option:: [configurations]
	
	Configuration options override defaults set up in :class:`AstroObject.simulator.Simulator`. As such, they are useful quick changes to a configuration.
	
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
	
.. option:: --configure Option.Key='literal value'

    Apply a dotted-name style configuration item to the configure variables. The value will be set as either a python literal, or a plain string. If the value parses as a python literal, that will be used. If parsing the value as a literal fails, the string will be used. As such, strings do not need to be quoted on the command line.
    ::
        
        $ sim --configure Option.Key=Value
        
    has the same effect as::
        
        try:
            sim.config["Option.Key"] = Value
        except:
            sim.config["Option.Key"] = "Value"
    
.. option:: -c file.yaml, --config-file file.yaml
	
	Set the name of the configuration file to use. By default, the configuation file is called `SED.main.config.yaml`. This will be the filename used for dumping configurations with the :option:`--dump` command (Dump will append the extension ``-dump.yaml`` onto the filename to prevent overwriting exisitng configurations)
	
.. option:: --p, --profile
    
    Show a timing profile of the simulation, including status of stages, at the end of the simulation.

.. option:: -n, --dry-run
	
	Traverse all of the stages to be run, printing them as the program goes, but do not run any stages.

.. option:: --show-tree
    
    Show a dependency tree for the simulator.
	
.. option:: --show-stages
    
    Show all of the stages ran for this simulation.    
    
.. option:: --dump-config
    
    Dump the configuration to a file. Filenames are the configuration file name with ``-dump.yaml`` appended.
    
.. option:: --list-stages
    
    Print all stages registered in the simulator. Any stage listed in the output of this function can be run.
    
.. _Configuration:

:program:`Simulator` Configuration Files
----------------------------------------

:program:`Simulator` configuration files are YAML files which contain a dictionary structure. All values in the YAML files are basic yaml, and contain no python-specific directives. To find out what the default or current configuration is, use the :option:`--dump` command. The file produced from this will contain a YAML structure for the configuration in use when the system started up. The various directives in the configuration file are described below. Configuration options are described using the dotted-syntax described in :mod:`AstroObject.config`

- ``Configurations``: contains a list of potential configuration files.
- ``Configurations.Main``: The name of the primary configuration file. This default is produced by the program. Overriding it in the configuration file has essentially no effect.
- ``Default``: The default macro to run (i.e. the default ``*``'d argument.)
- ``Dirs``: Directories that this simulator will use for output.
- ``Dirs.Caches``: Location of cache files.
- ``Dirs.Logs``: Location of log files.
- ``Dirs.Partials``: Location of partial output, including a dump of the configuration.
- ``Options``: The dictionary for storing command line options.
- ``Options.DryRun``: Whether to skip actually executing stages.
- ``Logging``: Configuration of the :mod:`AstroObject.loggers` module

A simple configuration file can be found in the :ref:`SimulatorExample`.

.. _Simulator_API:

API Methods
-----------
    
The following methods handle the external-API for the simulator. Normally, when you write a simulator, you will subclass the :class:`Simulator`, and then use the methods here to control the behavior of the simulator. At a minimum, a simulator must register stages, probably using :meth:`Simulator.collect` or :meth:`Simulator.registerStage`, and then call the :meth:`Simulator.run` function to process the command line interface and start the simulator.
    
.. autoclass::
    AstroObject.simulator.Simulator
    
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
The following decorators can be used (in conjuction with :meth:`AstroObject.simulator.Simulator.collect`) to register and configure simulator stages:

.. autofunction:: collect

.. autofunction:: ignore

.. autofunction:: include

.. autofunction:: help

.. autofunction:: description

.. autofunction:: depends

.. autofunction:: triggers

.. autofunction:: replaces

.. autofunction:: optional

.. autofunction:: excepts

.. autofunction:: on_collection

.. autofunction:: on_instance_collection
    
Private Methods and Classes
---------------------------
    
These methods are used to implment the public-facing API. They are documented here to explain their use in development.

.. inheritance-diagram::
    AstroObject.simulator.Simulator
    AstroObject.simulator.Stage
    :parts: 1

.. automethod:: 
    AstroObject.simulator.Simulator._initOptions

.. automethod:: 
    AstroObject.simulator.Simulator._default_macros
    
.. automethod:: 
    AstroObject.simulator.Simulator._parseArguments
    
.. automethod:: 
    AstroObject.simulator.Simulator._preConfiguration
    
.. automethod:: 
    AstroObject.simulator.Simulator._configure
    
.. automethod:: 
    AstroObject.simulator.Simulator._postConfiguration

.. automethod:: 
    AstroObject.simulator.Simulator.execute
    
.. autoclass::
    AstroObject.simulator.Stage


"""


# Standard Python Modules
import math, copy, sys, time, os, json, datetime
import re
import argparse
import yaml
from ast import literal_eval

from pkg_resources import resource_filename

import multiprocessing

# Submodules from this system
from .cache import *
from .config import StructuredConfiguration, DottedConfiguration
from .loggers import *

import util.pbar as progressbar
import util.terminal as terminal
from util import getVersion, npArrayInfo, func_lineno, make_decorator

__all__ = ["Simulator","on_collection","help","replaces","excepts","depends","triggers","include","optional","description","collect","ignore","on_instance_collection"]

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
    def __init__(self,stage,name="a Stage",description=None,exceptions=None,dependencies=None,replaces=None,triggers=None,optional=False):
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
        self.trig = triggers
        self.optional = optional
        self.startTime = None
        self.endTime = None
        self.ran = False
        self.complete = False
    
    @property
    def name(self):
        return self._name
    
    @staticmethod
    def table_head(term=True):
        """Table head for profiling."""
        if term:
            text  = u""
            text += terminal.render(u"|%(BLUE)s-----------------------%(NORMAL)s|%(BLUE)s--------%(NORMAL)s|%(BLUE)s---------------%(NORMAL)s|\n")
            text += u"|         Stage         | Passed |     Time      |\n"
            text += terminal.render(u"|%(BLUE)s-----------------------%(NORMAL)s|%(BLUE)s--------%(NORMAL)s|%(BLUE)s---------------%(NORMAL)s|")
        else:
            text  = ""
            text += "|-----------------------|--------|---------------|\n"
            text += "|         Stage         | Passed |     Time      |\n"
            text += "|-----------------------|--------|---------------|"
        return text
      
    @staticmethod 
    def table_foot(total,term=True):
        """Table footer for profiling."""
        if term:
            text = terminal.render(u"|%(BLUE)s-----------------------%(NORMAL)s Total Time: ")+u"%(time)-9s"+terminal.render(u"%(BLUE)s---%(NORMAL)s|")
        else:
            text = "|----------------------- Total Time: "+"%(time)-9s"+"---|"
        text = text % {"time":datetime.timedelta(seconds=int(total))}
        return text
        
    def table_row(self,total=None,term=True):
        """Return a profiling string table row.
        ::
            
            >>> stage.table_row()
            |                 other |   True |  0:00:00   0% |
            
        
        """
        assert self.ran, "Stage %s didn't run" % self.name
        string =  u"| %(stage)21s | %(color)s%(result)6s%(normal)s | %(timestr) 12s |"
        if self.complete:
            color = terminal.GREEN
        elif self.optional:
            color = terminal.BLUE
        else:
            color = terminal.RED
        
        keys = {
                "stage": self.name,
                "color": color,
                "normal": terminal.NORMAL,
                "result": str(self.complete),
                "time": datetime.timedelta(seconds=int(self.durTime)),
            }
        if not term:
            keys["color"] = ""
            keys["normal"] = ""
        if total == None or total == 0:
            keys["timestr"] = u"% 12s" % keys["time"]            
        elif term:
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
            blen -= 1
            string += u"█" * blen
            string += terminal.NORMAL + "|"
            keys["timestr"] = u"%(time)8s %(per)3d%%" % keys
        else:
            keys["per"] = ( self.durTime / total ) * 100.0
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

class SimulatorStateError(Exception):
    """An error due to the state of the simulator."""
    pass
    
class SimulatorPause(Exception):
    """Exception indicating that the simulator is paused."""
    pass
    

class Simulator(object):
    """A Simulator, used for running large segements of code with detailed logging and progress checking. Simulators have a name, the `name` parameter can be left as is to use the name of the simulator's class (mostly useful if you subclassed it!). The `commandLine` parameter can be set to False to prevent the simulator collecting arguments from `sys.argv` for use. This allows you to programatically call the simulator with the :meth:`do` method.
    
    :param string name: Simulator name
    :param bool commandLine: Whether the simulator is run from the command line, or programatically.
    
    By default simulators are named for their class."""
    
    name = "Simulator"
    
    def __init__(self, name="__class__.__name__", commandLine=True, version=None, caches=True, **kwargs):
        super(Simulator, self).__init__(**kwargs)
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
        self.order = None
        self.use_caches = caches
        
        self.name = name        
        if name == "__class__.__name__":
            self.name = self.__class__.__name__
        if isinstance(name,str):
            self.name = self.name.encode('utf-8')
        
        self.log = logging.getLogger("%s.%s" % (__name__,self.name))
        self.logging = False
        logging.getLogger(__name__.split(".")[0]).init_buffer()
        
        self.config = StructuredConfiguration({})
        self.config.dn = DottedConfiguration
        self.config.load(resource_filename(__name__,"Defaults.yaml"))
        
        
        # The following are boolean state values for the simulator
        self._reset()
        self.commandLine = commandLine
        self._depTree = []
        
        if version==None:
            self.version = [u"%s: " % __name__.split(".")[0] + __version__]
        else:
            self.version = [self.name + u": " + version,u"AstroObject: " + __version__]
        
        self._initOptions()
    
    def _reset(self):
        """Re-set flag variables to initial states."""
        self.configured = False
        self.running = False
        self.plotting = False
        self.debugging = False
        self.caching = True
        self.starting = False
        self.started = False
        self.paused = False
        self.progressbar = False
        
        
    def _initOptions(self):
        """Initializes the command line options for this script. This function is automatically called on construction, and provides the following default command options which are already supported by the simulator:
        
        Command line options are:
        
        =========================================== =====================
        CLI Option                                  Description
        =========================================== =====================
        ``--version``                               Display version information about this module
        ``--configure Option.Key=Value``            Set a configuration value on the command line. 
        ``-c file.yaml, --config-file file.yaml``   Specify a configuration file
        ``-n, --dry-run``                           Print the stages this command would have run.
        ``--show-tree``                             Show a dependency tree for the simulation
        ``--show-stages``                           List all of the used stages for the simulation
        ``--dump-config``                           Write the current configuration to file
        ``--list-stages``                           Print the stages that the command will execute, do not do anything
        =========================================== =====================
        
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
        self.cache_parser = self.parser.add_argument_group("caching control")
        self.pos_stage_parser = self.parser.add_argument_group('Single Use Stages')
        self.neg_stage_parser = self.parser.add_argument_group('Remove Stages')
        self.inc_stage_parser = self.parser.add_argument_group('action stages')
        
        # Add the basic controls for the script
        self.parser.add_argument('--version',action='version',version="\n".join(self.version))
        
        # Operational Controls
        self.registerConfigOpts('d',{'Debug':True},help="enable debugging messages and plots")
        
        # Caching Controls
        self.registerConfigOpts('-clean-cache',{'Cache':{'Clear':True},}, help="clean out caches",iscache=True)
        self.registerConfigOpts('-clean-all-cache',{'Cache':{'ClearAll':True},}, help="clean out all caches",iscache=True)
        self.registerConfigOpts('-no-cache',{'Cache':{'Use':False},}, help="Do not save or load from cache files",iscache=True)
        
        # Config Commands
        self.parser.add_argument('--configure',action='append',metavar="Option.Key='literal value'",help="add configuration items in the form of dotted names and value pairs: Option.Key='literal value' will set config[\"Option.Key\"] = 'literal value'",dest='literalconfig')
        self.parser.add_argument('-c','--config-file',action='store',dest='config',type=str,help="use the specified configuration file",metavar="file.yaml")
        self.registerFunction('-p','--profile',self._show_profile,run='end',help="show a simulation profile")
        self.registerFunction('-pp','--print-profile',self._print_profile,run='end')
        self.registerFunction('-n','--dry-run', self._dry_run, run='post',help="run the simulation, but do not execute stages.")
        self.registerFunction('--show-tree', self._show_dep_tree, run='end',help="show a dependcy tree of all stages run.")
        self.registerFunction('--show-stages',self._show_done_stages,run='end',help="show a flat list of all stages run.")
        self.registerFunction('--dump-config', self._dump_config, help="dump the configuration to a file, with extension .dump.yaml")
        self.registerFunction('--dump-full-raw', self._dump_full_config)
        self.registerFunction('--list-stages', self._list_stages, run='end', help="list all of the stages initialized in the simulator.")
        
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
        
    def registerStage(self,stage,name=None,description=None,exceptions=None,include=None,help=False,dependencies=None,replaces=None,triggers=None,optional=False):
        """Register a stage for operation with the simulator. The stage will then be available as a command line option, and will be operated with the simulator. Stages should be registered early in the operation of the simulator (preferably in the initialization, after the simulator class itself has initialized) so that the program is aware of the stages for running. 
        
        :keyword function stage: The function to run for this stage. Should not take any arguments
        :keyword string name:  The command-line name of this stage (no spaces, `+`, `-`, or `*`)
        :keyword string description: A short description, which will be used by the logger when displaying information about the stage
        :keyword tuple exceptions: A tuple of exceptions which are acceptable results for this stage. These exceptions will be caught and logged, but will allow the simulator to continue. These exceptions will still raise errors in Debug mode.
        :keyword bool include: A boolean, Whether to include this stage in the `*all` macro or not.
        :keyword string help: Help text for the command line argument. A value of False excludes the help, None includes generic help.
        :keyword list dependencies: An ordered list of the stages which must run before this stage can run. Dependencies will be deep-searched.
        :keyword list replaces: A list of stages which can be replaced by this stage. This stage will now satisfy those dependencies.
        :keyword list triggers: A list of stages which should be triggered by this stage. These stages will be run if they occur (are registered) after this stage.
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
            raise SimulatorStateError("Cannot add a new stage to the simulator, the simulation has already started!")
        if name == None:
            name = stage.__name__
        name = name.replace("_","-")
            
        if name in self.stages:
            raise ValueError("Cannot have duplicate stage named %s" % name)
        
        if hasattr(stage,'optional'):
            optional = stage.optional
        
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
        
        if triggers == None and hasattr(stage,'triggers'):
            triggers = stage.triggers
        elif triggers == None:
            triggers = []
        if not isinstance(triggers,list):
            raise ValueError("Invalid type for triggers: %s" % type(triggers))
            
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
        
        stageObject = Stage(stage,name=name,description=description,exceptions=exceptions,dependencies=dependencies,replaces=replaces,triggers=triggers,optional=optional)
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
        
        help = kwargs.pop("help",argparse.SUPPRESS)
            
        run = kwargs.pop('run','post')
        runOpts = { 'post' : 'afterFunction' , 'pre' : 'beforeFunction', 'end' : 'endFunction'}
        if run not in runOpts:
            raise KeyError("Run option not supported: %s, %r" % (run,runOpts.keys()))
        
        arguments = list(arguments)
        function = arguments.pop()
        
        name = kwargs.pop('name',function.__name__)
        
        self.functions[name] = function
        
        if len(arguments) < 1 and not self.running:
            self.config["Options"].update({ runOpts[run] : [name] })
        elif not self.running and not self.starting:
            self.parser.add_argument(*arguments,action='append_const',dest=runOpts[run],const=name,help=help,**kwargs)
        else:         
            raise SimulatorStateError("Cannot add function after simulator has started!")
            
        
    def registerConfigOpts(self,argument,configuration,preconfig=True,**kwargs):
        """Registers a bulk configuration option which will be provided with the USAGE statement. This configuration option can easily override normal configuration settings. Configuration provided here will override programmatically specified configuration options. It will not override configuration provided by the configuration file. These configuration options are meant to provide alterantive *defaults*, not alternative configurations.
        
        :param string argument: The command line argument (e.g. ``-D``)
        :param dict configuration: The configuration dictionary to be merged with the master configuration.
        :keyword bool preconfig: Applies these adjustments before loading the configuration file.
        
        Other keyword arguments are passed to :meth:`ArgumentParser.add_argument`
        """
        if self.running or self.starting:
            raise SimulatorStateError("Cannot add macro after simulator has started!")
        
        if "help" not in kwargs:
            help = argparse.SUPPRESS
        else:
            help = kwargs["help"]
            del kwargs["help"]
        
        iscache = kwargs.pop('iscache',False)    
        
        if preconfig:
            dest = 'beforeConfigure'
        else:
            dest = 'afterConfigure'
        if iscache:
            self.cache_parser.add_argument("-"+argument,action='append_const',dest=dest,const=configuration,help=help,**kwargs)
        else:
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
    
    def collect(self, matching=r'^(?!\_)', genericClasses=(), **kwargs):
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
        for gClass in genericClasses:
            genericList += dir(gClass)
        currentList = dir(self)
        stageList = []
        for methodname in currentList:
            if (methodname not in genericList):
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
        # Write Configuration to Partials Directory
        self._setupCaching()
        if os.path.isdir(self.config["Dirs.Partials"]) and self.commandLine:
            filename = self.dir_filename("Partials","%s.config.yaml" % self.name)
            self.config.save(filename)
        self.starting = False
        self.started = True
                
    def do(self,*stages):
        """Run the simulator.
        
        :argument stages: Stages to be run as macros.
        
        This command can be used to run specific stages and their dependents. The control is far less flow control than the command-line interface (there is currently no argument interface to inclusion and exclusion lists, ``+`` and ``-``.), but can be used to call single macros in simulators froms scripts. In these cases, it is often beneficial to set up your own macro (calling :func:`registerStage` with ``None`` as the stage action) to wrap the actions you want taken in each phase.
        
        It is possible to stop execution in the middle of this function. Simply raise an :exc:`SimulatorPause` exception and the simulator will return, and remain in a state where you are free to call :meth:`do` again."""
        if not self.started:
            raise SimulatorStateError("Simulator has not yet started!")
        elif self.running and not self.paused:
            raise SimulatorStateError(u"Simulator is already running!")
        elif self.paused:
            self.pasued = False
            macro += list(stages)
        else:
            self.running = True
            self.macro = []
            self.include = []
            self.macro += self.config["Options.macro"]
            self.macro += list(stages)
            self.include += self.config["Options.include"]
            if self.attempt == []:
                self.inorder = True
                self.complete = []
        if len(self.macro) == 0 and self.config["Default"] is not None:
            self.macro += self.config.get("Default",[])
        if len(self.macro) == 0:
            self.parser.error(u"No stages triggered to run!")
        self.trigger = []
        try:
            stage,code = self.next_stage(None,dependencies=True)
            while code != "F":
                self.execute(stage,code=code)
                stage,code = self.next_stage(None,dependencies=True)
        except SimulatorPause:
            self.paused = True
        else:
            self.running = False
        return self.complete
    
    def next_stage(self,parent,dependencies=False):
        """Return the name of the next stage"""
        for stage in self.orders:
            if stage not in self.attempt and stage not in self.complete:
                if parent is not None and stage in self.stages[parent].deps:
                    return stage,"D"
                elif stage == parent:
                    return stage,"C"
                elif parent is None:
                    if stage in self.macro:
                        return stage,"M"
                    if stage in self.include:
                        return stage,"I"
                    if stage in self.trigger:
                        return stage,"T"
        return None,"F"
                    
                    
    
    def execute(self,stage,deps=True,level=0,code=""):
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
        if stage in self.trigger:
            use = True
        if stage in self.config["Options.exclude"]:
            use = False
        if stage in self.config["Options.include"]:
            use = True
        if stage in self.attempt:
            return use
        if stage in self.complete:
            return use
        if not use:
            return use
        
        self.attempt += [stage]
        if code == "T":
            indicator = u"->%s"
            level = 0
        elif code == "I":
            indicator = u"+>%s"
            level = 0
        elif code == "C":
            indicator = u"=>%s"
        elif code == "D":
            indicator = u"└>%s"
        elif code == "M":
            indicator = u"*>%s"
        else:
            indicator = u"  %s"
        if deps:
            
            for dependent in self.orders:
                if dependent in self.stages[stage].deps:
                    if dependent not in self.attempt and dependent not in self.complete:
                        self.execute(dependent,level=level+1,code="D")
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
        self._depTree += [u"%-30s : %s" % (u"  " * level + indicator % stage,s.description)]
        if s.macro or self.config["Options.DryRun"]:
            self.trigger += self.stages[stage].trig
            self.complete += [stage] + s.reps
            self.done += [stage]
            return use
        elif stage in self.complete:
            return use
        
        self.log.debug("Starting \'%s\'" % s.name)
        self.log.info(u"%s" % s.description)
        if s.optional:
            s.exceptions = Exception
        
        try:
            s.run()
        except SimulatorPause:
            raise
        except (KeyboardInterrupt,SystemExit) as e:
            self.log.useConsole(True)
            self.log.critical(u"Keyboard Interrupt during %(stage)s... ending simulator." % {'stage':s.name})
            self.log.critical(u"Last completed stage: %(stage)s" % {'stage':self.complete.pop()})
            self.log.debug(u"Stages completed: %s" % ", ".join(self.complete))
            raise
        except s.exceptions as e:
            if self.config["Debug"]:
                self.log.useConsole(True)
            emsgA = u"Error %(name)s in stage %(stage)s:%(desc)s. Stage indicated that this error was not critical" % {'name': e.__class__.__name__, 'desc': s.description,'stage':s.name}
            emsgB = u"Error: %(msg)s" % {'msg':e}
            if s.optional:
                self.log.debug(emsgA)
                self.log.debug(emsgB)
            else:
                self.log.error(emsgA)
                self.log.error(emsgB)
                if self.config["Debug"]:
                    raise
        except Exception as e:
            self.log.useConsole(True)
            self.log.critical(u"Error %(name)s in stage %(stage)s:'%(desc)s'!" % { 'name' : e.__class__.__name__, 'desc' : s.description, 'stage' : s.name } )
            self.log.critical(u"Error: %(msg)s" % { 'msg' : e } )
            raise
        else:
            self.log.debug(u"Completed '%s' and %r" % (s.name,s.reps))
            self.trigger += self.stages[stage].trig
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
        self._reset()
        if code != 0 and self.commandLine:
            self.log.critical("Simulator exiting abnormally: %d" % code)
            sys.exit(code)
        elif code != 0:
            self.log.critical("Simulator closing out, exit code %d" % code)
        else:
            self.log.info(u"Simulator %s Finished" % self.name)
                
    def map(self,function,collection=[],idfun=str,exceptions=True,color="green"):
        """Map a function over a given collection."""
        if exceptions == True:
            exceptions = Exception
        
        self.errors = []
        
        if not len(collection) >= 1:
            return
        
        if not self.progressbar and color and self.log.config["logging.console.level"] <= 20:
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
                
            if len(collection) >= 1:
                ferr = float(len(self.errors)) / float(len(collection))
            else:
                ferr = 1.0
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
            Namespace = vars(self.parser.parse_args())
            for key in Namespace.keys():
                if Namespace[key] == None:
                    del Namespace[key]
            self.config["Options"].merge(Namespace)
            self.config["Options.Parsed"] = True
            self.log.log(2,"Parsed command line arguments")
        elif not self.config["Options.Parsed"]:
            Namespace = vars(self.parser.parse_args())
            for key in Namespace.keys():
                if Namespace[key] == None:
                    del Namespace[key]
            self.config["Options"].merge(Namespace)
            self.config["Options.Parsed"] = True
            self.log.log(2,"Parsed default line arguments")
        else:
            self.log.debug("Skipping argument parsing")
    
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
            raise SimulatorStateError("Cannot configure the simulator, the simulation has already started!")

        if not self.configured:
            self.configured |= self.config.load()
            self.log.debug("Updated Configuration from default file %s" % self.config["Configurations.This"])            
                
        if not self.configured:
            self.log.log(8,"No configuration provided or accessed. Using defaults.")
        

    
            
    def _postConfiguration(self):
        """Apply arguments after configuration. The arguments applied here flesh out macros, and copy data from the configuration system into the operations system."""
        # Fix configuration lists
        if not isinstance(self.config.get("Options.exclude",False),list):
            self.config["Options.exclude"] = []
        if not isinstance(self.config.get("Options.include",False),list):
            self.config["Options.include"] = []
        if not isinstance(self.config.get("Options.macro",False),list):
            self.config["Options.macro"] = []
        
        # Handler command line literal configurations.
        for item in self.config.get("Options.literalconfig",[]):    
            key,value = item.split("=")
            try:
                self.config[key] = literal_eval(value)
            except:
                self.config[key] = value
        
        # Handle post configuration updates
        for cfg in self.config.get("Options.afterConfigure",[]):
            self.config.merge(cfg)
        
        logger = logging.getLogger(self.config["Logger"])
        logger.configure(configuration=self.config)
        logger.start()
        
        for vstr in self.version:
            self.log.info(vstr)
        for fk in self.config.get("Options.afterFunction",[]):
            self.functions[fk]()

    def _setupCaching(self):
        """Sets up a cache variable for simulator caching functions."""
        if self.config.get("Cache.Disable",False) :
            return
        cfg = self.config.store
        del cfg["Options"]
        del cfg["Cache"]
        self.Caches = CacheManager(hashable = repr(cfg), destination = self.config["Dirs.Caches"], expiretime=self.config["Cache.Expire"])
        if not self.config.get("Cache.Use",True):
            self.Caches.flag('saving',False)
            self.Caches.flag('loading',False)
        if self.config.get("Cache.Clear",False):
             self.Caches.clear(self.Caches.hashhex)
        if self.config.get("Cache.ClearAll",False):
            self.Caches.clear()
        self.registerFunction(self._shutdown_caching,run='end')
        self.log.info("Cache: %s" % self.Caches)
        
    def _shutdown_caching(self):
        """docstring for finish_cache"""
        self.Caches.close()
    

    ############################################
    ### INTERNAL FUNCTION INTROSPECTION APIs ###
    ############################################    
        
    def _list_stages(self):
        """List stages"""
        text = ["Stages:"]
        for stage in self.orders:
            s = self.stages[stage]
            text += ["%(command)-20s : %(desc)s" % {'command':s.name,'desc':s.description}]
        self.log.info(u"\n".join(text))
    
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
        self.log.debug(u"Operating in DryRun mode")
        
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
    
    def _print_profile(self):
        """Print a profile with no terminal fun."""
        total = sum([ self.stages[stage].durTime for stage in self.aran])
        
        text = ["Simulation profile:"]
        text += [Stage.table_head(term=False)]
        
        for stage in self.aran:
            text += [self.stages[stage].table_row(total,term=False)]
            
        text += [Stage.table_foot(total,term=False)]
        
        print "\n".join(text)
        
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
        widgets = [ progressbar.Percentage(),' ', progressbar.ColorBar(color=color),' ', progressbar.ETA()]
        self.progressbar = progressbar.ProgressBar(widgets=widgets,maxval=length).start()
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
        except SimulatorPause:
            raise
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
    """Makes this object optional. This stage will now trap all exceptions, and will not cause the simulator to fail if it fails."""
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
    """Commands this object to be included in the ``*all`` method."""
    if callable(include):
        func = include
        func.include = True
        return func
    def decorate(func):
        func.include = include
        return func
    return decorate

def replaces(*replaces):
    """Registers replacements for this stage. This stage will satisfy any dependencies which call for ``replaces`` if this stage is run before those dependencies are requested."""
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
    """Registers dependencies for this function. Dependencies will be completed before this stage is called."""
    def decorate(func):
        func.dependencies = list(dependencies)
        return func
    return decorate

def triggers(*triggers):
    """Registers triggers for this function. Triggers are stages which should be added to the run queue if this stage is called."""
    def decorate(func):
        func.triggers = list(triggers)
        return func
    return decorate


def excepts(*exceptions):
    """Registers exceptions for this function. Exceptions listed here are deemed 'acceptable failures' for this stage, and will allow the simulator to continue operating
    without error.
    """
    def decorate(func):
        func.exceptions = tuple(exceptions)
        return func
    return decorate

def collect(collect=True):
    """Include stage explicitly in simulator automated stage collection"""
    if callable(collect):
        func = collect
        func.collect = True
        return func
    def decorate(func):
        func.collect = collect
        return func
    return decorate
    

def ignore(ignore=True):
    """Ignore stage explicitly in simulator automated stage collection"""
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
    
