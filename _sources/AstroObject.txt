:mod:`AstroObjectBase`
======================

The Base API was introduced in version 0.2.1 to facilitate the creation and use of basic template classes.

.. module:: 
    AstroObjectBase

AstroObjectBase provides template objects for the Object-Oriented Modules :mod:`AstroImage` and :mod:`AstroSpectra`. Template classes implement all of the required methods. However, calling a method defined by a template class will usually raise an :exc:`AbstractError` indicating that an Abstract method was called.

.. autoclass:: 
    AstroObjectBase.FITSFrame
    :members:
    :special-members:
    
.. autoclass::
    AstroObjectBase.FITSObject
    :members:
    :special-members:

    