.. module:: 
    AstroObject.AstroObjectBase

API for Objects: :class:`FITSObject` 
************************************



The Base API was introduced in version 0.2.1 to facilitate the creation and use of basic template classes.

The FITSObject container is useful for handling many data frames. It can be sub-classed easily to make a customized data container which can handle new types of data frames. To create a custom data container, ensure you have a class which conforms to the :ref:`AstroObjectAPI` (called a ``frame``), then simply subclass :class:`AstroObjectBase.FITSObject` and provide the ``frame`` to :attr:`FITSObject.dataclasses`. For example, if :class:`FooFrame` conforms to the :ref:`AstroObjectAPI`, then you could use::
    
    class FooObject(AstroObjectBase.FITSObject):
        """A container for tracking FooFrames"""
        def __init__(self, array=None):
            super(ImageObject, self).__init__()
            self.dataClasses += [FooFrame]
            self.dataClasses.remove(AstroObjectBase.FITSFrame)
            if array != None:
                self.save(array)        # Save the initializing data
            
        
    
This object will then have all of the functions provided by :class:`AstroObjectBase.FITSObject`, but will only accept and handle data of type :class:`FooFrame`. :class:`FooFrame` should then implement all of the functions described in the :ref:`AstroObjectAPI`.

.. autoclass::
    AstroObject.AstroObjectBase.FITSObject
    :members:
    



API for Frames :class:`FITSFrame`
*********************************

AstroObjectBase provides template objects for the Object-Oriented Modules :mod:`AstroImage` and :mod:`AstroSpectra`. Template classes implement all of the required methods. However, calling a method defined by a template class will usually raise an :exc:`AbstractError` indicating that an Abstract method was called.

.. Note::
    You should still use Template Classes even though they really only raise abstract errors. This helps you to ensure that you have implemented all of the required methods. As well, if new methods are added to the APIs in the future, using the Abstract class will likely cause your program to fail quietly on these new API calls, allowing you to mix old and new code with out too much concern for what has changed.

.. autoclass:: 
    AstroObject.AstroObjectBase.FITSFrame
    :members:
    :special-members:
    


    