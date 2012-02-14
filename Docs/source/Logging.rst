.. module:: AstroObject.AstroObjectLogging

Easy Logging :mod:`AstroObjectLogging`
**************************************

This module provides basic access to logging functions. It elimiates much of the variablity in logging, replacing it with the simple logging configuration options that AstroObject is constantly using. It is, however, built on the normal logging module, and so shouldn't break any other logging schemes.

Other than a simpler set of possible configuration options, this object has the advantage that it allows for dynamic configurations which vary from run to run. As is common in complex programs, a lot happens before reading a configuration file. However, without the configuration file, the system can't start logging. This logger holds all the messages it recieves pre-configuration for use once the logger starts, preserving these messages for later debugging.

To use the logging::
	
	LOG = logging.getLogger(__name__)
	LOG.info("Buffered Message Saved for later output")
	LOG.configure(configFile="some.yaml")
	LOG.info("Buffered Message, which will never get to the console")
	LOG.start()
	LOG.info("Normal Message")
	LOG.useConsole(False)
	LOG.info("Not on the console")
	LOG.useConsole(True)
	LOG.info("Back to the console!")
	

.. autoclass::
    AstroObject.AstroObjectLogging.LogManager
    :members:

