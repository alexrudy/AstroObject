.. module:: AstroObject.AstroSimulator

Simulator :mod:`AstroSimulator`
*******************************

The Simulator is designed to provide a high level, command-line useful interface to large computational tasks. As the name suggests, Simulators often do a lot of programming work, and do so across many distinct "stages", whcih can be configured in any way the user desires. All of the abilities in this program are simply object abstraction techniques to provide a complex program with a command line interface and better control and reporting on the activities carreid out to successfully complete the program. It allows for the configuration of simple test cases and "macros" from within the program, eliminating the need to provide small wrapper scripts and test handlers.

An example (simple) program using the simulator can be found in :ref:`SimulatorExample`

.. _Simulator_CLI:

:program:`Simulator` Command Line Interface
-------------------------------------------

The master simulator program is a command-line interface to the :meth:`AstroObject.AstroSimulator.Simulator.run` method. Below are the major command line components.

.. program:: Simulator

.. option:: {stages}
	
	The stages option specifies individual stages for the program to run. You must specify at least one stage to run in the simulator. By default, two basic stages are provided, ``*all`` and ``*none``. The default simulation is performed by ``*all``. To test the simulator without running any stages (for example, to test :meth:`AstroObject.AstroSimulator.Simulator.registerFunction` functionality), use the ``*none`` stage to opertate without using any stages.
	
	Stages are called with either a ``*``, ``+`` or ``-`` character at the beginning. Their resepctive actions are shown below. All commands must include at least one macro. If you don't want any particular macro, use the ``*none`` macro.
	
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
	
.. option:: --dry-run
	
	Traverse all of the stages to be run, printing them as the program goes, but do not run any stages.
	
.. option:: --stages
	
	Print all stages registered in the simulator. Any stage listed in the output of this function can be run.
	
.. option:: --dump
	
	Dump the configuration to a file. Filenames are the configuration file name with ``-dump.yaml`` appended.

.. _Configuration:

:program:`Simulator` Configuration Files
----------------------------------------

:program:`Simulator` configuration files are YAML files which contain a dictionary structure. All values in the YAML files are basic yaml, and contain no python-specific directives. To find out what the default or current configuration is, use the :option:`--dump` command. The file produced from this will contain a YAML structure for the configuration in use when the system started up. The various directives in the configuration file are described below.

- ``Configurations``: contains a list of potential configuration files.

    - ``Main``: The name of the primary configuration file. This default is produced by the program. Overriding it in the configuration file has essentially no effect.

- ``Dirs``: Directories that this simulator will use for output.

    - ``Caches``: Location of cache files.
        .. Note:: This function has almost no effect, but can be used internally by the simulator. See :ref:`SimulatorExample`

    - ``Logs``: Location of log files
    
    - ``Partials``: Location of partial output, including a dump of the configuration.
    
- ``Logging``: Configuration of the :mod:`AstroObject.AstroObjectLogging` module

A simple configuration file can be found in the :ref:`SimulatorExample`.

.. _Simulator_API:

API Methods
-----------
    
The following methods handle the external-API for the simulator.
    
.. autoclass::
    AstroObject.AstroSimulator.Simulator
    
	.. automethod:: registerStage
	
	.. automethod:: registerConfigOpts
	
	.. automethod:: registerFunction
	
	.. automethod:: run
	
	.. automethod:: startup
	
	.. automethod:: do
	
	.. automethod:: exit
    
Private Methods and Classes
---------------------------
    
These methods are used to implment the public-facing API. They are documented here to explain their use in development.

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