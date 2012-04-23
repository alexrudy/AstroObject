.. _SimulatorExample:

An Example Simulator
====================

Example Program

.. literalinclude:: /../../Examples/simulator.py

Example Configuration::
    
    Configurations:
      Main: Simulator.yaml
    Dirs:
      Caches: Caches
      Logs: Logs/
      Partials: Partials
    logging:
      console:
        enable: true
        level: null
        message: '...%(message)s'
      file:
        dateformat: '%Y-%m-%d-%H:%M:%S'
        enable: true
        filename: AstroObjectSim
        format: '%(asctime)s : %(levelname)-8s : %(module)-15s : %(funcName)-10s : %(message)s'
        level: null
      growl:
        enable: true
        level: null
        name: AstroSimulator
    
