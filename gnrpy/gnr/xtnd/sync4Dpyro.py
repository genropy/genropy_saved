import os

import Pyro.core
import Pyro.naming

from gnr.xtnd.sync4Dapp import GnrAppSync4D

class Sync4DCommander(Pyro.core.ObjBase):
    def __init__(self, daemon, instancefolder):
        Pyro.core.ObjBase.__init__(self)
        
        self.app = GnrAppSync4D(instancefolder)
        self.daemon = daemon
        
        self.instancefolder = instancefolder
        self.instancename = os.path.basename(instancefolder)
        

    def loopCondition(self):
        print 'loop'
        self.app.do()
        return True
    
    def run(self):
        
        self.app.beforeLoop()
        
        self.ns = Pyro.naming.NameServerLocator().getNS()
        self.daemon.useNameServer(self.ns)
        uri = self.daemon.connect(self,"sync4d_%s" % self.instancename)
        
        print "The daemon runs on port:", self.daemon.port
        print "The object's uri is:",uri
        
        self.daemon.requestLoop(timeout=self.app.sync4d_timing, condition=self.loopCondition)
        
    def stop(self):
        self.daemon.shutdown(True)
    