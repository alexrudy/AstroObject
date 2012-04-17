.. _AstroObjectAPI:

AstroObject API
===============

The API is the foundation of the :mod:`AstroObject` module. When creating new types of data, you will want to create frames for that type of data. The functions shown below are the functions which must be present in every data frame type, in order to maintain compatibility with enclosing Objects. If your class conforms to this API, then it can easily be used as data for :class:`AstroObjectBase.BaseObject`. 


To see how easy this will make objects, examine the following code for a custom Object class which accepts :class:`FooFrame`. To create the custom :class:`AstroObjectBase.BaseObject` which accepts your new data type :class:`FooFrame`, simply use::
    
    class FooObject(AstroObjectBase.BaseObject):
        """A container for tracking FooFrames"""
        def __init__(self, dataClasses=[FooFrame]):
            super(ImageObject, self).__init__(dataClasses = dataClasses)
            
        
    
This object will then have all of the functions provided by :class:`AstroObjectBase.BaseObject`, but will only accept and handle data of type :class:`FooFrame`. :class:`FooFrame` should then implement all of the functions described in the API below.

To use this API, it is recommended that you sub-class :class:`AstroObjectBase.BaseFrame`. This template class is an abstract base which will ensure that you implement all of the required methods.

The API also provides a number of Mixin classes for special cases. These mixins allow you to use incomplete, or standard implementations in certain cases. Mixins are useful when your data type cannot possibly conform to the full API provided by :class:`AstroObjectBase.BaseFrame`. Examples of this are classes which cannot produce HDUs or FITS files, or classes which do not actually contain raw data. See :ref:`Mixins` for more information.

Base Frame :class:`BaseFrame`
-----------------------------

The :class:`BaseFrame` class provides abstract methods for all of the required frame methods. If you subclass from :class:`BaseFrame`, you will ensure that your subclass is interoperable with all of the frame and object features of this module.

.. autoclass:: 
    AstroObject.AstroObjectBase.BaseFrame
    :members:
    :special-members:

.. _Mixins:

Mixins in :mod:`AstroObjectBase`
--------------------------------

.. currentmodule:: AstroObject.AstroObjectBase

Mixins allow certain classes to operate without all of the features required by :class:`BaseFrame`. Each class below implements certain methods and skips others. 

A summary table is below. The table has classes provided from right to left. Note that :class:`AnalyticFrame` inherits from :class:`NoHDUMixin` and :class:`NoDataMixin`. This means that objects with type :class:`AnalyticFrame` are assumed by the system to be a type of frame, but they do not implement any of the major frame methods.

=============================== ==================== ========================= ====================== ===================== ========================================== ===============================
Method                           :class:`BaseFrame`   :class:`HDUHeaderMixin`   :class:`NoDataMixin`   :class:`NoHDUMixin`   :class:`AnalyticFrame`                     :class:`AbstractSpectraMixin`
=============================== ==================== ========================= ====================== ===================== ========================================== ===============================
inherits                                                                                                                     :class:`NoHDUMixin` :class:`NoDataMixin`                     
:meth:`BaseFrame.__call__`       Abstract                                       Skipped                                      Skipped
:meth:`BaseFrame.__setheader__`  Abstract              Implemented                                     Skipped               *Skipped*
:meth:`BaseFrame.__getheader__`  Abstract              Implemented                                     Skipped               *Skipped*
:meth:`BaseFrame.__hdu__`        Abstract                                                              Skipped               *Skipped*
:meth:`BaseFrame.__show__`       Abstract                                       Skipped                                      *Skipped*                                     Implemented
:meth:`BaseFrame.__save__`       Abstract                                                                                    Skipped
:meth:`BaseFrame.__read__`       Abstract                                                              Skipped               *Skipped*
=============================== ==================== ========================= ====================== ===================== ========================================== ===============================

.. autoclass::
	AstroObject.AstroObjectBase.HDUHeaderMixin
	
.. autoclass::
	AstroObject.AstroObjectBase.NoDataMixin
	
.. autoclass::
	AstroObject.AstroObjectBase.NoHDUMixin
	
.. autoclass::
	AstroObject.AstroObjectBase.AnalyticFrame
	
.. autoclass::
	AstroObject.AstroSpectra.SpectraMixin

Base Object :class:`BaseObject`
-----------------------------------------------

The base object definition provides the normal object accessor methods. It should be subclassed as shown in :ref:`AstroObjectAPI`

.. autoclass::
	AstroObject.AstroObjectBase.BaseObject
	:members:

Module Structure
----------------

.. inheritance-diagram::
	AstroObject.AstroObjectBase.FITSFrame
	AstroObject.AstroObjectBase.FITSObject
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
	AstroObject.AnalyticSpectra.FlatSpectrum
	AstroObject.AnalyticSpectra.GaussianSpectrum
	AstroObject.AnalyticSpectra.BlackBodySpectrum
    :parts: 1
