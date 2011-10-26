:mod:`AstroObjectBase`
======================

The Base API was introduced in version 0.2.1 to facilitate the creation and use of basic template classes.

.. module:: 
    AstroObjectBase

AstroObjectBase provides template objects for the Object-Oriented Modules :mod:`AstroImage` and :mod:`AstroSpectra`. Template classes implement all of the required methods. However, calling a method defined by a template class will usually raise an :exc:`AbstractError` indicating that an Abstract method was called.

.. Note::
    You should still use Template Classes even though they really only raise abstract errors. This helps you to ensure that you have implemented all of the required methods. As well, if new methods are added to the APIs in the future, using the Abstract class will likely cause your program to fail quietly on these new API calls, allowing you to mix old and new code with out too much concern for what has changed.

.. autoclass:: 
    AstroObjectBase.FITSFrame
    :members:
    :special-members:
    
.. autoclass::
    AstroObjectBase.FITSObject
    :members:

    