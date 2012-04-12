Simulator :mod:`AstroSimulator`
*******************************

.. automodule:: AstroObject.AstroSimulator

.. currentmodule:: AstroObject.AstroSimulator

.. _Simulator_API:

API Methods
-----------
    
The following methods handle the external-API for the simulator.
    
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
    
    .. automethod:: map_over_collection
    
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