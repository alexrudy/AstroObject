.. module:: AstroObject.AstroFITS

HDU Objects and Storage :mod:`AstroFITS`
****************************************


Objects for manipulating and managing HDUs directly.

.. warning:: There are some problems in this feature at the moment. Right now, HDU generation and reading does not happen correctly, as only data and headers are extracted and included. This will be corrected shortly.


.. autoclass::
    AstroObject.AstroFITS.HDUFrame
    :members:
    :special-members:


.. autoclass::
    AstroObject.AstroFITS.HDUObject
    :members:
    :inherited-members:
