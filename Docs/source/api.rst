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

Base Frame :class:`BaseFrame`
-----------------------------

.. autoclass:: 
    AstroObject.AstroObjectBase.BaseFrame
    :members:
    :special-members:

Module Structure
----------------

.. inheritance-diagram::
	AstroObject.AstroImage.ImageFrame
	AstroObject.AstroImage.ImageObject
	AstroObject.AstroSpectra.SpectraFrame
	AstroObject.AstroSpectra.SpectraObject
	AstroObject.AstroFITS.HDUFrame
	AstroObject.AstroFITS.HDUObject
    AstroObject.AnalyticSpectra.AnalyticSpectrum
    AstroObject.AnalyticSpectra.CompositeSpectra
    AstroObject.AnalyticSpectra.InterpolatedSpectrum
    AstroObject.AnalyticSpectra.Resolver
    AstroObject.AnalyticSpectra.UnitarySpectrum
    :parts: 1
