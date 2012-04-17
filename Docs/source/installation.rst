Installation
============
You can install AstroObject through ``pypi`` using :ref:`pip` (**Recommended**) or from source using :ref:`setuptools`

.. _pip:
Installation via ``pip``
------------------------

.. Warning:: Installation of AstroObject will, in the future, be avaialble through pypi and pip. For now, this method will not work. Please install using ``setuptools``

To isntall this module via ``pip``, use::
	
	$ sudo pip install AstroObject
	

.. _setuptools:
Installation via ``setuptools``
-------------------------------

Obtain the source distribution. This can be retrieved from GitHub using::
	
	$ git clone https://gihub.com/alexrudy/AstroObject.git
	

Then, in the source directory, run::
	
	$ sudo python setup.py install
	
to install the software.

What to do about Bugs
---------------------

It is really helpful, if (or maybe when) you find bugs, to file issues on *GitHub*, at <http://github.com/alexrudy/AstroObject/issues>. Bug reports are useful no matter how little output you can provide, but they are easier to fix if I have as much information as possible. Please be sure to at least provide the traceback showing the issue that caused the bug.

Development of :mod:`AstroObject`
---------------------------------

I'm developing this module to support my own Astronomical Data reduction. As this is an early release (|release|), it lacks many features. My general development philosophy is as follows:

Build features that I need, when I need them. Discover bugs as I go along, and squash those bugs when I can. Maintain relatively stable APIs which are gracefully depreciated over multiple minor versions at minimum, but make no guarantee that the APIs will stay this way. Leave features partially implemented when I don't need much of their functionality.

In many ways, this constitutes "agile" development. That means that I can't/won't guarantee what works and doesn't in this library now, or later, until I decide to release a version 1.0

That being said, I'd love help. If you have development ideas or principles that I should include, or if you think that this project would be well suited in some other environment, please let me know. If you have patches and development assistance, let me know about that as well.

At this time, I'm not posting the development branch to Github. If you want to help develop, let me know, and I will start posting the development branch.


Testing the Pacakge
-------------------

:mod:`AstroObject` uses nosetests for testing, and so complies with the unittest framework but with automated discovery of tests. In general, tests were written with the ``spec`` plugin in mind, whcih outputs each test in the form of a specification. New features should be submitted with tests written to handle thier functionality. I am slowly building the test library up to full coverage, but be warned that right now, tests do not cover all features of the system. 

To run the tests using ``setuptools``, you can use::
	
	$ python setup.py nosetests
	

.. Note:: This invocation may produce a large amount of Debugging log output. This is due to the :mod:`AstroObjectLogging` module's implementation.

To run the tests purely from the command-line (without building the module)::
	
	$ nosetests
	



Source Code for Development
---------------------------

The source is available on `github`_ for development. You can download the source code using::
	
	$ git clone https://gihub.com/alexrudy/AstroObject.git
	

To develop with the source code, I recommend you use the setup.py develop task like this::
	
	sudo python setup.py develop
	

If you just wish to install the system from source, use::
	
	sudo python setup.py install
	

Pull requests are welcome on Github.

.. _github: http://github.com/alexrudy/AstroObject/