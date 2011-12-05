.. _AstroObjectAPI:

AstroObject API
===============

The API is the foundation of the module. When creating new types of data, you will want to create frames for that type of data. The functions shown below are the functions which must be present in every data frame type, in order to maintain compatibility with enclosing Objects. If your class conforms to this API, then it can easily be used with the :class:`AstroObjectBase.FITSObject`. To create a custom :class:`AstroObjectBase.FITSObject` which accepts your new data type :class:`FooFrame`, simply use::
    
    class FooObject(AstroObjectBase.FITSObject):
        """A container for tracking FooFrames"""
        def __init__(self, array=None):
            super(ImageObject, self).__init__()
            self.dataClasses += [FooFrame]
            self.dataClasses.remove(AstroObjectBase.FITSFrame)
            if array != None:
                self.save(array)        # Save the initializing data
            
        
    
This object will then have all of the functions provided by :class:`AstroObjectBase.FITSObject`, but will only accept and handle data of type :class:`FooFrame`. :class:`FooFrame` should then implement all of the functions described in the API below.

To use this API, it is recommended that you sub-class :class:`AstroObjectBase.FITSFrame`. This template class will implement all of the required functions, and will raise abstract errors on functions that must be overwritten by your subclass.

.. py:class:: AstroFrameAPI()
    
    This is the API for frame objects, that is, objects which represnet a single state of data. See :class:`AstroObjectBase.FITSFrame`. This API is generally not called by the end user, but rather is called by the parent *Object* function. For an example of a parent object, see :class:`AstroObjectBase.FITSObject`
    
    .. py:method:: __call__()
    
        This method will return data for the object. It should normally return a :class:`numpy.ndarray`.
    
    .. py:method:: __hdu__(primary=False)
    
        This method returns an HDU which represents the object. The HDU should respect the object's :attr:`header` attribute, and use that dictionary to populate the headers of the HDU. If the ``primary`` keyword is set, the function should return a :class:`pyFITS.PrimaryHDU` object. If the frame cannot reasonable generate a :class:`pyFITS.PrimaryHDU`, then it should raise an :exc:`AbstractError` in that case.
    
    .. py:method:: __show__()
    
        This method should create a simple view of the provided frame. Often this is done using :mod:`Matplotlib.pyplot` to create a simple plot. The plot should have the minimum amount of work done to make a passable plot view, but still be basic enough that the end user can customize the plot object after calling :meth:`__show__`.
    
    .. py:method:: __str__()
    
        This method returns a string representation of the provided object. The base API (which you should use as the superclass of any new Frame classes that you develop) provides a basic :meth:`AstroObjectBase.FITSFrame.__str__` method, which just inserts the label to identify a particular frame. In other cases, you may wish to overwrite this method to also include other data, such as the target name.
    
    .. py:method:: __valid__()
    
        This method is an internal method for checking data validity. It is automatically called once at the end of the superclass initialization if you use :class:`AstroObjectBase.FITSFrame` as your parent class. If you do use this method as your parent class, you should be sure to perform your own object's initialization before you call your super class initializer. Failing to do this will cause :meth:`__valid__` to run before any data has been established in the object.
    
    .. py:classmethod:: __save__(data,label)
        
        This method should retun an instance of the parent class if the given data can be turned into an object of that class. If the data cannot be correctly cast, this method should throw an :exc:`AbstractError`.
        
        .. Note:: Because the :meth:`__valid__` is called when an object is initialized, it is possible to check some aspects of the provided data in this initialization function. However, this would raise an :exc:`AssertionError` not an :exc:`AbstractError`. To avoid this problem, it is suggested that you wrap your initialization in a try...except block like::
                
                try:
                    Object = cls(HDU.data,label)
                except AssertionError as AE:
                    msg = "%s data did not validate: %s" % (cls.__name__,AE)
                    raise AbstractError(msg)
                
            This block simply changes the error type emitted from the __valid__ function. This trick is not a substituion for data validation before initializing the class. Just instantiating a class like this often results in bizzare errors (like :exc:`AttributeError`) which are diffult to track and diagnose without the code in :meth:`__save__`. See :meth:`AstroImage.__save__` for an example ``__read__`` function which uses this trick, but also includes some basic data validation.
        
    .. py:classmethod:: __read__(HDU,label)
    
        This method should return an instance of the parent class if the given ``HDU`` can be turned into an object of that class. If this is not possible (i.e. a Table HDU is provided to an Image Frame), this method should raise an :exc:`AbstractError` with a message that describes the resaon the data could not be cast into this type of frame.
        
        .. Note:: Because the :meth:`__valid__` is called when an object is initialized, it is possible to check some aspects of the provided data in this initialization function. However, this would raise an :exc:`AssertionError` not an :exc:`AbstractError`. To avoid this problem, it is suggested that you wrap your initialization in a try...except block like::
                
                try:
                    Object = cls(HDU.data,label)
                except AssertionError as AE:
                    msg = "%s data did not validate: %s" % (cls.__name__,AE)
                    raise AbstractError(msg)
                
            This block simply changes the error type emitted from the __valid__ function. This trick is not a substituion for data validation before initializing the class. Just instantiating a class like this often results in bizzare errors (like :exc:`AttributeError`) which are diffult to track and diagnose without the code in :meth:`__read__`. See :meth:`AstroImage.__read__` for an example ``__read__`` function which uses this trick, but also includes some basic data validation.
            
        .. Note:: It is acceptable to call the class :meth:`__save__` function here. However, the :meth:`__read__` function should also correctly handle header data.