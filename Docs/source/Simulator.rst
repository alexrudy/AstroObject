.. module:: AstroObject.AstroSimulator

Simulator and Complex Task Management :mod:`AstroSimulator`
***********************************************************

The Simulator is designed to provide a high level, command-line useful interface to large computational tasks. As the name suggests, Simulators often do a lot of programming work, and do so across many distinct "stages", whcih can be configured in any way the user desires. All of the abilities in this program are simply object abstraction techniques to provide a complex program with a command line interface and better control and reporting on the activiites carreid out to successfully complete the program. It allows for the configuration of simple test cases and "macros" from within the program, eliminating the need to provide small wrapper scripts and test handlers.

An example (simple) program using the simulator::
	
	import numpy as np
	
	from AstroObject.AstroSimulator import *
	from AstroObject.AstroCache import *
    
	class SimpleModel(object):
	    def __init__(self,SIM):
	        super(SimpleStage, self).__init__()
	        self.name = "SimpleStage"
	        self.sim = SIM
    
	    def run(self):
	        print "Hello from %s Object" % self.name
	        img = self.sim.Caches.get("Random Image")
	        print img[0,0]
        
	    def other(self):
	        """Other Stage Function"""
	        print "Hello from %s Stage" % "other"
	        img = self.sim.Caches.get("Random NPY")
	        print img[1,1]
    
	    def last(self):
	        """Last Stage Function"""
	        print "Last Stage"
	        img = self.sim.Caches.get("Random Image")
	        print img[0,0]
    
	    def save(self,stream,data):
	        """Saves some cache data"""
	        np.save(stream,data)
        
    
	    def cache(self):
	        """Cache this image"""
	        img = np.random.normal(10,2,(1000,1000))
	        return img
        
	    def load(self,stream):
	        """Load the image"""
	        try:
	            img = np.load(stream)
	        except IOError:
	            raise CacheIOError("Couldn't find Cache File")
	        return img
    
	SIM = Simulator(commandLine=True)    
	stage = SimpleModel(SIM)
	
	SIM.registerStage(stage.run,name="examp",description="Example Stage")
	SIM.registerStage(stage.other,name="other",description="Other Stage")
	SIM.registerStage(stage.last,name="last",description="Last Stage")
	SIM.registerMacro("ex","examp",help="example Macro")
	SIM.Caches.register("Random Image",stage.cache,stage.load,stage.save)
	SIM.Caches.registerNPY("Random NPY",stage.cache,directory="Caches/",filename="Random.npy")
	SIM.Caches.clear()
	SIM.run()
	

.. autoclass::
    AstroObject.AstroSimulator.Simulator
    :members:
